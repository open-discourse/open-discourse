FROM python

COPY . /srv

WORKDIR /srv/

COPY docker_requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

COPY api.py .

EXPOSE 5400

CMD ["python3", "./api.py"]
