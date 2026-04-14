# Copyparty toolkit

- https://github.com/cloudflare/cfssl

`init` command creates the following dir structure in the provided `--root-dir` or cwd if none.
```bash
/sharex
/tmp
/home
    /admin
        /Documents    
        /Music
        /Pictures
        /Videos
    /public
        /Documents
            /00-tools
            /01-vm
        /Music
        /Pictures
        /Videos
```
`add user` creates a new user. That implies:
- Create dirs `sharex/username`
- Create dir `home/username/{Documents,Music,Pictures,Videos}`
- Create account: `[account] user:password`
- Add volumes:
```yaml
[/sharex/user]
  ./sharex/user
  accs:
    A: user
    r: @acct
[/user]
  ./home/user
  accs:
    A: user
```

`add group` creates a new group, that implies:
- Create group: `[groups] groupname: user1, user2`
- Add volumes
```yaml
[/group-club]
  ./home/group-club
  accs:
    A: @group
[/sharex/group-club]
  ./sharex/group-club
  accs:
    A: user
    r: @acct
```

## Installing cp Toolkit

```bash
apt update && apt install git curl
curl -fsSL https://raw.githubusercontent.com/uRHL/copyparty-toolkit/refs/heads/main/install_ctk.sh | bash


```

## Getting started with Copyparty

```bash
python3 ctk.py init
python3 ctk.py user add "User Name" # Creates user 'user-name' and correspoding shares
python3 ctk.py group add group-name "user-name" # Add user-name to group
python ctk.py group rm group-name "user-name" # Remove user-name from group

```

## Requirements.txt

`pip freeze | xclip -selection clipboard`

```conf
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
cffi==2.0.0
MarkupSafe==3.0.3
packaging==25.0
pycparser==2.23
PyYAML==6.0.3
```

## Configring Copyparty as a service

- [Documentation](https://github.com/9001/copyparty/tree/hovudstraum?tab=readme-ov-file#on-servers)

```bash
sudo useradd -r -s /usr/sbin/nologin -m -d /var/lib/copyparty copyparty
# - Assert copyparty-sfx.py, is placed under /usr/local/bin/, and ug+x.
# - Also place your copyparty.conf under /etc/ (or whichever config path you choose).

sudo cp copyparty.service /etc/systemd/system/  # Install systemd unit
sudo systemctl daemon-reload  # Reload systemd to pick up the new unit:
sudo systemctl enable --now copyparty  # Start the service and enable on 

# Check status and logs:
sudo systemctl status copyparty
sudo journalctl -u copyparty -f
```

## TODO

- [ ] Enable Copyparty as a service
- [ ] Mount external drive so that is accessible by Copyparty
- [ ] Review FW to check if it is necessary to open ports
- [ ] https://pi-hole.net/


FreeBSD Mastery: Advanced ZFS
FreeBSD Mastery: ZFS: Volume 7 (IT Mastery) Paperback – 16 May 2015
https://wintelguy.com/html_character_codes.pl
https://github.com/bashclub/zamba-lxc-toolbox?tab=readme-ov-file