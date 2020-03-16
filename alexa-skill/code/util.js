const AWS = require('aws-sdk');
const axios = require('axios');
const levenshtein = require('js-levenshtein');

const s3SigV4Client = new AWS.S3({
    signatureVersion: 'v4'
});

LEVENSHTEIN_THRESHOLD = 2

module.exports.getS3PreSignedUrl = function getS3PreSignedUrl(s3ObjectKey) {

    const bucketName = process.env.S3_PERSISTENCE_BUCKET;
    const s3PreSignedUrl = s3SigV4Client.getSignedUrl('getObject', {
        Bucket: bucketName,
        Key: s3ObjectKey,
        Expires: 60*1 // the Expires is capped for 1 minute
    });
    console.log(`Util.s3PreSignedUrl: ${s3ObjectKey} URL ${s3PreSignedUrl}`);
    return s3PreSignedUrl;
}

module.exports.getRacePrediction = async () => {
    if (!process.env.PREDICTION_ENDPOINT) {
        throw Error('Prediction endpoint missing - disabled predictions');
    }

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+'/race');

    if (result.status !== 200) {
        throw Error(`Did not receive status 200 from race prediction request: ${result.status}`);
    }

    if (!result.data || typeof result.data !== 'object') {
        throw Error('Did not receive data object');
    }

    return result;
}

module.exports.getQualifyingPrediction = async () => {
    if (!process.env.PREDICTION_ENDPOINT) {
        throw Error('Prediction endpoint missing - disabled predictions');
    }

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+'/qualifying');

    if (result.status !== 200) {
        throw Error(`Did not receive status 200 from qualifying prediction request: ${result.status}`);
    }

    if (!result.data || typeof result.data !== 'object') {
        throw Error('Did not receive data object');
    }

    return result;
}

module.exports.searchForDriver = (result, handlerInput) => {
    if (!handlerInput.requestEnvelope || !handlerInput.requestEnvelope.request ||
        !handlerInput.requestEnvelope.request.intent || !handlerInput.requestEnvelope.request.intent.slots ||
        !handlerInput.requestEnvelope.request.intent.slots.Driver ||
        !handlerInput.requestEnvelope.request.intent.slots.Driver.value) {
            return null;
    }

    const value = handlerInput.requestEnvelope.request.intent.slots.Driver.value;

    if (!result.result || result.result.length === 0) {
        return null;
    }

    let drivers;

    const valueAsNum = Number.parseInt(value, 10);
    if (!Number.isNaN(valueAsNum)) {
        drivers = result.result.filter((driver, index) => {
            driver.position = index + 1;
            return driver.driver_num === valueAsNum;
        });
    } else {
        drivers = result.result.filter((driver, index) => {
            driver.position = index + 1;
            valueSplit = value.split(' ');
            if (valueSplit.length === 2) {
                return (levenshtein(driver.driver_forename,valueSplit[0]) <= LEVENSHTEIN_THRESHOLD ||
                levenshtein(driver.driver_surname,valueSplit[1]) <= LEVENSHTEIN_THRESHOLD);
            }
            return (levenshtein(driver.driver_forename,value) <= LEVENSHTEIN_THRESHOLD  ||
            levenshtein(driver.driver_surname,value) <= LEVENSHTEIN_THRESHOLD);
        });
    }
    if (drivers.length !== 1) {
        return null;
    }
    return drivers[0];
}

