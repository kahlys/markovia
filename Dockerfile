FROM python

ADD main.py /
ADD config.json / 

RUN pip install tweepy schedule

CMD [ "python", "-u", "./main.py" ]