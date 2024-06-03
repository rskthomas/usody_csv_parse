FROM tiangolo/uwsgi-nginx-flask:python3.8


WORKDIR /app

COPY requirements.txt requirements.txt
# Install the required dependencies
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
