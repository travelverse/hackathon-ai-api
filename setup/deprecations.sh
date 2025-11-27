#!/bin/bash

# installs Python configuration hook to disable deprecation warning once and for all

site=$(./.venv/bin/python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
cp -fr $PWD/setup/deprecations.pth $site/deprecations.pth
echo "configuration hook installed, deprecations are muted"
