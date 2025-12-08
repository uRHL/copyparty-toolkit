from argon2.low_level import Type as ArgonType
try:
    from packaging.version import Version  # type: ignore
    _Version = Version
except ImportError:  # fallback for minimal environments
    from distutils.version import LooseVersion as _Version  # type: ignore
from argon2.low_level import hash_secret
from pathlib import Path

import urllib.request
import argparse
import random
import shutil
import re
import os


ROOT_DIR = Path(__file__).parent
TEMPLATE_DIR = ROOT_DIR / "templates"

# https://github.com/9001/copyparty/blob/c5c5f9b4b828b984cf7109d12f86150a334eb566/copyparty/pwhash.py#L110
def _gen_argon2(salt: str, plain: str) -> str:
        if salt is None:
            raise ValueError("salt cannot be None")  
        time_cost = 3
        mem_cost = 256
        parallelism = 4
        version = 19

        bplain = plain.encode("utf-8")

        bret = hash_secret(
            secret=bplain,
            salt=salt.encode('utf-8'),
            time_cost=time_cost,
            memory_cost=mem_cost * 1024,
            parallelism=parallelism,
            hash_len=24,
            type=ArgonType.ID,
            version=version,
        )
        ret = bret.split(b"$")[-1].decode("utf-8")
        return "+" + ret.replace("/", "_").replace("+", "-")

def _strip_comment(line: str) -> str:
    line = line.rstrip()
    if not line or line.lstrip().startswith('#'):
        return ''
    cut = line.find('  #')
    if cut != -1:
        line = line[:cut]
    return line.rstrip()

def _parse_atom(token: str):
    if re.fullmatch(r'-?\d+', token):
        return int(token)
    return token

def _parse_value(value: str):
    if not value:
        return True
    if re.search(r',\s+', value):
        parts = [p.strip() for p in re.split(r',\s+', value) if p.strip()]
        parsed = [_parse_atom(p) for p in parts]
        if not parsed:
            return True
        if len(parsed) == 1:
            return parsed[0]
        return parsed
    return _parse_atom(value.strip())

def _parse_flag_line(text: str, dest: dict) -> None:
    chunks = re.split(r',\s+', text) if re.search(r',\s+', text) else [text]
    for chunk in chunks:
        item = chunk.strip()
        if not item:
            continue
        if ':' in item:
            k, v = item.split(':', 1)
            dest[k.strip()] = _parse_value(v.strip())
        else:
            dest[item] = True

def gen_passwd(length: int = 12) -> str:
    charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choices(charset, k=length))

def gen_password(length: int = 12) -> str:
    return gen_passwd(length)

def sanitize(value) -> str:
    return re.sub(r'[^a-z0-9_-]', '-', value)

COLOR_MAP = {
    "[+]": "\033[32m",
    "[-]": "\033[33m",
    "[!]": "\033[31m",
    "[*]": "\033[96m",
}

def _log(message: str):
    text = str(message)
    prefix = text[:3]
    color = COLOR_MAP.get(prefix)
    if color:
        print(f"{color}{text}\033[0m")
    else:
        print(text)

def _prompt(message: str) -> str:
    text = str(message)
    prefix = text[:3]
    color = COLOR_MAP.get(prefix)
    if color:
        return f"{color}{text}\033[0m"
    return text

