
const Alexa = require('ask-sdk-core');

const { formatRaceDate } = require('./util.js');

const logger = require('./logger.js');
const config = require('./config.js')();

const NoIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.NoIntent');
  },
  handle(handlerInput) {
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastPosition = undefined;
    attributes.lastResult = undefined;
    attributes.lastIntent = undefined;
    const speakOutput = 'Ok. I will stop now. See you later!';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

const YesIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.YesIntent';
  },
  async handle(handlerInput) {
    let speakOutput = '';
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    try {
      if (!attributes.lastPosition || !attributes.lastResult || !attributes.lastIntent) {
        throw Error('There are no attributes present in the request.');
      }

      const { lastPosition, lastResult, lastIntent } = attributes;

      logger.info(`Yes received for ${lastIntent}: Last position is ${lastPosition}`);
      for (let i = lastPosition; i < lastPosition + config.listMax; i += 1) {
        if (i < lastResult.length) {
          if (lastIntent === 'ReadRaceForecastIntent'
             || lastIntent === 'ReadQualifyingForecastIntent'
             || lastIntent === 'GetFullRaceResultIntent'
             || lastIntent === 'GetFullQualifyingResultIntent') {
            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>\
            <say-as interpret-as="ordinal">${i + 1}</say-as> ${lastResult[i].driver_forename} \
            ${lastResult[i].driver_surname} </amazon:emotion>`;
          } else if (lastIntent === 'GetFullCalendarIntent') {
            const formattedDate = formatRaceDate(lastResult[i].race_date);
            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round \
            ${lastResult[i].race_round}. The ${lastResult[i].race_name} on \
            <say-as interpret-as="date">${formattedDate}</say-as> </amazon:emotion>`;
          } else if (lastIntent === 'FullChampionshipDriverIntent') {
            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>\
            <say-as interpret-as="ordinal">${i + 1}</say-as> ${lastResult[i].driver_forename} \
            ${lastResult[i].driver_surname} with ${lastResult[i].driver_points} \
            point${lastResult[i].driver_points === 1 ? '' : 's'}.</amazon:emotion>`;
          } else if (lastIntent === 'FullChampionshipConstructorsIntent') {
            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>\
            <say-as interpret-as="ordinal">${i + 1}</say-as> ${lastResult[i].constructor_name} with \
            ${lastResult[i].constructor_points} \
            point${lastResult[i].constructor_points === 1 ? '' : 's'}.</amazon:emotion>`;
          }
        }
      }

      if (lastPosition + config.listMax < lastResult.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition += config.listMax;
        attributes.lastResult = lastResult;
        attributes.lastIntent = lastIntent;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('<break time="1s"/>Would you like me to continue?')
          .getResponse();
      }

      speakOutput += '<break time="1s"/>Summary concluded';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for YesIntent: ${e}`);
      speakOutput = 'I was unable to carry out the requested action. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

module.exports = [
  NoIntentHandler,
  YesIntentHandler,
];
