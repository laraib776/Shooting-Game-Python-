#!/usr/bin/env bash
set -euo pipefail

python3 -m pip install --user buildozer cython
buildozer android debug

echo ""
echo "Android debug APK should be in:"
echo "  bin/"
