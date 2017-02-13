from alpine:3.5

run apk add --no-cache mysql-client pwgen
copy init.sh disable-remote-root.sql /
copy mysql-init.d /mysql-init.d/

cmd ["/init.sh"]
