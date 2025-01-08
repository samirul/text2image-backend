FROM python:3.12.3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HF_HOME='text2image-model/model/'
EXPOSE 5011
EXPOSE 5012
EXPOSE 5013
EXPOSE 5014
WORKDIR /text2image-app
COPY requirements.txt /text2image-app/
COPY . /text2image-app/
COPY scripts.sh .
RUN python -m venv /virtual-py && \
    /virtual-py/bin/pip install --upgrade pip && \
    apt-get update && \
    /virtual-py/bin/pip install --no-cache-dir -r requirements.txt && \
    adduser --disabled-password text2image-user && \
    chown -R text2image-user:text2image-user /text2image-app && \
    chmod -R 755 /text2image-app && \
    chmod +x scripts.sh


USER text2image-user

CMD ["./scripts.sh"]