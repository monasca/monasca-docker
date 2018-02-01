#!/bin/sh
# shellcheck shell=dash

set -x

if [ -e /apk.sh ]; then
    echo "Overriding default apk dependencies install function"
    # shellcheck disable=SC1091
    . /apk.sh
else
    echo "Using default apk dependencies install function"
    install_apk_deps() {
        echo "No APK dependencies by default"
    }
fi

if [ -e /install.sh ]; then
    echo "Overriding default install function"
    # shellcheck disable=SC1091
    . /install.sh
else
    echo "Using default install function"
    install() {
        local constraints=${1}
        local extras=${2}
        local extra_deps=${3}

        if [ "z$extra_deps" != "z" ]; then
            for extra in $extra_deps; do
                pip install --no-cache-dir "$extra" -c "$constraints"
            done
        else
            echo "No extra dependencies"
        fi

        if [ "z$extras" != "z" ]; then
            for extra in $extras; do
                pip install --no-cache-dir .["${extra}"] -c "$constraints"
            done
        else
            echo "No extras"
        fi

        pip install --no-cache-dir -r requirements.txt -c "$constraints"
        python setup.py install
    }
fi

if [ -e /clone.sh ]; then
    echo "Overriding default clone function"
    # shellcheck disable=SC1091
    . /clone.sh
else
    echo "Using default clone function"
    clone() {
        local repo=$1
        local branch=$2

        git init
        git remote add origin "${repo}"
        git fetch origin "${branch}"
        git reset --hard FETCH_HEAD

    }
fi

# declare variables
REPO=""
BRANCH=""
EXTRAS=""
EXTRA_DEPS=""
CONSTRAINTS=""
CONSTRAINTS_URL=""
CONSTRAINTS_BRANCH=""

if ! OPTS=$(getopt -n 'parse-options' -o r:b:e:d:c:u:q: -- "$@"); then
  echo "Failed parsing options." >&2
  exit 1
fi

echo "$OPTS"
eval set -- "$OPTS"

# process args
while true; do
    case "${1}" in
        -r) REPO=${2}; shift 2 ;;
        -b) BRANCH=${2}; shift 2 ;;
        -e) EXTRAS=${2}; shift 2 ;;
        -d) EXTRA_DEPS=${2}; shift 2 ;;
        -c) CONSTRAINTS=${2}; shift ;;
        -u) CONSTRAINTS_URL=${2}; shift 2 ;;
        -q) CONSTRAINTS_BRANCH=${2}; shift 2 ;;
        -- ) shift; break ;;
        * ) break ;;
    esac
done

# handle the arguments / defaults etc.
CONSTRAINTS_BASE="https://git.openstack.org/cgit/openstack/requirements/plain/upper-constraints.txt"
BRANCH=${BRANCH:-master}
CONSTRAINTS_BRANCH=${CONSTRAINTS_BRANCH:-$BRANCH}
CONSTRAINTS_URL=${CONSTRAINTS_URL:-$CONSTRAINTS_BASE}
CONSTRAINTS=${CONSTRAINTS:-"$CONSTRAINTS_URL?h=$CONSTRAINTS_BRANCH"}
EXTRAS="${EXTRAS:-""}"
EXTRA_DEPS="${EXTRA_DEPS:-""}"

echo "Installing APK Dependencies" && install_apk_deps
mkdir -p /app
cd /app || exit

# actual build happens here
cat << EOF
Build environment:
PROJECT=${REPO}@${BRANCH}
EXTRAS=${EXTRAS}
CONSTRAINTS=${CONSTRAINTS}
EXTRA_DEPENDENCIES=${EXTRA_DEPS}
EOF
echo "Cloning ${REPO}@${BRANCH}" && clone "${REPO}" "${BRANCH}"
echo "Installing ${REPO}" && install "${CONSTRAINTS}" "${EXTRAS}" "${EXTRA_DEPS}"
# end of actual build

cd - || exit
rm -rf /install.sh /clone.sh /install_apk_deps.sh /app /root/.cache/pip

apk del build-dep
