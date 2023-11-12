FROM	python:3.12-alpine

COPY    requirements.txt /tmp

RUN	pip install --no-cache-dir -r /tmp/requirements.txt

COPY	unpage.py /

ENTRYPOINT ["/usr/local/bin/python3", "unpage.py"]
