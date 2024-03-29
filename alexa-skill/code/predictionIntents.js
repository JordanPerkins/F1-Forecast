
const Alexa = require('ask-sdk-core');
const { getRacePrediction, getQualifyingPrediction, searchForDriver } = require('./util.js');

const logger = require('./logger.js');

const config = require('./config.js')();

/**
 * The intent for handling the prediction of the race winner. It calls the
 * prediction endpoint on the backend, and takes the first result in the
 * provided ranking, speaking it to the user.
 */
const PredictWinnerIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictWinnerIntent';
  },
  async handle(handlerInput) {
    logger.info('PredictWinnerIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getRacePrediction();
      const { data } = result;
      speakOutput = `The predicted winner of the ${data.year} ${data.name} grand prix is ` +
      `${data.result[0].driver_nationality} driver ${data.result[0].driver_forename} ${data.result[0].driver_surname}`;
    } catch (e) {
      logger.error(`Error fetching result for PredictWinnerIntent: ${e}`);
      speakOutput = 'I was unable to make a race prediction at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * The intent for handling the prediction of the qualifying polesitter. It calls the
 * prediction endpoint on the backend, and takes the first result in the provided
 * ranking, speaking it to the user.
 */
const PredictQualifyingIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictQualifyingIntent';
  },
  async handle(handlerInput) {
    logger.info('PredictQualifyingIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getQualifyingPrediction();
      const { data } = result;
      speakOutput = `The driver on pole position at the ${data.year} ${data.name} grand prix is predicted to be ` +
     `${data.result[0].driver_nationality} driver ${data.result[0].driver_forename} ${data.result[0].driver_surname}`;
    } catch (e) {
      logger.error(`Error fetching result for PredictQualifyingIntent: ${e}`);
      speakOutput = 'I was unable to make a qualifying prediction at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * The intent for returning the predicted position of the driver specified in the slot.
 * It calls the prediction endpoint to get the full results, then uses a Levenshtein
 * distance based search to try and find the specified driver.
 */
const PredictRacePositionIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictRacePositionIntent';
  },
  async handle(handlerInput) {
    logger.info('PredictRacePositionIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getRacePrediction();
      const searchedResult = searchForDriver(result.data.result, handlerInput);
      if (!searchedResult) {
        speakOutput = 'I could not find the driver you requested. Try using the driver number instead. ' +
        'For example, where will 44 finish at the next race';
      } else {
        speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} ` +
        `${searchedResult.driver_surname} is predicted to finish in ` +
        `<say-as interpret-as="ordinal">${searchedResult.position}</say-as> at the ${result.data.year} ` +
        `${result.data.name} grand prix`;
      }
    } catch (e) {
      logger.error(`Error fetching result for PredictRacePositionIntent: ${e}`);
      speakOutput = 'I was unable to make a race prediction at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * The intent for returning the predicted qualifying position of the driver
 * specified in the slot. It calls the prediction endpoint to get the full results,
 * then uses a Levenshtein distance based search to try and find the specified driver.
 */
const PredictQualifyingPositionIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictQualifyingPositionIntent';
  },
  async handle(handlerInput) {
    logger.info('PredictQualifyingPositionIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getQualifyingPrediction();
      const searchedResult = searchForDriver(result.data.result, handlerInput);
      if (!searchedResult) {
        speakOutput = 'I could not find the driver you requested. Try using the driver number instead. ' +
        'For example, where will 44 qualify at the next race';
      } else {
        speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} ` +
        `${searchedResult.driver_surname} is predicted to qualify in ` +
        `<say-as interpret-as="ordinal">${searchedResult.position}</say-as> at the ${result.data.year} ` +
        `${result.data.name} grand prix`;
        if (searchedResult.driver_quali_result) {
          speakOutput += ` with a lap time ${searchedResult.driver_quali_result} seconds away from pole position`;
        }
      }
    } catch (e) {
      logger.error(`Error fetching result for PredictQualifyingPositionIntent: ${e}`);
      speakOutput = 'I was unable to make a qualifying prediction at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * Reads the full race prediction by retrieving it from the backend, and
 * returning the results one by one, saving the result in the attributes to
 * prompt for continuation which is handled by the YesIntent.
 */
const ReadRaceForecastIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ReadRaceForecastIntent';
  },
  async handle(handlerInput) {
    logger.info('ReadRaceForecastIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getRacePrediction();
      const { data } = result;
      if (data.result.length === 0) {
        throw Error('Result was empty');
      }

      speakOutput = `Here is the race prediction forecast for the ${data.year} ${data.name} grand prix.`;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < data.result.length) {
          speakOutput += '<amazon:emotion name="excited" intensity="medium"><break time="1s"/>' +
          `<say-as interpret-as="ordinal">${i + 1}</say-as> ${data.result[i].driver_forename} ` + 
          `${data.result[i].driver_surname} </amazon:emotion>`;
        }
      }
      if (config.listMax < data.result.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = data.result;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for ReadRaceForecastIntent: ${e}`);
      speakOutput = 'I was unable to make a race prediction at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

/**
 * Reads the full qualifying prediction by retrieving it from the backend, and
 * returning the results one by one, saving the result in the attributes to
 * prompt for continuation which is handled by the YesIntent.
 */
const ReadQualifyingForecastIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ReadQualifyingForecastIntent';
  },
  async handle(handlerInput) {
    logger.info('ReadQualifyingForecastIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getQualifyingPrediction();
      const { data } = result;
      if (data.result.length === 0) {
        throw Error('Result was empty');
      }

      speakOutput = `Here is the qualifying prediction forecast for the ${data.year} ${data.name} grand prix.`;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < data.result.length) {
          speakOutput += '<amazon:emotion name="excited" intensity="medium"><break time="1s"/>' +
          `<say-as interpret-as="ordinal">${i + 1}</say-as> ${data.result[i].driver_forename} ` +
          `${data.result[i].driver_surname} </amazon:emotion>`;
        }
      }
      if (config.listMax < data.result.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = data.result;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for ReadQualifyingForecastIntent: ${e}`);
      speakOutput = 'I was unable to make a qualifying prediction at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

module.exports = [
  PredictWinnerIntentHandler,
  PredictQualifyingIntentHandler,
  PredictRacePositionIntentHandler,
  PredictQualifyingPositionIntentHandler,
  ReadRaceForecastIntentHandler,
  ReadQualifyingForecastIntentHandler,
];
