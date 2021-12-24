# clickable helper scripts

Helper scripts to write click applications development's environment


* Free software: BSD license


## Features

Clickable allows to easily write python and shell-based tools for your projects.

Clickable is based on the following building-blocks:

* a bootstrap.py standalone script that installs a conda based python environment,
  that allows to initialize an isolated python environment.
  (https://github.com/lalmeras/clickable_bootstrap)

* a bootstrap.py's post-install callback that uses poetry to install:

  * your project-related command(s)
  * by python dependencies mechanism, clickable and any optional dependencies

* clickable python library, that provides a clickables.py/clickables.yml file
  loading mechanism

* clickable extensions that provide helpers for writing sphinx, ansible, ...
  commands

Clickable is heavily based on Python, Conda, Poetry and Click projects.


## Release

Stable branch is `master`; development branch is `dev`. Usual release steps are :

```
# install dev tools and switch in pipenv
pipenv install --dev
pipenv shell

# if needed, update Pipfile.lock and commit changes
pipenv lock --clear
pipenv install --dev

# prepare dev branch for release...
# update version
# increase version; may be launch multiple time to cycle dev, rc, ...
bump2version --verbose prerel [--allow-dirty] [--no-commit] [--no-tag]

# merge on main
git checkout main
git pull
git merge dev

# prepare next development version (+1dev0)
git checkout dev
bump2version --verbose --no-tag minor

# push all (launch with --dry-run to check before actual update)
# delete (git tag -d <tag> unneeded tags - dev, rc)
git push --all
git push --tag

# publish (pypi credentials required)
git checkout tag
pipenv shell
python setup.py clean --all
rm -rf dist/*
python setup.py sdist
python setup.py bdist_wheel
# fake upload
# run pypi-server in another shell
mkdir -p /tmp/packages && pypi-server -P . -a . /tmp/packages/
twine upload  -u "" -p "" --repository-url http://localhost:8080/ dist/*.whl dist/*.tar.gz

# real upload
twine upload dist/*.whl dist/*.tar.gz
```
