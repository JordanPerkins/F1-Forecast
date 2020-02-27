mv update/Dockerfile .
mv update/elasticbeanstalk .
eb deploy dev2
mv Dockerfile update
mv .elasticbeanstalk update