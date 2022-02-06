FROM python:3.9.10-slim-buster

ENV APP_NAME=homesecuritysource
ENV WORK_DIR=/usr/${APP_NAME}

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${WORK_DIR}

COPY . .

RUN python3 -m venv $VIRTUAL_ENV
RUN pip install -r requirements.txt

CMD ["python", "src/main/main.py"]