
const Alexa = require('ask-sdk-core');
const {
  getCalendar, getNextRace, formatRaceDate, getRemainingRaces, searchForRace,
} = require('./util.js');

const logger = require('./logger.js');
const config = require('./config.js')();

/**
 * The intent handler for retrieving the details of the next grand prix.
 * It fetches the full calendar from the backend, and then gets the next
 * race using the is_next_race flag inside the structure.
 */
const GetNextRaceIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetNextRaceIntent';
  },
  async handle(handlerInput) {
    logger.info('GetNextRaceIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getCalendar();
      const nextRace = getNextRace(result.data);
      const formattedDate = formatRaceDate(nextRace.race_date);
      speakOutput = `The next Grand Prix, which is the <say-as interpret-as="ordinal">${nextRace.race_round}</say-as> ` +
      `round of the championship, is the ${nextRace.race_name} at the ${nextRace.circuit_name} on ` +
      `<say-as interpret-as="date">${formattedDate}</say-as>, starting at ${nextRace.race_time} GMT.`;
    } catch (e) {
      logger.error(`Error fetching result for GetNextRaceIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the race calendar at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * The intent handler for the full calendar. It gets it from the backend, and filters out
 * races that have already happened, using the round number. It then speaks the results 
 * one by one, using attributes to allow prompting for continuation.
 */
const GetFullCalendarIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetFullCalendarIntent';
  },
  async handle(handlerInput) {
    logger.info('GetFullCalendarIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getCalendar();
      const filteredRaces = getRemainingRaces(result.data);
      speakOutput = `Here is the full race calendar for the ${result.data.year} season. `;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < filteredRaces.length) {
          const formattedDate = formatRaceDate(filteredRaces[i].race_date);
          speakOutput += ('<amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round ' +
          `${filteredRaces[i].race_round}. The ${filteredRaces[i].race_name} on ` +
          `<say-as interpret-as="date">${formattedDate}</say-as> </amazon:emotion>`);
        }
      }
      if (config.listMax < filteredRaces.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = filteredRaces;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for GetFullCalendarIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the race calendar at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

/**
 * The intent for searching for the race requested by the user as a Slot value.
 * The full calendar is retrieved, and a function which searches based on
 * Levenshtein distance is used to try and find a relevant result.
 */
const CalendarRaceIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'CalendarRaceIntent';
  },
  async handle(handlerInput) {
    logger.info('CalendarRaceIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getCalendar();
      const searchedRace = searchForRace(result.data.calendar, handlerInput);
      if (!searchedRace) {
        speakOutput = 'I could not find the race you requested. You can use the race name, ' +
        'circuit name, circuit location or circuit country.';
      } else {
        const formattedDate = formatRaceDate(searchedRace.race_date);
        if (searchedRace.race_round < result.data.next_race_round) {
          speakOutput = `The ${searchedRace.race_name}, which was the ` +
          `<say-as interpret-as="ordinal">${searchedRace.race_round}</say-as> round of the championship, took ` +
          `place at ${searchedRace.circuit_name} on <say-as interpret-as="date">${formattedDate}</say-as>`;
        } else {
          speakOutput = `The ${searchedRace.race_name}, which is the ` +
          `<say-as interpret-as="ordinal">${searchedRace.race_round}</say-as> round of the championship, will ` +
          `take place at ${searchedRace.circuit_name} on <say-as interpret-as="date">${formattedDate}</say-as>, ` +
          `starting at ${searchedRace.race_time} GMT.`;
        }
      }
    } catch (e) {
      logger.error(`Error fetching result for CalendarRaceIntent: ${e}`);
      speakOutput = 'I was unable to get the race calendar at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};


module.exports = [
  GetNextRaceIntentHandler,
  GetFullCalendarIntentHandler,
  CalendarRaceIntentHandler,
];
