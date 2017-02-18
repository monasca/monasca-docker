from alpine:3.5

run apk add --no-cache mysql-client pwgen py2-jinja2
copy init.sh template.py disable-remote-root.sql /
copy mysql-init.d /mysql-init.d/

cmd ["/init.sh"]
