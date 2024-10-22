FROM python:3.10-slim


RUN apt-get update && apt-get install -y git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /project

COPY ./requirements.txt ./

RUN python -m pip install --upgrade pip && \
    pip install torch --extra-index-url https://download.pytorch.org/whl/cpu && \
    pip install -r requirements.txt

COPY ./alembic.ini ./
COPY ./migrations ./

COPY ./src ./src/

CMD ["python", "main.py"]