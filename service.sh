#!/bin/bash

NC='\033[0m' RED='\033[0;31m'

if ! [[ -f ".env" ]] || ! [[ -f "config/settings.toml" ]] || ! [[ -d ".venv" ]]; then
    echo -en "${RED}"
    echo "missing required application gears"
    echo "looks like application is not properly installed"
    echo -en "${NC}"
    exit 1
fi

set -o allexport
. .env
set +o allexport

./.venv/bin/python app/service.py service:app "$@"
