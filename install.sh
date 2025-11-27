#!/bin/bash

args=("$@")
NC='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' BLUE='\033[0;34m' YELLOW='\033[0;33m'

set -e
set -o pipefail
catch() {
    echo -e "${RED}$1${NC}"
    exit 1
}

choose() {
    echo -e "${GREEN}choose $1:${NC}"
    for idx in "${!options[@]}"; do
        echo "$((idx + 1))) ${options[idx]}"
    done
    read -r -p "> " chosen </dev/tty
    chosen=$(($(echo "$chosen" | sed -r "s/[^0-9]//g") - 1))
    if [[ ${chosen} -lt '0' ]] || [[ ${chosen} -ge ${#options[@]} ]]; then
        echo -e "${RED}incorrect value${NC}"
        exit 1
    fi
    result=${options[chosen]}
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

# -----------------------------------------------------------
# ------------------- prerequisites setup -------------------

echo -e "${BLUE}setting up prerequisites...${NC}"
trap 'catch "failed to set up prerequisites"' ERR

if ! [[ -x "$(command -v conda)" ]]; then
    if confirm "conda not found, install miniconda"; then
        echo -e "${BLUE}installing miniconda...${NC}"
        wget -q --show-progress https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
        bash ~/miniconda.sh -u -b -p "$HOME/miniconda"
        rm ~/miniconda.sh
        # shellcheck disable=SC2086
        eval "$($HOME/miniconda/bin/conda shell.bash hook)"
        conda init
        conda config --set auto_activate_base false
        conda config --set env_prompt '({name}) '
        source ~/.bashrc
        echo -e "${BLUE}conda installed, version: ${NC}$(conda --version | cut -d " " -f 2)"
    else
        echo -e "${RED}conda is required, so please install miniconda or anaconda first${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}conda found, version: ${NC}$(conda --version | cut -d " " -f 2)"
fi

if [[ -f ./setup/system.sh ]]; then
    echo -e "${BLUE}running system install script...${NC}"
    if ! source ./setup/system.sh; then
        echo -e "${RED}system install script failed${NC}"
        exit 1
    fi
fi

if ! [[ -x "$(command -v poetry)" ]]; then
    if confirm "poetry not found, install poetry"; then
        echo -e "${BLUE}installing poetry...${NC}"
        export POETRY_HOME="$HOME/.poetry"
        wget -qO- https://install.python-poetry.org | $CONDA_PYTHON_EXE -
        if ! grep -q "export PATH=$POETRY_HOME/bin" ~/.bashrc; then
            echo "export PATH=$POETRY_HOME/bin:\$PATH" >> ~/.bashrc
            export PATH=$POETRY_HOME/bin:$PATH
        fi
        echo -e "${BLUE}poetry installed, version: ${NC}$(poetry --version | cut -d " " -f 3)"
    else
        echo -e "${RED}poetry is required, so please install it first${NC}"
        exit 1
    fi
else
    echo -e "${BLUE}poetry found, version: ${NC}$(poetry --version | cut -d " " -f 3)"
fi

# -----------------------------------------------------------
# ------------------ environment setup ----------------------

echo -e "${BLUE}setting up environment...${NC}"
trap 'catch "failed to set up environment"' ERR

if [[ -d ".venv" ]]; then
    if confirm "looks like environment already exists, remove and reinstall"; then
        echo -e "${BLUE}removing environment...${NC}"
        rm -rf .venv
    else
        echo -e "${YELLOW}installation cancelled${NC}"
        exit 0
    fi
fi

if ! [[ -f environment.yml ]]; then
    options=("3.7.11" "3.8.11" "3.9.7" "3.10.0")
    choose "Python version"
    {
        echo "name: venv"
        echo "channels:"
        echo "  - conda-forge"
        echo "  - defaults"
        echo "dependencies:"
        echo "  - python=${result}"
    } > environment.yml
fi

conda env create --prefix=./.venv -f environment.yml

# -----------------------------------------------------------
# ------------------ dependencies setup ---------------------

echo -e "${BLUE}setting up dependencies...${NC}"
trap 'catch "failed to set up dependencies"' ERR

if [[ ${args[0]} == "--unattended" ]]; then
    mode="production"
else
    options=("production" "development")
    choose "environment type"; mode=$result
fi

if ! [[ -f pyproject.toml ]]; then
    dependencies="--dependency=python-dotenv:~1.0.0
                  --dependency=tomlkit:~0.12.3
                  --dependency=loguru:~0.7.2
                  --dependency=pydantic:~1.9.0"
    # shellcheck disable=SC2086
    poetry init --python="$(./.venv/bin/python --version | sed 's/Python //')" $dependencies
    poetry install
else
    if [[ $mode == "development" ]]; then
        poetry install
    else
        poetry install -n --only main
    fi
fi

# -----------------------------------------------------------
# --------------- application configuration -----------------

echo -e "${BLUE}configuring application...${NC}"
trap 'catch "failed to configure application"' ERR

{
    echo "APP_MODE=${mode}"
    echo "APP_ROOT=$(pwd)"
    echo "APP_DEPRECATIONS=false"
    echo ""
    echo "TZ=UTC"
} > .env

mkdir -p ./setup
if [[ -f ./setup/settings.toml ]]; then
  cp -n ./setup/settings.toml settings.toml
else
    touch settings.toml
    touch ./setup/settings.toml
fi

echo "-----------------------------------------------------------"
echo -e "${BLUE}installation finished, don't forget to:${NC}"
echo -e "${BLUE}- check and complete configuration of settings.toml${NC}"