class CopypartyConf:
    def __init__(self, global_conf=None, accounts=None, volumes=None, extra=None, groups=None, path: str = None):
        self._global = global_conf or {}
        self._accounts = accounts or {}
        self._volumes = volumes or {}
        self._extra = extra or {}
        self._groups = groups or {}
        self._path = path

    @property
    def salt(self) -> str | None:
        return self._global.get('ah-salt', None)
    
    @property
    def vault_dir(self) -> str | None:
        return self._global.get('chdir', None)
    
    @property
    def global_conf(self):
        return self._global

    @property
    def accounts(self):
        return self._accounts

    @property
    def volumes(self):
        return self._volumes

    @property
    def extra(self):
        return self._extra

    @property
    def path(self):
        return self._path
    
    @property
    def get_groups(self):
        return self._groups

    @staticmethod
    def parse_conf(path: str = "copyparty.conf"):
        sections = {"global": {}, "accounts": {}, "volumes": {}, "extra": {}, "groups": {}}
        current = None
        block_name = None
        block_indent = 0
        lines = None
        try:
            with open(path, encoding="utf-8") as fh:
                lines = fh.readlines()
        except FileNotFoundError:
            _log(f"[-] Copyparty conf is missing. Run ctk.py init to initialize it")
            exit(1)
        if not lines:
            raise ValueError("Config file syntax is not correct")
        for raw in lines:
            stripped = _strip_comment(raw)
            if not stripped.strip():
                continue
            indent = len(stripped) - len(stripped.lstrip(' '))
            text = stripped.strip()
            if text.startswith('[') and text.endswith(']'):
                block_name = None
                name = text[1:-1].strip()
                if name == "global":
                    current = ("global", sections["global"])
                elif name == "accounts":
                    current = ("accounts", sections["accounts"])
                elif name == "groups":
                    current = ("groups", sections["groups"])
                elif name.startswith('/'):
                    vol = {}
                    sections["volumes"][name] = vol
                    current = ("volume", vol)
                else:
                    extra = {}
                    sections["extra"][name] = extra
                    current = ("extra", extra)
                continue
            if current is None:
                continue
            sect_type, target = current
            if sect_type == "volume":
                if block_name and indent <= block_indent:
                    block_name = None
                if block_name:
                    if block_name == "accs":
                        entry = text
                        if entry:
                            target.setdefault("accs", []).append(entry)
                    else:
                        group = target.setdefault(block_name, {})
                        _parse_flag_line(text, group)
                    continue
                if text.endswith(':') and ':' not in text[:-1]:
                    block_name = text[:-1]
                    block_indent = indent
                    continue
                if "path" not in target and ':' not in text:
                    target["path"] = text
                    continue
                if ':' in text:
                    k, v = text.split(':', 1)
                    target[k.strip()] = _parse_value(v.strip())
                else:
                    target[text] = True
            else:
                if sect_type == "accounts":
                    if ':' not in text:
                        continue
                    k, v = text.split(':', 1)
                    target[k.strip()] = v.strip()
                elif sect_type == "groups":
                    if ':' not in text:
                        continue
                    k, v = text.split(':', 1)
                    entries = [s.strip() for s in re.split(r',\s*', v.strip()) if s.strip()]
                    target[k.strip()] = entries
                else:
                    if ':' in text:
                        k, v = text.split(':', 1)
                        target[k.strip()] = _parse_value(v.strip())
                    else:
                        target[text] = True
        return CopypartyConf(
            global_conf=sections["global"],
            accounts=sections["accounts"],
            volumes=sections["volumes"],
            extra=sections["extra"],
            groups=sections["groups"],
            path=path
        )

    def _base_dir(self) -> Path:
        if self.vault_dir:
            return Path(self.vault_dir)
        if self._path:
            return Path(self._path).parent
        return ROOT_DIR

    def to_conf(self, path: str = None) -> str:
        def fmt_scalar(val):
            if val is True:
                return ''
            if isinstance(val, list):
                return ', '.join(str(x) for x in val)
            return str(val)

        lines = []
        if self._global:
            lines.append("[global]")
            for k, v in self._global.items():
                sval = fmt_scalar(v)
                lines.append(f"  {k}" if sval == '' else f"  {k}: {sval}")
            lines.append("")

        if self._accounts:
            lines.append("[accounts]")
            for k, v in self._accounts.items():
                lines.append(f"  {k}: {v}")
            lines.append("")

        if self._groups:
            lines.append("[groups]")
            for k, v in self._groups.items():
                vals = ', '.join(str(x) for x in v)
                lines.append(f"  {k}: {vals}")
            lines.append("")

        for vol_name, vol in self._volumes.items():
            lines.append(f"[{vol_name}]")
            if "path" in vol:
                lines.append(f"  {vol['path']}")
            for k, v in vol.items():
                if k == "path":
                    continue
                if k == "accs" and isinstance(v, list):
                    lines.append("  accs:")
                    for entry in v:
                        lines.append(f"    {entry}")
                    continue
                if isinstance(v, dict):
                    lines.append(f"  {k}:")
                    for kk, vv in v.items():
                        sval = fmt_scalar(vv)
                        lines.append(f"    {kk}" if sval == '' else f"    {kk}: {sval}")
                else:
                    sval = fmt_scalar(v)
                    lines.append(f"  {k}" if sval == '' else f"  {k}: {sval}")
            lines.append("")

        if self._extra:
            for name, content in self._extra.items():
                lines.append(f"[{name}]")
                if isinstance(content, dict):
                    for k, v in content.items():
                        sval = fmt_scalar(v)
                        lines.append(f"  {k}" if sval == '' else f"  {k}: {sval}")
                lines.append("")

        conf_str = "\n".join(lines).rstrip() + "\n"
        target_path = path or self._path
        if target_path:
            base, ext = os.path.splitext(target_path)
            backup_path = f"{base}.bak{ext}"
            if os.path.exists(target_path):
                os.replace(target_path, backup_path)
            with open(target_path, "w", encoding="utf-8") as fh:
                fh.write(conf_str)
        return conf_str

    def undo(self) -> bool:
        if not self._path:
            return False
        base, ext = os.path.splitext(self._path)
        target_path = self._path
        backup_path = f"{base}.bak{ext}"
        if not os.path.exists(backup_path) or not os.path.exists(target_path):
            return False
        swap_path = f"{base}.swap{ext}"
        os.replace(target_path, swap_path)
        os.replace(backup_path, target_path)
        os.replace(swap_path, backup_path)
        return True

    def add_user(self, user: str):
        username = sanitize(user)
        if username in self._accounts:
            _log(f"[!] User '{username}' already exists")
            return
        password = gen_passwd()
        self._accounts[username] = _gen_argon2(self.salt, password)
        self._volumes[f"/sharex/{username}"] = {
            "path": f"./sharex/{username}",
            "accs": [
                f"A: {username}",
                "r: @acct",
            ],
        }
        self._volumes[f"/{username}"] = {
            "path": f"./home/{username}",
            "accs": [
                f"A: {username}",
            ],
        }
        user_struct = TEMPLATE_DIR / 'user_account_struct.txt'
        if user_struct.exists():
            base_path = self._base_dir()
            for line in user_struct.read_text(encoding="utf-8").splitlines():
                rel = line.strip().lstrip('/')
                if not rel:
                    continue
                dest = base_path / "home" / username / rel
                dest.mkdir(parents=True, exist_ok=True)
        base_path = self._base_dir()
        sharex_dir = base_path / "sharex" / username
        sharex_dir.mkdir(parents=True, exist_ok=True)
        # _log(f"[+] Created user '{username}' with password '{password}'")
        self.to_conf()
        return password

    def rm_user(self, username: str, confirm: bool = True) -> bool:
        username = sanitize(username)
        if username == "admin":
            _log("[!] Cannot remove reserved user 'admin'")
            return False
        if username not in self._accounts:
            _log(f"[!] User '{username}' not found")
            return False
        if confirm:
            ans = input(_prompt(f"[*] Remove user '{username}' and related volumes? [y/N]: ")).strip().lower()
            if not ans.startswith('y'):
                _log("[-] Aborted")
                return False
        self._accounts.pop(username, None)
        self._volumes.pop(f"/sharex/{username}", None)
        self._volumes.pop(f"/{username}", None)
        for gname, members in list(self._groups.items()):
            filtered = [m for m in members if m != username]
            if len(filtered) != len(members):
                self._groups[gname] = filtered
        base_path = self._base_dir()
        home_dir = base_path / "home" / username
        sharex_dir = base_path / "sharex" / username
        if home_dir.exists():
            shutil.rmtree(home_dir)
        if sharex_dir.exists():
            shutil.rmtree(sharex_dir)
        _log(f"[+] Removed user '{username}' and associated data")
        self.to_conf()
        return True

    def reset_passwd(self, username: str) -> str:
        username = sanitize(username)
        if username not in self._accounts:
            _log(f"[!] User '{username}' not found")
            return ''
        new_password = gen_passwd()
        self._accounts[username] = new_password
        self.to_conf()
        return new_password

    @staticmethod
    def mkdirs(root_dir: str = None, reset: bool = False, confirm: bool = True) -> bool:
        root = os.path.abspath(root_dir) if root_dir else os.path.join(os.getenv('HOME', os.getcwd()), "partybox")
        conf_target = ROOT_DIR / "copyparty.conf"
        conf_template = TEMPLATE_DIR / "default.conf"
        if os.path.exists(root):
            is_empty = not any(os.scandir(root))
            if not is_empty:
                if not reset:
                    _log(f"[!] Target '{root}' is not empty; use reset=True to clear it")
                    return False
                if confirm:
                    ans = input(_prompt(f"[*] Delete ALL contents of '{root}'? [y/N]: ")).strip().lower()
                    if not ans.startswith('y'):
                        _log("[-] Aborted")
                        return False
                for entry in os.listdir(root):
                    target = os.path.join(root, entry)
                    if os.path.isdir(target) and not os.path.islink(target):
                        shutil.rmtree(target)
                    else:
                        os.remove(target)
                if reset and conf_target.exists():
                    conf_target.unlink()
                _log(f"[+] Cleared existing vault at '{root}'")
        else:
            os.makedirs(root, exist_ok=True)

        def _create_from_file(file_path, prefix: str = ""):
            with open(file_path, encoding="utf-8") as fh:
                for line in fh:
                    rel = line.strip()
                    if not rel:
                        continue
                    rel = rel.lstrip('/')
                    parts = [root]
                    if prefix:
                        parts.append(prefix)
                    if rel:
                        parts.append(rel)
                    dest = os.path.join(*parts)
                    os.makedirs(dest, exist_ok=True)

        _create_from_file(TEMPLATE_DIR / 'base_struct.txt')
        _create_from_file(TEMPLATE_DIR / 'admin_account_struct.txt', os.path.join("home", "admin"))
        _create_from_file(TEMPLATE_DIR / 'public_account_struct.txt', os.path.join("home", "public"))

        if not conf_target.exists() and conf_template.exists():
            salt = gen_password(24)
            admin_hash = _gen_argon2(salt, 'admin')
            tpl = conf_template.read_text(encoding="utf-8")
            tpl = tpl.replace("%vaultdir%", root)
            tpl = tpl.replace("%salt%", salt)
            tpl = tpl.replace("%hash(admin)%", admin_hash)
            if not tpl.endswith("\n"):
                tpl += "\n"
            conf_target.write_text(tpl, encoding="utf-8")
            _log(f"[+] Initialized config at '{conf_target}' with vault dir '{root}'")
        _log(f"[+] Vault ready at '{root}'")
        return True

    def add_group(self, groupname: str, *users: str):
        gname = sanitize(groupname)
        if gname in self._groups:
            _log(f"[-] Group '{gname}' already exists; adding members")
            existing = set(self._groups.get(gname, []))
            new_members = [sanitize(u) for u in users if u]
            merged = existing.union(new_members)
            self._groups[gname] = list(merged)
            if new_members:
                _log(f"[+] Added members to group '{gname}': {', '.join(new_members)}")
            self.to_conf()
            return
        members = [sanitize(u) for u in users if u]
        self._groups[gname] = members
        club_name = f"{gname}-club"
        self._volumes[f"/sharex/{club_name}"] = {
            "path": f"./sharex/{club_name}",
            "accs": [
                f"A: @{gname}",
                "r: @acct",
            ],
        }
        self._volumes[f"/{club_name}"] = {
            "path": f"./home/{club_name}",
            "accs": [
                f"A: @{gname}",
            ],
        }
        base_path = self._base_dir()
        public_struct = TEMPLATE_DIR / 'group_account_struct.txt'
        if public_struct.exists():
            for line in public_struct.read_text(encoding="utf-8").splitlines():
                rel = line.strip().lstrip('/')
                if not rel:
                    continue
                dest = base_path / "home" / club_name / rel
                dest.mkdir(parents=True, exist_ok=True)
        sharex_dir = base_path / "sharex" / club_name
        sharex_dir.mkdir(parents=True, exist_ok=True)
        _log(f"[+] Created group '{gname}' with members: {', '.join(members) if members else '(none)'}")
        self.to_conf()

    def rm_group(self, groupname: str, *users: str, confirm: bool = True) -> bool:
        gname = sanitize(groupname)
        if gname == "admin":
            _log("[!] Cannot remove reserved group 'admin'")
            return False
        if gname not in self._groups:
            _log(f"[!] Group '{gname}' not found")
            return False
        members = self._groups.get(gname, [])
        if users:
            new_members = {m for m in members}
            for u in users:
                new_members.discard(sanitize(u))
            self._groups[gname] = list(new_members)
            _log(f"[+] Removed members from group '{gname}': {', '.join(users)}")
            self.to_conf()
            return True
        if confirm:
            ans = input(_prompt(f"[*] Remove group '{gname}' and related volume? [y/N]: ")).strip().lower()
            if not ans.startswith('y'):
                _log("[!] Aborted")
                return False
        self._groups.pop(gname, None)
        self._volumes.pop(f"/sharex/{gname}-club", None)
        self._volumes.pop(f"/{gname}-club", None)
        base_path = self._base_dir()
        home_dir = base_path / "home" / f"{gname}-club"
        sharex_dir = base_path / "sharex" / f"{gname}-club"
        if home_dir.exists():
            shutil.rmtree(home_dir)
        if sharex_dir.exists():
            shutil.rmtree(sharex_dir)
        _log(f"[+] Removed group '{gname}' and associated data")
        self.to_conf()
        return True

