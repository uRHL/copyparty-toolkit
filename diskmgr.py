from pathlib import Path
import subprocess
import argparse
import stat
import os
import re

__all__ = [
    'RW', 'RO',
    'mount',
    'umount',
    'list_mnt'
]

RW = "ro=0"
RO = "ro=1"

COLORS = {
    "[+]": "\033[32m",   # green
    "[-]": "\033[33m",   # yellow
    "[*]": "\033[94m",   # light blue
    "[!]": "\033[31m",   # red
}
RESET = "\033[0m"


def colorize(msg: str) -> str:
    for tag, color in COLORS.items():
        if msg.startswith(tag):
            return f"{color}{tag}{RESET}{msg[len(tag):]}"
    return msg


def log(msg: str):
    print(colorize(msg))


def cmd(cmd: str, **kwargs):
    """Run a shell command and return the CompletedProcess."""
    return subprocess.run(cmd, shell=True, **kwargs)


def _is_block_device(path: Path) -> bool:
    try:
        return stat.S_ISBLK(path.stat().st_mode)
    except FileNotFoundError:
        return False


def _resolve_path(raw: Path) -> Path | None:
    """Resolve a user-provided path to an absolute directory or block device."""
    if not raw.is_absolute():
        dev_candidate = Path("/dev") / raw
        if dev_candidate.exists():
            return dev_candidate

        resolved = Path(os.getcwd()) / raw
        try:
            resolved.mkdir()
            log(f"[+] New directory created '{resolved}'")
        except FileExistsError:
            pass
        return resolved

    if not raw.exists():
        log(f"[-] Path not found '{raw}'. Skipping mount.")
        return None

    return raw


def _read_lxc_conf(conf_path: Path) -> list[str]:
    if not conf_path.exists():
        log(f"[-] LXC config not found at '{conf_path}'")
        return []

    try:
        with conf_path.open("r") as file:
            return [line.rstrip("\n") for line in file.readlines()]
    except PermissionError:
        log(f"[!] Permission denied reading '{conf_path}'. Are you superuser?")
        return []


def _write_lxc_conf(conf_path: Path, lines: list[str]) -> None:
    try:
        conf_path.write_text("\n".join(lines) + ("\n" if lines else ""))
    except PermissionError:
        log(f"[!] Permission denied writing '{conf_path}'. Are you superuser?")


def _lines_to_entries(lines: list[str]) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        entries[key.strip()] = value.strip()
    return entries


def _list_configured_lxc_ids(conf_dir: Path) -> list[int]:
    if not conf_dir.exists():
        log(f"[-] LXC config directory not found at '{conf_dir}'")
        return []
    ids: list[int] = []
    for path in conf_dir.glob("*.conf"):
        if path.stem.isdigit():
            ids.append(int(path.stem))
    return sorted(ids)


def umount(paths: list[str | Path], lxc_id: int):
    check_pve_install() # Only run in PVE installations, either as CLI or python module

    for raw_path in [Path(p) for p in paths]:
        name = Path(raw_path).name

        conf_path = Path(f"/etc/pve/lxc/{lxc_id}.conf")
        lines = _read_lxc_conf(conf_path)
        if lines:
            new_lines = []
            removed = False
            for line in lines:
                if re.match(r"^mp\d+\s*:", line) and f"mp=/shr/{name}" in line:
                    removed = True
                    continue
                new_lines.append(line)

            if removed:
                _write_lxc_conf(conf_path, new_lines)
                log(f"[+] Removed mount from config for '/shr/{name}'")
            else:
                log(f"[!] No mount found for '/shr/{name}' in config")

        cmd(f"umount /mnt/{name}")
    # Once all directories are removed, restart container
    restart_container(lxc_id)


def mount(paths: list[str | Path], lxc_id: int, permanent: bool = False, ro: bool = True):
    """Mounts paths in a given container.
    :param paths: host directories or block devices to be mounted.
    :param lxc_id: Container ID.
    :param permanent: If True, directories will be mounted automatically on boot (/etc/fstab).
    :param ro: If True, mounted directories will be Read-Only (default).
    """
    check_pve_install() # Only run in PVE installations, either as CLI or python module

    def _mount_filter(pair):
        k, _ = pair
        return re.match(r"^mp\d+", k) is not None

    log("[*] Preparing host mounting points")
    for raw_path in [Path(p) for p in paths]:
        source_path = _resolve_path(raw_path)
        if source_path is None:
            continue

        is_dir = source_path.is_dir()
        is_block = _is_block_device(source_path)
        if not (is_dir or is_block):
            log(f"[-] Path must be a directory or block device '{source_path}'. Skipping mount.")
            continue

        if source_path.is_file() and not is_block:
            log("[-] Single files cannot be mounted. Use directories or block devices instead.")
            continue

        # 1. Prepare mount points on the Proxmox host
        try:
            Path(f"/mnt/{source_path.name}").mkdir(parents=True, exist_ok=True)
        except PermissionError:
            log(f"[!] Permission denied creating '/mnt/{source_path.name}'. Are you superuser?")
            continue
        mnt_cmd = f"mount {source_path} /mnt/{source_path.name}"
        cmd(mnt_cmd)
        if permanent:
            try:
                with open("/etc/fstab", "r+") as file:
                    content = [line.rstrip("\n") for line in file.readlines()]
                    if mnt_cmd in content:
                        log(f"[-] Already permanently mounted '{source_path.name}'")
                    else:
                        content.append(mnt_cmd)
                        file.seek(0)
                        file.write("\n".join(content) + "\n")
                        file.truncate()
                        log(f"[+] Directory '{source_path.name}' mounted permanently")
            except PermissionError:
                log(f"[!] Permission denied updating /etc/fstab. Are you superuser?")

        # 2. Create mountpoints inside the container
        try:
            Path(f"/var/lib/lxc/{lxc_id}/rootfs/shr/{source_path.name}").mkdir(parents=True, exist_ok=True)
        except PermissionError:
            log(f"[!] Permission denied creating container path for '{source_path.name}'. Are you superuser?")
            continue

        # 3. Add bind-mounts to the container config
        conf_path = Path(f"/etc/pve/lxc/{lxc_id}.conf")
        lines = _read_lxc_conf(conf_path)
        if not lines:
            continue

        entries = _lines_to_entries(lines)
        current_mounts = dict(filter(_mount_filter, entries.items()))

        if any(f"mp=/shr/{source_path.name}" in value for value in current_mounts.values()):
            log(f"[!] A directory is already mounted at '/shr/{source_path.name}'")
            continue

        existing_indices = sorted(int(key[2:]) for key in current_mounts) if current_mounts else []
        next_index = existing_indices[-1] + 1 if existing_indices else 0
        mp_key = f"mp{next_index}"
        mp_value = f"/mnt/{source_path.name},mp=/shr/{source_path.name},{RO if ro else RW}"

        lines.append(f"{mp_key}: {mp_value}")
        _write_lxc_conf(conf_path, lines)

    # Once all directories are mounted, restart container
    restart_container(lxc_id)


