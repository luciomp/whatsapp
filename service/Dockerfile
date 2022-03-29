FROM python:3.10.4-slim-buster
WORKDIR /app
COPY src/ /app
RUN pip3 install -r requirements.txt
# CMD ["ls", "-la"]
CMD ["python", "main.py", "8080"]
EXPOSE 8080