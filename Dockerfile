FROM python:3.12.3-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME='/vol/model/text2image-model'
WORKDIR /text2image-app
COPY requirements.txt /text2image-app/
COPY . /text2image-app/
RUN python -m venv /virtual-py && \
    /virtual-py/bin/pip install --upgrade pip && \
    apt-get update && \
    /virtual-py/bin/pip install --no-cache-dir -r requirements.txt && \
    adduser --disabled-password text2image-user && \
    mkdir -p /vol/model && \
    mkdir -p /vol/images && \
    chown -R text2image-user:text2image-user /vol && \
    chmod -R 755 /vol

USER text2image-user