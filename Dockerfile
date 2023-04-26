# base-line image
FROM python:3.10.11

# copy file
COPY . /Users/dangchan/Desktop/Github/flask_practice/

# set workdir
WORKDIR /Users/dangchan/Desktop/Github/flask_practice/

# install requirements
RUN pip install -r requirements.txt

# expose
EXPOSE 5000

# environment variables
ENV FLASK_APP pybo

# command
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]