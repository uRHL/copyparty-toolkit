# Copyparty toolkit

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
# apt update && apt install git
git clone https://user/repo.git
bash auto_install.sh
```

## Installing Copyparty

```bash
# AUTOINSTALL FROM DEBIAN 12
# Install dependencies
apt update && apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python3.11-venv

# Download pyenv
curl -fsSL https://pyenv.run | bash

# Add pyenv to PATH
echo -e "export PYENV_ROOT=\"$HOME/.pyenv\"\n[[ -d $PYENV_ROOT/bin ]] && export PATH=\"$PYENV_ROOT/bin:$PATH\"\neval \"$(pyenv init - bash)\"" | tee -a .bashrc

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

# Download copyparty
wget https://github.com/9001/copyparty/releases/latest/download/copyparty-sfx.py

# 
python3 cp-toolkit.py init
python3 copyparty-sfx.py -c /root/copyparty.conf

```

Add a new subparser "update" which "Updates Copyparty SFX". It does the following:
1. download https://github.com/9001/copyparty/releases/latest/download/copyparty-sfx.py into ROOT_DIR, appending ".tmp" to the file name so that current copyparty-sfx.py (if exists) is not overwriten.
2. If file "copyparty-sfx.py" does not exist yet, print message "Successfully installed Copyparty <tmp.VER> then strip .tmp suffix from the file and return.
2. If file "copyparty-sfx.py" already exists, compare the variable "VER" (moreless around line 26) of current "copyparty-sfx.py" against "VER" from "copyparty-sfx.py.tmp". If tmp.VER == current.VER, print message "Already at the newest version" and delete tmp file. If tmp.VER > current.VER, print message "Copyparty updated from <current.VER> to <tmp.VER>" then replace current "copyparty-sfx.py" by "copyparty-sfx.py.tmp", so that only the highest version "copyparty-sfx" is preserved.

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