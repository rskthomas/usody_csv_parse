FROM tiangolo/uwsgi-nginx-flask:python3.8

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt file into the container and install the dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Run the app
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]
