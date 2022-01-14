FROM python:alpine
RUN apk add --no-cache tini

ADD metrics.py /metrics.py
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python" , "/metrics.py"]