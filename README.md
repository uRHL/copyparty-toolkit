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
curl -fsSL https://raw.githubusercontent.com/uRHL/copyparty-toolkit/refs/heads/main/install.sh | bash


```

## Getting started with Copyparty

```bash
python3 toolkit.py init
python3 toolkit.py user add "User Name" # Creates user 'user-name' and correspoding shares
python3 toolkit.py group add group-name "user-name" # Add user-name to group
python toolkit.py group rm group-name "user-name" # Remove user-name from group

```

## Requirements.txt

```conf
argon2-cffi==25.1.0
argon2-cffi-bindings==25.1.0
cffi==2.0.0
cryptography==46.0.3
ffmpeg==1.4
ffprobe==0.5
mutagen==1.47.0
numpy==2.3.5
pillow==12.0.0
pycparser==2.23
pyftpdlib==2.1.0
pyOpenSSL==25.3.0
rawpy==0.25.1
typing_extensions==4.15.0
```

```bash
I want you to create a new flag "--remove" which executes remove_dptk() function.
That function does the following:

```bash
# TODO: prompt user to confirm uninstalling
echo "[*] Uninstalling..."
# Removing virtual environment
pyenv virtualenv-delete $PYTHON_ENV
# Uninstalling Python $PYTHON_VER
pyenv uninstall $PYTHON_VER
# Removing Copyparty and CTK
rm -fr $INSTALL_DIR
echo "[+] Successfully uninstalled Copyparty and CTK
```

I want you to implement the flag and function. Apply the same logging we are using for the rest of steps (print before, result)
```
