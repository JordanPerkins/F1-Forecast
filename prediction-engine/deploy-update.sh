mv update/Dockerfile .
mv update/.elasticbeanstalk .
mv update/cron.yaml .
eb deploy $1
mv Dockerfile update
mv .elasticbeanstalk update
mv cron.yaml update
