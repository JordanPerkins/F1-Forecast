
const Alexa = require('ask-sdk-core');
const {
  getLastResult, getQualifyingLap, getLastQualifyingResult, searchForDriver,
} = require('./util.js');

const logger = require('./logger.js');

const config = require('./config.js')();

const LastWinnerIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'LastWinnerIntent';
  },
  async handle(handlerInput) {
    logger.info('LastWinnerIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getLastResult();
      const { data } = result;
      speakOutput = `${data.results[0].driver_nationality} driver ${data.results[0].driver_forename} \
      ${data.results[0].driver_surname} won the ${data.last_race_year} ${data.last_race_name} grand prix after \
      starting on the grid in <say-as interpret-as="ordinal">${data.results[0].race_grid}</say-as> position, \
      scoring ${data.results[0].race_points} point${data.results[0].race_points === 1 ? '' : 's'}`;
    } catch (e) {
      logger.error(`Error fetching result for LastWinnerIntentHandler: ${e}`);
      speakOutput = 'I was unable to retrieve race result information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

const LastPoleIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'LastPoleIntent';
  },
  async handle(handlerInput) {
    logger.info('LastPoleIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getLastQualifyingResult();
      const { data } = result;
      const lapTime = getQualifyingLap(data.results[0]);
      speakOutput = `${data.results[0].driver_nationality} driver ${data.results[0].driver_forename} \
      ${data.results[0].driver_surname} started on pole position at the ${data.last_race_year} ${data.last_race_name} \
      grand prix after a lap time of ${lapTime}.`;
    } catch (e) {
      logger.error(`Error fetching result for LastPoleIntentHandler: ${e}`);
      speakOutput = 'I was unable to retrieve race result information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

const LastRacePositionIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'LastRacePositionIntent';
  },
  async handle(handlerInput) {
    logger.info('LastRacePositionIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getLastResult();
      const searchedResult = searchForDriver(result.data.results, handlerInput);
      if (!searchedResult) {
        speakOutput = `I coud not find the driver you requested. Try using the driver number instead.
                For example, where did 44 finish at the last race`;
      } else {
        speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} \
        ${searchedResult.driver_surname} finished in <say-as interpret-as="ordinal">${searchedResult.race_position}</say-as> \
        at the ${result.data.last_race_year} ${result.data.last_race_name} grand prix, scoring \
        ${searchedResult.race_points} point${searchedResult.race_points === 1 ? '' : 's'}.`;
      }
    } catch (e) {
      logger.error(`Error fetching result for LastRacePositionIntentHandler: ${e}`);
      speakOutput = 'I was unable to retrieve race result information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

const LastQualifyingPositionIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'QualifyingPositionIntent';
  },
  async handle(handlerInput) {
    logger.info('LastQualifyingPositionIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getLastQualifyingResult();
      const searchedResult = searchForDriver(result.data.results, handlerInput);
      if (!searchedResult) {
        speakOutput = `I coud not find the driver you requested. Try using the driver number instead.
                For example, where did 44 qualify at the last race`;
      } else {
        const lapTime = getQualifyingLap(searchedResult);
        speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} \
        ${searchedResult.driver_surname} qualified in \
        <say-as interpret-as="ordinal">${searchedResult.qualifying_position}</say-as> at the ${result.data.last_race_year} \
        ${result.data.last_race_name} grand prix, with a lap time of ${lapTime}`;
      }
    } catch (e) {
      logger.error(`Error fetching result for LastRacePositionIntentHandler: ${e}`);
      speakOutput = 'I was unable to retrieve race result information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

const GetFullRaceResultIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetFullRaceResultIntent';
  },
  async handle(handlerInput) {
    logger.info('GetFullRaceResultIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getLastResult();
      const { data } = result;
      speakOutput = `Here are the full results of the ${data.last_race_year} ${data.last_race_name} grand prix. `;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < data.results.length) {
          speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>\
          <say-as interpret-as="ordinal">${i + 1}</say-as> ${data.results[i].driver_forename} \
          ${data.results[i].driver_surname}</amazon:emotion>`;
        }
      }
      if (config.listMax < data.results.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = data.results;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for GetFullRaceResultIntentHandlerHandler: ${e}`);
      speakOutput = 'I was unable to retrieve race result information at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

const GetFullQualifyingResultIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetFullQualifyingResultIntent';
  },
  async handle(handlerInput) {
    logger.info('GetFullQualifyingResultIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getLastQualifyingResult();
      const { data } = result;
      speakOutput = `Here are the full results of the ${data.last_race_year} ${data.last_race_name} grand prix \
      qualifying session. `;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < data.results.length) {
          speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${data.results[i].driver_forename} ${data.results[i].driver_surname}</amazon:emotion>`;
        }
      }
      if (config.listMax < data.results.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = data.results;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for GetFullQualifyingResultIntentHandler: ${e}`);
      speakOutput = 'I was unable to retrieve race result information at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

module.exports = [
  LastWinnerIntentHandler,
  LastPoleIntentHandler,
  LastRacePositionIntentHandler,
  LastQualifyingPositionIntentHandler,
  GetFullRaceResultIntentHandler,
  GetFullQualifyingResultIntentHandler,
];
