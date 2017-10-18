#!/bin/sh
# shellcheck shell=dash

TPL_DIR=/templates

_get_tpl_name_from_file() {
    local tpl=$1
    local tpl_name
    tpl_name=$(basename "$tpl")
    echo "$tpl_name"
}

if [ ! -d $TPL_DIR ]; then
    echo "No templates mounted"
    exit 0
else
    TPLS=$(ls $TPL_DIR)
fi

for template in $TPLS; do

    echo "Handling template file $template"
    tpl_name=$(_get_tpl_name_from_file "$template")

    curl -XPUT --retry 2 --retry-delay 2 "$ELASTICSEARCH_URI"/_template/"${tpl_name}" -d @$TPL_DIR/"$template"

done
