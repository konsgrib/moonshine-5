# Dockerfile
FROM python:3.11-slim-buster

WORKDIR /app

COPY ./tests/requirements.txt ./

COPY ./tests/RPi.GPIO.py ./

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN python -c "import site; print(site.getsitepackages()[0])" > site_packages.txt

RUN pwd

RUN ls -lA

RUN cat site_packages.txt | xargs -I {} cp ./RPi.GPIO.py {}/RPi.GPIO.py

ENV PYTHONPATH /app:$PYTHONPATH

COPY . .

RUN whereis python

CMD ["pytest", "-vvs", "tests.py"]