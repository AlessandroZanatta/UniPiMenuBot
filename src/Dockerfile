FROM python:3-alpine

# Copy requirements
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

# Create working directory for bot
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
COPY . ./

# Start bot
CMD ["python", "bot.py"]