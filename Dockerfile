FROM python:3-alpine

ARG SECRET_KEY
ARG ALLOWED_HOSTS=127.0.0.1,localhost

WORKDIR /app/polls

ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=True
ENV TIMEZONE=Asia/Bangkok
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS:-127.0.0.1,localhost}


COPY ./requirements.txt .
# Install dependencies in Docker container
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Running Django functions in here is not good!
# Apply Migrations
#RUN python ./manage.py migrate
#
## Apply fixtures
#RUN python ./manage.py loaddata data/polls-v4.json
#RUN python ./manage.py loaddata data/users.json
#RUN python ./manage.py loaddata data/votes-v4.json

# Apply fixtures
#RUN python ./manage.py createsuperuser --username admin1 --email admin@example.com --noinput
COPY ./entrypoint.sh .


EXPOSE 8000
RUN chmod +x ./entrypoint.sh
# Run application
#CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]


CMD [ "./entrypoint.sh" ]
#+CMD python ./manage.py migrate ; python ./manage.py runserver 0.0.0.0:8000