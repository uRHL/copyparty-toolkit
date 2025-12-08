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
bash https://user/repo/install.sh | bash


```

## Installing Copyparty

```bash
# AUTOINSTALL FROM DEBIAN 12

INSTALL_DIR="$HOME/cp-toolkit"

# Ensure system is up-to-date
apt update && apt upgrade -y

# Download tool
git clone https://user/repo.git -d "$INSTALL_DIR"

# Install dependencies
apt update && apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python3.11-venv -y

# Download pyenv
curl -fsSL https://pyenv.run | bash

# Add pyenv to PATH
echo -e "export PYENV_ROOT=\"$HOME/.pyenv\"\n[[ -d $PYENV_ROOT/bin ]] && export PATH=\"$PYENV_ROOT/bin:$PATH\"\neval \"$(pyenv init - bash)\"" | tee -a .bashrc

# Download tool
git clone https://user/repo.git

# Add repo to path
echo -e "\nexport PATH=\"$INSTALL_DIR:$PATH\"" | tee -a .bashrc

# Reload virtual env
source .bashrc

# Install python
pyenv install 3.13.0

# Create virtual env
pyenv virtualenv copyparty

# Activate virtual env
pyenv activate copyparty

# Install dependencies for: pw-hashing, thumbnails, audio and video, raw images, SFTP
pip install argon2-cffi mutagen Pillow ffmpeg ffprobe rawpy pyftpdlib pyopenssl
# or pip install -r requirements.txt

# Download Copyparty 
python3 cp-toolkit.py update

# Initialize vault
python3 cp-toolkit.py init

# Run Copyparty
python3 copyparty-sfx.py -c /root/copyparty.conf

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
# Removing Copyparty and CPTK
rm -fr $INSTALL_DIR
echo "[+] Successfully uninstalled Copyparty and CPTK
```

I want you to implement the flag and function. Apply the same logging we are using for the rest of steps (print before, result)
```
