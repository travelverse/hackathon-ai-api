#!/bin/bash

NC='\033[0m' GREEN='\033[0;32m' BLUE='\033[0;34m' YELLOW='\033[0;33m'

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

# shellcheck disable=SC2046,SC2002
export $(cat .env | xargs)

case "$1" in
    clean)
        find ./app -name '*.pyc' -exec rm -fv {} +
        find ./app -name '*.pyo' -exec rm -fv {} +
        find ./app -name '*~' -exec rm -fv {} +
        find ./app -name '__pycache__' -exec rm -frv {} +
    ;;
    lint)
        if [[ $APP_MODE == "development" ]]; then
            RESULT=$(./.venv/bin/pylint app)
            if [[ -z "$RESULT" ]]; then
                echo -e "${GREEN}everything looks good${NC}"
            else
                echo "${RESULT}"
            fi
        else
            echo -e "${YELLOW}this command intended to use in development environment${NC}"
        fi
    ;;
    deptree)
        if [[ $APP_MODE == "development" ]]; then
            poetry show --tree --latest
        else
            poetry show --tree --latest --no-dev
        fi
    ;;
    update)
        conda env update --prefix ./.venv --file environment.yml --prune
        if [[ $APP_MODE == "development" ]]; then
            poetry update
        else
            poetry update --no-dev
        fi
    ;;
    switch)
        options=("production" "development")
        choose "environment type"; mode=$result
        if [[ $mode == "development" ]]; then
            poetry update
        else
            poetry update --no-dev
        fi
        {
            echo "APP_MODE=${mode}"
            echo "APP_ROOT=$(pwd)"
        } > .env
    ;;
    version)
        version=$(sed -nr "/^\[tool.poetry\]/ { :l /^version[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" ./pyproject.toml | tr -d '"')
        version=${version:-0.0.0}
        echo "$version"
    ;;
    *)
        echo -e "${YELLOW}Usage${NC}: $0 command [args]..."
        echo ""
        echo -e "${YELLOW}Commands${NC}:"
        echo -e "  ${BLUE}clean${NC}       remove Python file artifacts"
        echo -e "  ${BLUE}lint${NC}        run code analysis with flake8"
        echo -e "  ${BLUE}deptree${NC}     show dependency tree of installed packages"
        echo -e "  ${BLUE}update${NC}      update application dependencies"
        echo -e "  ${BLUE}switch${NC}      switch application mode"
        echo -e "  ${BLUE}version${NC}     print current application version"
        exit 1
esac
