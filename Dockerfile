FROM python:2.7
LABEL maintainer="manuel.bovo@gmail.com"
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install .
EXPOSE 5000
ENV GINDROP_PORT="5000" \
    GINDROP_LOG_LEVEL="info" \
    GINDROP_STOP_TIMEOUT="1"
CMD [ "gindrop" ]