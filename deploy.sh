#! /bin/bash

# fail fast
set -e

GPG_USER="clickable.project@gmail.com"
GPG_OPTS="--pinentry-mode loopback --passphrase-fd 0"

# import signing key
echo "${gpg_passphrase}" | \
  gpg $GPG_OPTS --import clickable.gpg

# build
python setup.py sdist bdist_wheel --python-tag py3

# sign
for file in dist/*; do
  echo "$gpg_passphrase" | \
    gpg $GPG_OPTS --detach-sign -u "$GPG_USER" --armor -o "$file.asc" "$file" >/dev/null 2>&1
done
echo "dist/ files"
ls dist/

# publish
TWINE_PASSWORD="${pypi_token}" twine upload -u __token__ dist/*
