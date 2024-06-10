# Загрузка базового образа ubuntu 22.04
FROM ubuntu:22.04

# LABEL о пользовательском образе
LABEL maintainer="organismus22@gmail.com"
LABEL version="1.0"
LABEL description="docker agent for jenkins"

# Отключение подсказки при установке пакетов
ARG DEBIAN_FRONTEND=noninteractive

# Обновление репозитория ПО Ubuntu
RUN apt update

RUN apt-get update && apt-get install -y \
  git \
  subversion \
  make \
  vim \
  mc \
  python3 \
  python3-venv \
  python3-pip \
  flex \
  gawk \
  zip \
  bison

# Запуск Jenkins
RUN useradd -ms /bin/bash Jenkins

USER Jenkins
WORKDIR /home/Jenkins
