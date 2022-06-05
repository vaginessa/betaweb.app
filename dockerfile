FROM archlinux

RUN pacman -Suy --noconfirm
RUN pacman -S --noconfirm python python-pip python-setuptools

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /code

COPY Pipfile Pipfile.lock /code/
RUN pip install pipenv && pipenv install --system
COPY . /code/