const AWS = require('aws-sdk');
const axios = require('axios');
const levenshtein = require('js-levenshtein');

const s3SigV4Client = new AWS.S3({
    signatureVersion: 'v4'
});

LEVENSHTEIN_THRESHOLD = 4

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

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+'/predict/race');

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

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+'/predict/qualifying');

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

    console.info(`Received slot value of ${value}`);

    if (!result.result || result.result.length === 0) {
        return null;
    }

    const valueAsNum = Number.parseInt(value, 10);
    const drivers = result.result.map((driver, index) => {
            let distanceValue = null;
            if (Number.isNaN(valueAsNum)) {
                valueSplit = value.split(' ');
                if (valueSplit.length === 2) {
                    distanceValue = Math.min(
                        levenshtein(driver.driver_forename.toLowerCase(), valueSplit[0].toLowerCase()),
                        levenshtein(driver.driver_surname.toLowerCase(), valueSplit[1].toLowerCase())
                    );
                } else {
                    distanceValue = Math.min(
                        levenshtein(driver.driver_forename.toLowerCase(), value.toLowerCase()),
                        levenshtein(driver.driver_surname.toLowerCase(), value.toLowerCase())
                    );
                }
            }
            return {
                ...driver,
                position: index + 1,
                distanceValue
            }
        })
        .filter(driver => {
            if (Number.isNaN(valueAsNum)) {
                return driver.distanceValue <= LEVENSHTEIN_THRESHOLD;
            }
            return driver.driver_num === valueAsNum;
        })
        .sort((driver1, driver2) => driver1.distanceValue - driver2.distanceValue);

    if (drivers.length === 1 || (drivers.length > 0 && (drivers[0].distanceValue !== null) && (drivers[0].distanceValue < drivers[1].distanceValue))) {
        return drivers[0];
    }

    return null;
}

