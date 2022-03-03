#@IgnoreInspection BashAddShebang
function do_compose {
    COMPOSE_COMMAND=$1
    FILE_LIST=$2
    SERVICE_LIST=$3

    TERM_CMD="gnome-terminal --geometry=132x43"
    for i in ${SERVICE_LIST}; do
        TERM_CMD="${TERM_CMD} --tab --command 'bash -c \"printf \\\"\033]0;${i}\007\\\"; docker-compose ${FILE_LIST} ${COMPOSE_COMMAND} ${i}; read -n1;\"'"
    done;

    echo "docker-compose ${COMPOSE_COMMAND}"
    eval "${TERM_CMD}"
}
