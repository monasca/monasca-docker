from alpine:3.5

run apk add --no-cache python py2-pip && pip install httpie 
copy init.sh /init.sh

cmd ["/init.sh"]
