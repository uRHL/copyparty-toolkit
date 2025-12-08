#!/bin/bash

# Auto-Install Copyparty-Toolkit (debian 12)

REPO_URL="https://github.com/uRHL/copyparty-toolkit.git"
INSTALL_DIR="$HOME/copyparty-toolkit"
PYTHON_VER="3.13.0"
PYTHON_ENV="copyparty"

usage() {
  cat <<EOF
Usage: $0 [-v|--verbose] [--remove] [-h|--help]

Options:
  -v, --verbose   Show command output (default: quiet)
  -h, --help      Show this help message
  --remove        Uninstall Copyparty and CTK
EOF
}

VERBOSE=0
DO_REMOVE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--verbose) VERBOSE=1 ;;
    -h|--help) usage; exit 0 ;;
    --remove) DO_REMOVE=1 ;;
    *) usage; exit 1 ;;
  esac
  shift
done

run_cmd() {
  if [[ $VERBOSE -eq 1 ]]; then
    bash -c "$1"
  else
    bash -c "$1" >/dev/null 2>&1
  fi
}

cecho() {
  local msg="$1" color=""
  case "${msg:0:3}" in
    "[+]") color="\033[32m";;
    "[-]") color="\033[33m";;
    "[!]") color="\033[31m";;
    "[*]") color="\033[96m";;
  esac
  if [[ -n "$color" ]]; then
    printf "%b\n" "${color}${msg}\033[0m"
  else
    printf "%s\n" "$msg"
  fi
}

cecho_err() {
  cecho "$1" >&2
}

reload_shell_env() {
  cecho "[*] Reloading shell configuration"
  source "$HOME/.bashrc"
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to reload shell configuration"
    exit 1
  fi
  cecho "[+] Shell configuration reloaded"
}

remove_dptk() {
  cecho "[*] Uninstalling..."
  # export PYENV_ROOT="$HOME/.pyenv"
  # export PATH="$PYENV_ROOT/bin:$PATH"
  # eval "$(pyenv init - bash)"
  cecho "[*] Removing virtual environment '$PYTHON_ENV'"
  pyenv virtualenv-delete -f $PYTHON_ENV
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to remove virtual environment '$PYTHON_ENV'"
    exit 1
  fi
  cecho "[+] Removed virtual environment '$PYTHON_ENV'"

  cecho "[*] Uninstalling Python $PYTHON_VER"
  pyenv uninstall -f $PYTHON_VER
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to uninstall Python $PYTHON_VER"
    exit 1
  fi
  cecho "[+] Uninstalled Python $PYTHON_VER"

  cecho "[*] Removing Copyparty and CTK from '$INSTALL_DIR'"
  rm -fr \"$INSTALL_DIR\"
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to remove '$INSTALL_DIR'"
    exit 1
  fi
  cecho "[+] Successfully uninstalled Copyparty and CTK"
  exit 0
}

