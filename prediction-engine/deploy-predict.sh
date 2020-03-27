mv predict/Dockerfile .
mv predict/.elasticbeanstalk .
eb deploy $1
mv Dockerfile predict
mv .elasticbeanstalk predict
