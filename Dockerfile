FROM python:3
MAINTAINER Eduardo <eduardo.becerril@umb.mx>

ENV PYTHONUNBUFFERED 1

COPY static/ /siget-vol/static

RUN mkdir -p /siget-app/src

COPY templates/ /siget-app/src/templates

COPY *.py /siget-app/src/
COPY requirements.txt /siget-app/src

WORKDIR /siget-app/src
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "server.py"]