def restart_container(lxc_id):
    """Restart a container by ID with logging."""
    check_pve_install() # Only run in PVE installations, either as CLI or python module

    log(f"[*] Stopping container {lxc_id}")
    stop_result = cmd(f"pct stop {lxc_id}")
    if stop_result.returncode != 0:
        log(f"[!] Failed to stop container {lxc_id} (code {stop_result.returncode})")
        return
    log(f"[+] Container stopped {lxc_id}")

    log(f"[*] Starting container {lxc_id}")
    start_result = cmd(f"pct start {lxc_id}")
    if start_result.returncode != 0:
        log(f"[!] Failed to start container {lxc_id} (code {start_result.returncode})")
        return
    log(f"[+] Container started {lxc_id}")


def check_pve_install(quiet: bool = True) -> bool:
    """Best-effort check to guess if host is running Proxmox VE."""
    expected_paths = [
        Path("/etc/pve"),
        Path("/usr/sbin/pct"),
        Path("/etc/apt/sources.list.d/pve-enterprise.list"),
    ]
    is_pve = all(p.exists() for p in expected_paths)
    if is_pve:
        if not quiet:
            log("[+] ProxMox VE install [OK]")
        return True
    log("[!] Not a ProxMox VE system. Exiting...")
    raise SystemExit(1)

def list_mnt(lxc_id: list[int] | None = None):
    """List mounted volumes in the specified containers.
    If lxc_id is None or empty, list mounts for all containers with configs present.
    """
    check_pve_install() # Only run in PVE installations, either as CLI or python module

    conf_dir = Path("/etc/pve/lxc")
    if lxc_id is None or lxc_id == []:
        ids = _list_configured_lxc_ids(conf_dir)
    elif isinstance(lxc_id, int):
        ids = [lxc_id]
    else:
        ids = lxc_id
    mounts: dict[int, list[tuple[str, str]]] = {}

    for cid in ids:
        conf_path = conf_dir / f"{cid}.conf"
        lines = _read_lxc_conf(conf_path)
        if not lines:
            continue

        entries = _lines_to_entries(lines)
        container_mounts = [(k, v) for k, v in entries.items() if re.match(r"^mp\d+", k)]
        if not container_mounts:
            log(f"[{cid}] No mounts found")
            continue

        mounts[cid] = container_mounts
        log(f"[{cid}]")
        for key, value in container_mounts:
            log(f"  {key}: {value}")

    return mounts

def main():
    parser = argparse.ArgumentParser(prog="diskmgr", description="Mount or unmount host paths into LXC containers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    mount_parser = subparsers.add_parser("mount", help="Mount host paths into the container.")
    mount_parser.add_argument("paths", nargs="+", help="Paths to mount (directories or block devices).")
    mount_parser.add_argument("lxc_id", type=int, help="Target LXC container ID.")
    mount_parser.add_argument("-p", "--permanent", action="store_true", help="Add to /etc/fstab for auto-mount on boot.")
    mount_parser.add_argument("--rw", action="store_true", help="Mount read-write instead of read-only.")

    umount_parser = subparsers.add_parser("umount", help="Unmount host paths from the container.")
    umount_parser.add_argument("paths", nargs="+", help="Paths to unmount.")
    umount_parser.add_argument("lxc_id", type=int, help="Target LXC container ID.")

    list_parser = subparsers.add_parser("list", help="List mounts configured on container(s).")
    list_parser.add_argument("lxc_id", nargs="*", type=int, help="Optional LXC container IDs. If omitted, list all.")

    args = parser.parse_args()

    if args.command == "mount":
        mount(paths=args.paths, lxc_id=args.lxc_id, permanent=args.permanent, ro=not args.rw)
    elif args.command == "umount":
        umount(paths=args.paths, lxc_id=args.lxc_id)
    elif args.command == "list":
        list_mnt(lxc_id=args.lxc_id if args.lxc_id else None)


if __name__ == "__main__":
    main()

