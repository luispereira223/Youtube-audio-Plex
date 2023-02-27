FROM python:3.10.6


RUN apt-get update && apt-get install -y ffmpeg
RUN apt-get install -y aria2
RUN echo "y"
RUN mkdir /app
ADD main.py /app

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["main.py"]