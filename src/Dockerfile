FROM python:3-alpine

COPY requirements.txt /requirements.txt
RUN apk add --no-cache --virtual .build-deps \
    build-base \
    python3-dev \
    && pip install -r requirements.txt \
    && apk del --no-cache .build-deps

# Create working directory for bot
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
COPY . ./

# Start bot
CMD ["python", "bot.py"]