def _extract_ver(path: Path) -> str | None:
    pattern = re.compile(r'^VER\s*=\s*[\'"]?([^\'"\s]+)')
    try:
        with open(path, "rb") as fh:
            for _ in range(30):
                line = fh.readline()
                if not line:
                    break
                try:
                    text = line.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                m = pattern.match(text.strip())
                if m:
                    return m.group(1)
    except OSError:
        return None
    return None

def update_sfx():
    url = "https://github.com/9001/copyparty/releases/latest/download/copyparty-sfx.py"
    dest = ROOT_DIR / "copyparty-sfx.py"
    tmp = ROOT_DIR / "copyparty-sfx.py.tmp"
    _log(f"[*] Updating Copyparty SFX...")
    try:
        with urllib.request.urlopen(url) as resp:
            tmp.write_bytes(resp.read())
    except Exception as e:
        _log(f"[!] Failed to download copyparty-sfx: {e}")
        return

    tmp_ver = _extract_ver(tmp)
    if not tmp_ver:
        _log(f"[!] Unable to determine version from {tmp.name}")
        tmp.unlink(missing_ok=True)
        return

    if not dest.exists():
        tmp.rename(dest)
        _log(f"[+] Successfully installed Copyparty {tmp_ver}")
        return

    cur_ver = _extract_ver(dest) or "0"
    try:
        newer = _Version(tmp_ver) > _Version(cur_ver)
    except Exception:
        newer = tmp_ver > cur_ver

    if not newer:
        _log("[*] Already at the newest version")
        tmp.unlink(missing_ok=True)
        return

    tmp.replace(dest)
    _log(f"[+] Copyparty updated from {cur_ver} to {tmp_ver}")