install_ctk() {
  # Ensure system is up-to-date
  cecho "[*] Ensuring system is up to date"
  apt update && apt upgrade -y > /dev/null
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to update system"
    exit 1
  fi
  cecho "[+] System updated"

  # Install dependencies
  cecho "[*] Installing system dependencies"
  apt update && apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python3.11-venv -y > /dev/null
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to install system dependencies"
    exit 1
  fi
  cecho "[+] System dependencies installed"

  # Download pyenv
  cecho "[*] Installing pyenv"
  curl -fsSL https://pyenv.run | bash
  if [ $? -eq 1 ]; then
    cecho "[-] Package already installed"
  elif [ $? -ne 0 ]; then
    cecho_err "[!] Failed to install pyenv (errno: $?)"
    exit 1
  else
    cecho "[+] pyenv installed"
  fi
  

  # Add pyenv to PATH
  cecho "[*] Configuring pyenv PATH"
  if [[ -z "$PYENV_ROOT" ]] || ! grep -q "export PYENV_ROOT=" "$HOME/.bashrc"; then
    echo "export PYENV_ROOT=\"\$HOME/.pyenv\"" >> "$HOME/.bashrc"
    echo "[[ -d \$PYENV_ROOT/bin ]] && export PATH=\"\$PYENV_ROOT/bin:\$PATH\"" >> "$HOME/.bashrc"
    echo "eval \"\$(pyenv init - bash)\"" >> "$HOME/.bashrc"
    echo "export PATH=\"$INSTALL_DIR/:\$PATH\"" >> "$HOME/.bashrc" # Add install dir to PATH
    cecho "[+] pyenv PATH configured"
  else
    cecho "[-] PYENV_ROOT already set, skipping PATH configuration"
  fi

  reload_shell_env  # Reload shell env again

  # Install python
  cecho "[*] Installing Python $PYTHON_VER with pyenv"
  pyenv install $PYTHON_VER
  if [ $? -eq 1 ]; then
    cecho "[-] Python $PYTHON_VER already installed"
  elif [ $? -ne 0 ]; then
    cecho_err "[!] Failed to install Python $PYTHON_VER"
    exit 1
  else
    cecho "[+] Python $PYTHON_VER installed"
  fi

  # Create virtual env
  cecho "[*] Creating virtualenv '$PYTHON_ENV'"
  pyenv virtualenv $PYTHON_ENV
  if [ $? -eq 1 ]; then
    cecho "[-] Virtualenv '$PYTHON_ENV' already exists"
  elif [ $? -ne 0 ]; then
    cecho_err "[!] Failed to create virtualenv '$PYTHON_ENV'"
    exit 1
  else
    cecho "[+] Virtualenv '$PYTHON_ENV' created"
  fi
  

  # Activate virtual env
  cecho "[*] Activating virtualenv '$PYTHON_ENV'"
  pyenv deactivate 2> /dev/null; source "$HOME/.bashrc" # Deactivate current env, if any
  pyenv activate $PYTHON_ENV
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to activate virtualenv '$PYTHON_ENV'"
    exit 1
  fi
  cecho "[+] Virtualenv '$PYTHON_ENV' activated"

  # Install dependencies for: pw-hashing, thumbnails, audio and video, raw images, SFTP and version numbers
  cecho "[*] Installing Python dependencies"
  pip install argon2-cffi mutagen Pillow ffmpeg ffprobe rawpy pyftpdlib pyopenssl packaging
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to install Python dependencies"
    exit 1
  fi
  # or pip install -r requirements.txt
  cecho "[+] Python dependencies installed"

  # Downloading Copyparty-Toolkit...
  cecho "[*] Downloading Copyparty-Toolkit..."
  git clone $REPO_URL "$INSTALL_DIR"
  if [ $? -ne 0 ]; then
    cecho_err "[!] Failed to download Copyparty-Toolkit"
    exit 1
  fi
  cecho "[+] Copyparty-Toolkit downloaded successfully"
  
  # Update permissions so executables are listed
  chmod u+x copyparty-toolkit/ctk.py copyparty-toolkit/copyparty-sfx.py copyparty-toolkit/install_ctk.sh

  # Download Copyparty 
  python3 $INSTALL_DIR/ctk.py update
  echo ""
  cecho "[*] Next steps:"
  cecho "[*] 1. Init config:             python3 ctk.py init"
  cecho "[*] 2. Run Copyparty:           python3 copyparty-sfx.py -c copyparty.conf"
}

# If remove flag set, perform uninstall and exit
if [[ $DO_REMOVE -eq 1 ]]; then
  read -rp "[*] Are you sure you want to uninstall Copyparty and CTK? [y/N]: " ans
  ans=${ans,,}
  if [[ $ans == y* ]]; then
    remove_dptk
  else
    cecho "[-] Aborted"
    exit 0
  fi
else
  install_ctk
fi
