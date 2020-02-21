FROM python:3.6

LABEL maintainer="Jordan Perkins <jordan@perkins.pw>"

COPY ./ ./app
WORKDIR ./app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD ["python", "-m prediction-engine.predict.app"]