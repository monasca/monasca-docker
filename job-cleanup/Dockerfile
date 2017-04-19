from alpine:3.5

arg KUBERNETES_CLIENT_VERSION=2.0.0a1

run apk add --no-cache py2-requests py2-pip && \
    pip install kubernetes=="$KUBERNETES_CLIENT_VERSION"

add cleanup.py /

cmd ["python", "/cleanup.py"]
