mv predict/Dockerfile .
mv predict/.elasticbeanstalk .
eb deploy dev2
mv Dockerfile predict
mv .elasticbeanstalk predict