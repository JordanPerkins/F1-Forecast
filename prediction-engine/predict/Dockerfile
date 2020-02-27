FROM python:3.6

LABEL maintainer="Jordan Perkins <jordan@perkins.pw>"

COPY ./ ./prediction-engine
WORKDIR ./prediction-engine

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
WORKDIR ../

CMD ["python", "-m", "prediction-engine.predict.app"]