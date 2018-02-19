from alpine:3.6

copy requirements.txt /requirements.txt

run apk add --no-cache python3 py3-yaml git && \
    pip3 install -r requirements.txt

add cleanup.py /

cmd ["python3", "/cleanup.py"]
