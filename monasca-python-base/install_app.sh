#!/bin/sh

REPO=$1
BRANCH=$2

# list of extras i.e. monasca-agent['libvirt']
EXTRAS=${3-""}

# extra dependencies not listed anywhere in project
# neither in requirements not in setup.cfg extras
EXTRA_DEPS=${4:-""}

# requirements file for given OpenStack release
CONSTRAINTS_FILE=$5

if [ -z $REPO and -z $BRANCH ]; then
    echo "No repo and branch provided"
fi

git init
git remote add origin $REPO
git fetch origin $BRANCH
git reset --hard FETCH_HEAD

if [ -n $EXTRA_DEPS ]; then
    pip install --no-cache-dir ${EXTRA_DEPS} -c $CONSTRAINTS_FILE
fi
if [ -n $EXTRA ]; then
    pip install --no-cache-dir .[${extra}] -c $CONSTRAINTS_FILE
fi
pip install --no-cache-dir -r requirements.txt -c $CONSTRAINTS_FILE
python setup.py install
