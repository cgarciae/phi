FROM python:2.7

RUN apt-get update
RUN apt-get -y install git

RUN pip install pdoc
RUN pip install mako
RUN pip install markdown
RUN pip install decorator>=4.0.9
RUN pip install pytest
RUN pip install pytest-sugar
RUN pip install fn