def _build_parser():
    parser = argparse.ArgumentParser(prog=Path(__file__).stem, description="Copyparty ToolKit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize vault structure")
    p_init.add_argument("-r", "--reset", action="store_true", help="Removes existing vault before init")
    p_init.add_argument("-d", "--root-dir", dest="root_dir", help="Root directory for the vault (default: ./partybox under cwd)")

    p_user = sub.add_parser("user", help="User operations")
    p_user.add_argument("-c", "--config", default="copyparty.conf", help="Path to copyparty.conf")
    user_sub = p_user.add_subparsers(dest="user_cmd", required=True)
    u_add = user_sub.add_parser("add", help="Create new user(s)")
    u_add.add_argument("users", nargs="+")
    u_pw = user_sub.add_parser("pw", help="Reset password for user(s)")
    u_pw.add_argument("users", nargs="+")
    u_rm = user_sub.add_parser("rm", help="Remove user(s)")
    u_rm.add_argument("users", nargs="+")

    p_group = sub.add_parser("group", help="Group operations")
    p_group.add_argument("-c", "--config", default="copyparty.conf", help="Path to copyparty.conf")
    group_sub = p_group.add_subparsers(dest="group_cmd", required=True)
    g_add = group_sub.add_parser("add", help="Create or extend a group")
    g_add.add_argument("groupname")
    g_add.add_argument("users", nargs="*", help="Group members")
    g_rm = group_sub.add_parser("rm", help="Remove group or members")
    g_rm.add_argument("groupname")
    g_rm.add_argument("users", nargs="*", help="Members to remove (empty to delete group)")

    p_update = sub.add_parser("update", help="Update Copyparty SFX")

    return parser

def main():
    args = _build_parser().parse_args()
    if args.cmd == "init":
        CopypartyConf.mkdirs(root_dir=args.root_dir, reset=args.reset, confirm=True)
        return

    if args.cmd == "user":
        conf = CopypartyConf.parse_conf(args.config)
        if args.user_cmd == "add":
            for u in args.users:
                pwd = conf.add_user(u)
                if pwd:
                    _log(f"[+] Added user '{sanitize(u)}' with password '{pwd}'")
        elif args.user_cmd == "pw":
            for u in args.users:
                pwd = conf.reset_passwd(u)
                if pwd:
                    _log(f"[+] Reset password for '{sanitize(u)}' -> '{pwd}'")
        elif args.user_cmd == "rm":
            for u in args.users:
                conf.rm_user(u, confirm=True)
        return

    if args.cmd == "group":
        conf = CopypartyConf.parse_conf(args.config)
        if args.group_cmd == "add":
            conf.add_group(args.groupname, *args.users)
        elif args.group_cmd == "rm":
            conf.rm_group(args.groupname, *args.users, confirm=True)
        return

    if args.cmd == "update":
        update_sfx()
        return


if __name__ == '__main__':
    main()
