from alpine:3.5

run apk add --no-cache mysql-client
copy init.sh /init.sh
copy mysql-init.d /mysql-init.d/

cmd ["/init.sh"]
