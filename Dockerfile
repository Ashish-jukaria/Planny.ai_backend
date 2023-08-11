FROM python:3.8-slim
RUN apt-get update
RUN apt install -y \
    postgresql 
RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .