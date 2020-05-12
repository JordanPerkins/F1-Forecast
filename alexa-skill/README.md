# alexa-skill

This folder contains the Node.js Alexa Skill Handler. In this folder, you will find:

* code - The AWS Lambda function
* infrastructure - Deployment configuration
* skill-package - Contains the interactionModels and the publishing assets
* tests - The Mocha Unit Tests

## To run the unit tests:
    * Run npm install
    * Set the environment variables found in tests.env
    * Run npm test

## To deploy:
    * Install ask-cli (npm install -g ask-cli)
    * Configure with ask configure
    * Deploy with ask deploy
