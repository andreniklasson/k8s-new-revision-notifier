FROM python:3.9
WORKDIR /srv

COPY deployment-revision-notifier.py .

RUN chmod +x deployment-revision-notifier.py

ENV PYTHONUNBUFFERED=1

RUN pip3 install slack_sdk
RUN pip3 install kubernetes

RUN chown -R 1000:1000 /srv
USER 1000

CMD [ "python3", "deployment-revision-notifier.py" ]