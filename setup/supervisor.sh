#!/bin/bash

args=("$@")
NC='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' BLUE='\033[0;34m' YELLOW='\033[0;33m'

set -e
set -o pipefail
catch() {
    echo -e "${RED}$1${NC}"
    exit 1
}

confirm() {
    if [[ ${args[0]} == "--unattended" ]]; then
        return 0
    fi
    echo -en "${2:-$YELLOW}"
    read -p "$1 [y/n] ? " -n 1 -r </dev/tty
    echo -e "${NC}"
    if [[ $REPLY =~ ^[Yy]$ ]]; then return 0; fi
    return 1
}


trap 'catch "failed to read application data"' ERR
project=$(sed -nr "/^\[tool.poetry\]/ { :l /^name[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./pyproject.toml | tr -d '"')
host=$(sed -nr "/^\[service\]/ { :l /^host[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./settings.toml | tr -d '"')
port=$(sed -nr "/^\[service\]/ { :l /^port[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./settings.toml | tr -d '"')
project=${project:-${PWD##*/}}
host=${host:-0.0.0.0}
port=${port:-8000}
export project host port


trap 'catch "failed to set up prerequisites"' ERR
if ! [[ -x "$(command -v supervisord)" ]]; then
    if confirm "supervisor not found, install supervisor"; then
        echo -e "${BLUE}installing supervisor...${NC}"
        sudo apt-get -y install supervisor
        echo -e "${BLUE}supervisor installed, version: ${NC}$(supervisord -v)"
    else
        echo -e "${RED}supervisor is required, so please install it first${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}supervisor found, version: ${NC}$(supervisord -v)"
fi


trap 'catch "failed to configure supervisor service"' ERR
for file in setup/templates/supervisor/conf.d/*.conf; do
    if confirm "found supervisor template '${project}-${file##*/}' configure service"; then
        # shellcheck disable=SC2002
        cat "${file}" | envsubst | sudo tee "/etc/supervisor/conf.d/${project}-${file##*/}" > /dev/null
        echo -e "${GREEN}supervisor service configured${NC}"
    fi
    sudo supervisorctl update
done
