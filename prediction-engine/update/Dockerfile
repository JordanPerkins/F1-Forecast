FROM python:3.6

LABEL maintainer="Jordan Perkins <jordan@perkins.pw>"

COPY ./ ./prediction-engine
WORKDIR ./prediction-engine

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
WORKDIR ../

CMD ["python", "-m", "prediction-engine.update.pywsgi"]