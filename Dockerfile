FROM tiangolo/uwsgi-nginx-flask:python3.7
COPY ./app /app
COPY mdash.py /
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["../mdash.py"]