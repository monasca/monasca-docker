from alpine:3.5

arg CLIENT_TARBALL=https://github.com/kubernetes-incubator/client-python/archive/master.zip

run apk add --no-cache py2-requests py2-pip && pip install "$CLIENT_TARBALL"

add cleanup.py /

cmd ["python", "/cleanup.py"]
