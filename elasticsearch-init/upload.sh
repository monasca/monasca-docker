#!/bin/sh
# shellcheck shell=dash

TPL_DIR=/elasticsearch-templates

_get_tpl_name_from_file() {
    local tpl=$1
    local tpl_name
    tpl_name=$(basename "$tpl")
    echo "$tpl_name"
}


if [ ! -d $TPL_DIR ]; then
    echo "ERROR: directory $TPL_DIR not found"
    exit 1
fi

TPLS=$(ls $TPL_DIR)
if [ -z "$TPLS" ]; then
    echo "ERROR: no templates found"
    exit 2
fi

for template in $TPLS; do
    echo "Handling template file $template"
    tpl_name=$(_get_tpl_name_from_file "$template")

    curl -XPUT --retry 2 --retry-delay 2 "$ELASTICSEARCH_URI"/_template/"${tpl_name}" -d @$TPL_DIR/"$template"
    returnCode=$?
    if test "$returnCode" != "0"; then
        echo "ERROR: curl to elasticsearch API failed with: $returnCode"
        exit 3
    fi
done
