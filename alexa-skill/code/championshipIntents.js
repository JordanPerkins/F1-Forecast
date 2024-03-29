
const Alexa = require('ask-sdk-core');
const {
  getDriversChampionship,
  getConstructorsChampionship,
  searchForDriver,
  searchForConstructor,
  validateYear,
} = require('./util.js');

const logger = require('./logger.js');
const config = require('./config.js')();

/**
 * The intent for retrieving the current championship leaders. It calls the backend in parallel
 * for both results, and then returns the top (leading) result.
 */
const ChampionshipLeaderIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ChampionshipLeaderIntent';
  },
  async handle(handlerInput) {
    logger.info('ChampionshipLeaderIntentHandler has been invoked');
    let speakOutput;
    try {
      const [driversResult, constructorsResult] = await Promise.all([
        getDriversChampionship(),
        getConstructorsChampionship(),
      ]);
      if (!driversResult.data.standings || !driversResult.data.standings.length === 0) {
        throw Error('Drivers standings were empty');
      }

      if (!constructorsResult.data.standings || !constructorsResult.data.standings.length === 0) {
        throw Error('Constructors standings were empty');
      }

      const driversLeader = driversResult.data.standings[0];
      const constructorsLeader = constructorsResult.data.standings[0];

      speakOutput = `The driver's championship is currently led by ${driversLeader.driver_nationality} driver ` +
      `${driversLeader.driver_forename} ${driversLeader.driver_surname} with ${driversLeader.driver_points} ` +
      `point${driversLeader.driver_points === 1 ? '' : 's'} and ${driversLeader.driver_wins} ` +
      `win${driversLeader.driver_wins === 1 ? '' : 's'}. `;

      speakOutput += `The constructor's championship is currently led by ${constructorsLeader.constructor_nationality} ` +
      `constructor ${constructorsLeader.constructor_name} with ${constructorsLeader.constructor_points} ` +
      `point${constructorsLeader.constructor_points === 1 ? '' : 's'} and ${constructorsLeader.constructor_wins} ` +
      `win${constructorsLeader.constructor_wins === 1 ? '' : 's'}.`;
    } catch (e) {
      logger.error(`Error fetching result for ChampionshipLeaderIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the championship information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * Intent for retrieving the championship position of the driver given in the slot value.
 * It calls the backend for the driver's championship, and then searches based on a
 * Levenshtein distance.
 */
const ChampionshipDriverIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ChampionshipDriverIntent';
  },
  async handle(handlerInput) {
    logger.info('ChampionshipDriverIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getDriversChampionship();
      const searchedResult = searchForDriver(result.data.standings, handlerInput);
      if (!searchedResult) {
        speakOutput = 'I could not find the driver you requested. Try using the driver number instead. ' +
        'For example, where is 44 in the standings';
      } else {
        speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} ` +
        `${searchedResult.driver_surname} is currently ` +
        `<say-as interpret-as="ordinal">${searchedResult.driver_position}</say-as> in the championship, with ` +
        `${searchedResult.driver_points} point${searchedResult.driver_points === 1 ? '' : 's'} and ` +
        `${searchedResult.driver_wins} win${searchedResult.driver_wins === 1 ? '' : 's'}`;
      }
    } catch (e) {
      logger.error(`Error fetching result for ChampionshipDriverIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the championship information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * Intent for retrieving the championship position of the constructor given in the slot value.
 * It calls the backend for the constructor's championship, and then searches based on a
 * Levenhstein distance.
 */
const ChampionshipConstructorIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ChampionshipConstructorIntent';
  },
  async handle(handlerInput) {
    logger.info('ChampionshipConstructorIntentHandler has been invoked');
    let speakOutput;
    try {
      const result = await getConstructorsChampionship();
      const searchedResult = searchForConstructor(result.data.standings, handlerInput);
      if (!searchedResult) {
        speakOutput = 'I could not find the constructor you requested. You can get a full championship breakdown '
        + 'by asking f. one forecast for the full constructors standings.';
      } else {
        speakOutput = `${searchedResult.constructor_nationality} constructor ${searchedResult.constructor_name} is ` +
        `currently <say-as interpret-as="ordinal">${searchedResult.constructor_position}</say-as> in the championship, ` +
        `with ${searchedResult.constructor_points} point${searchedResult.constructor_points === 1 ? '' : 's'} and ` +
        `${searchedResult.constructor_wins} win${searchedResult.constructor_wins === 1 ? '' : 's'}`;
      }
    } catch (e) {
      logger.error(`Error fetching result for ChampionshipConstructorIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the championship information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * Intent for returning the full result's of the drivers championship. It gets the full
 * result from the backend, and then speaks it one by one, saving the result as an attribute
 * so we can prompt for continuation, handled by YesIntent.
 */
const FullChampionshipDriverIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'FullChampionshipDriverIntent';
  },
  async handle(handlerInput) {
    logger.info('FullChampionshipDriverIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getDriversChampionship();
      const { data } = result;
      if (data.standings.length === 0) {
        throw Error('Result was empty');
      }

      speakOutput = `Here are the full drivers standings for the ${data.last_race_year} season. `;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < data.standings.length) {
          speakOutput += '<amazon:emotion name="excited" intensity="medium"><break time="1s"/>' +
          `<say-as interpret-as="ordinal">${i + 1}</say-as> ${data.standings[i].driver_forename} ` +
          `${data.standings[i].driver_surname} with ${data.standings[i].driver_points} ` +
          `point${data.standings[i].driver_points === 1 ? '' : 's'}. </amazon:emotion>`;
        }
      }
      if (config.listMax < data.standings.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = data.standings;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for FullChampionshipDriverIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the championship information at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

/**
 * Intent for returning the full result's of the constructors championship. It gets the full
 * result from the backend, and then speaks it one by one, saving the result as an attribute
 * so we can prompt for continuation, handled by YesIntent.
 */
const FullChampionshipConstructorsIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'FullChampionshipConstructorsIntent';
  },
  async handle(handlerInput) {
    logger.info('FullChampionshipConstructorsIntentHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
    let speakOutput;
    try {
      const result = await getConstructorsChampionship();
      const { data } = result;
      if (data.standings.length === 0) {
        throw Error('Result was empty');
      }

      speakOutput = `Here are the full constructors standings for the ${data.last_race_year} season. `;
      for (let i = 0; i < config.listMax; i += 1) {
        if (i < data.standings.length) {
          speakOutput += '<amazon:emotion name="excited" intensity="medium"><break time="1s"/>' +
          `<say-as interpret-as="ordinal">${i + 1}</say-as> ${data.standings[i].constructor_name} with ` +
          `${data.standings[i].constructor_points} point${data.standings[i].constructor_points === 1 ? '' : 's'}. ` +
          '</amazon:emotion>';
        }
      }
      if (config.listMax < data.standings.length) {
        speakOutput += '<break time="1s"/>Would you like me to continue?';
        attributes.lastPosition = config.listMax;
        attributes.lastResult = data.standings;
        return handlerInput.responseBuilder
          .speak(speakOutput)
          .reprompt('Would you like me to continue?')
          .getResponse();
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for FullChampionshipConstructorIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the championship information at this time. Please check back later';
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    }
  },
};

/**
 * Intent for returning the world champion in a season given by the slot. It fetches the
 * result from the backend, using the year as a parameter in the request URL and then
 * speaks out the result.
 */
const WorldChampionIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'WorldChampionIntent';
  },
  async handle(handlerInput) {
    logger.info('WorldChampionIntentHandler has been invoked');
    let speakOutput;
    try {
      const year = validateYear(handlerInput);
      if (!year) {
        speakOutput = 'Please provide a valid season year. For example, who was world champion in 2009';
      } else {
        const [driversResult, constructorsResult] = await Promise.all([
          getDriversChampionship(year),
          getConstructorsChampionship(year),
        ]);
        if (!driversResult.data.standings.length || !constructorsResult.data.standings.length) {
          speakOutput = 'Please provide a valid season year. For example, who was world champion in 2009';
        } else {
          speakOutput = `The driver's world champion in ${year} was ` +
          `${driversResult.data.standings[0].driver_nationality} driver ${driversResult.data.standings[0].driver_forename} ` +
          `${driversResult.data.standings[0].driver_surname} with ${driversResult.data.standings[0].driver_points} ` +
          `point${driversResult.data.standings[0].driver_points === 1 ? '' : 's'} and ` +
          `${driversResult.data.standings[0].driver_wins} win${driversResult.data.standings[0].driver_wins === 1 ? '' : 's'}. ` +
          `The constructor's world champion was ${constructorsResult.data.standings[0].constructor_nationality} constructor ` +
          `${constructorsResult.data.standings[0].constructor_name} with ` +
          `${constructorsResult.data.standings[0].constructor_points} ` +
          `point${constructorsResult.data.standings[0].constructor_points === 1 ? '' : 's'} and ` +
          `${constructorsResult.data.standings[0].constructor_wins} ` +
          `win${constructorsResult.data.standings[0].constructor_wins === 1 ? '' : 's'}.`;
        }
      }
      return handlerInput.responseBuilder
        .speak(speakOutput)
        .getResponse();
    } catch (e) {
      logger.error(`Error fetching result for WorldChampionIntentHandler: ${e}`);
      speakOutput = 'I was unable to get the championship information at this time. Please check back later';
    }
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};


module.exports = [
  ChampionshipLeaderIntentHandler,
  ChampionshipDriverIntentHandler,
  ChampionshipConstructorIntentHandler,
  FullChampionshipDriverIntentHandler,
  FullChampionshipConstructorsIntentHandler,
  WorldChampionIntentHandler,
];
