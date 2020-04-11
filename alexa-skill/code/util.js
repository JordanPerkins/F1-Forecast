
const axios = require('axios');
const levenshtein = require('js-levenshtein');

const config = require('./config.js')();

const logger = require('./logger.js');

module.exports.getRacePrediction = async () => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled predictions');
  }

  const result = await axios.get(`${config.predictionEndpoint}/predict/race`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from race prediction request: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.getQualifyingPrediction = async () => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled predictions');
  }

  const result = await axios.get(`${config.predictionEndpoint}/predict/qualifying`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from qualifying prediction request: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.getCalendar = async () => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled information');
  }

  const result = await axios.get(`${config.predictionEndpoint}/info/calendar`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from calendar request: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.searchForDriver = (result, handlerInput) => {
  if (!handlerInput.requestEnvelope || !handlerInput.requestEnvelope.request
        || !handlerInput.requestEnvelope.request.intent
        || !handlerInput.requestEnvelope.request.intent.slots
        || !handlerInput.requestEnvelope.request.intent.slots.Driver
        || !handlerInput.requestEnvelope.request.intent.slots.Driver.value) {
    return null;
  }

  const { value } = handlerInput.requestEnvelope.request.intent.slots.Driver;

  logger.info(`Received slot value of ${value}`);

  if (!result || result.length === 0) {
    return null;
  }

  const valueAsNum = Number.parseInt(value, 10);
  const drivers = result.map((driver, index) => {
    let distanceValue = null;
    if (Number.isNaN(valueAsNum)) {
      const valueSplit = value.split(' ');
      if (valueSplit.length === 2) {
        distanceValue = Math.min(
          levenshtein(driver.driver_forename.toLowerCase(), valueSplit[0].toLowerCase()),
          levenshtein(driver.driver_surname.toLowerCase(), valueSplit[1].toLowerCase()),
        );
      } else if (valueSplit.length === 1) {
        distanceValue = Math.min(
          levenshtein(driver.driver_forename.toLowerCase(), value.toLowerCase()),
          levenshtein(driver.driver_surname.toLowerCase(), value.toLowerCase()),
        );
      }
    }
    return {
      ...driver,
      position: index + 1,
      distanceValue,
    };
  })
    .filter((driver) => {
      if (Number.isNaN(valueAsNum)) {
        return (driver.distanceValue !== null)
          && (driver.distanceValue <= config.levenshteinThreshold);
      }
      return driver.driver_num === valueAsNum;
    })
    .sort((driver1, driver2) => driver1.distanceValue - driver2.distanceValue);

  if (drivers.length === 1
      || (drivers.length > 0 && (drivers[0].distanceValue !== null)
      && (drivers[0].distanceValue < drivers[1].distanceValue))) {
    return drivers[0];
  }

  return null;
};

module.exports.searchForRace = (result, handlerInput) => {
  if (!handlerInput.requestEnvelope || !handlerInput.requestEnvelope.request
        || !handlerInput.requestEnvelope.request.intent
        || !handlerInput.requestEnvelope.request.intent.slots
        || !handlerInput.requestEnvelope.request.intent.slots.Race
        || !handlerInput.requestEnvelope.request.intent.slots.Race.value) {
    return null;
  }

  const { value } = handlerInput.requestEnvelope.request.intent.slots.Race;

  logger.info(`Received slot value of ${value}`);

  if (!result || result.length === 0) {
    return null;
  }

  const races = result.map((race) => {
    const grandPrixName = race.race_name.split(' ').slice(0, -2).join(' ').toLowerCase();
    const circuitName = race.circuit_ref.replace('_', ' ').toLowerCase();
    const distanceValue = Math.min(
      levenshtein(grandPrixName, value.toLowerCase()),
      levenshtein(race.circuit_location.toLowerCase(), value.toLowerCase()),
      levenshtein(race.circuit_country.toLowerCase(), value.toLowerCase()),
      levenshtein(race.circuit_country.toLowerCase(), value.toLowerCase()),
      levenshtein(circuitName, value.toLowerCase()),
    );
    return {
      ...race,
      distanceValue,
    };
  })
    .filter((race) => (race.distanceValue !== null)
        && (race.distanceValue <= config.levenshteinRaceThreshold))
    .sort((race1, race2) => race1.distanceValue - race2.distanceValue);

  if (races.length === 1
      || (races.length > 0 && (races[0].distanceValue !== null)
      && (races[0].distanceValue < races[1].distanceValue))) {
    return races[0];
  }

  return null;
};

module.exports.getNextRace = (result) => {
  if (!result.calendar || result.calendar.length === 0) {
    throw Error('Calendar was empty');
  }

  const filteredRaces = result.calendar.filter((race) => race.is_next_race);

  if (!filteredRaces.length) {
    throw Error('Filtered calendar results were empty');
  }

  return filteredRaces[0];
};

module.exports.getRemainingRaces = (result) => {
  if (!result.calendar || result.calendar.length === 0) {
    throw Error('Calendar was empty');
  }

  const filteredRaces = result.calendar.filter((race) => race.race_round >= result.next_race_round);

  if (!filteredRaces.length) {
    throw Error('Filtered calendar results were empty');
  }

  return filteredRaces;
};

module.exports.formatRaceDate = (date) => {
  const raceDate = new Date(date);
  const monthString = (raceDate.getMonth() + 1).toString().padStart(2, '0');
  const dateString = raceDate.getDate().toString().padStart(2, '0');
  const formattedDate = `${raceDate.getFullYear()}${monthString}${dateString}`;
  return formattedDate;
};

module.exports.getDriversChampionship = async (year = null) => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled information');
  }

  const result = await axios.get(`${config.predictionEndpoint}/info/championship/drivers${year ? `/${year}` : ''}`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from drivers championship request for year ${year}: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.getConstructorsChampionship = async (year = null) => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled information');
  }

  const result = await axios.get(`${config.predictionEndpoint}/info/championship/constructors${year ? `/${year}` : ''}`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from constructors championship request for year ${year}: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.searchForConstructor = (result, handlerInput) => {
  if (!handlerInput.requestEnvelope || !handlerInput.requestEnvelope.request
        || !handlerInput.requestEnvelope.request.intent
        || !handlerInput.requestEnvelope.request.intent.slots
        || !handlerInput.requestEnvelope.request.intent.slots.Team
        || !handlerInput.requestEnvelope.request.intent.slots.Team.value) {
    return null;
  }

  const { value } = handlerInput.requestEnvelope.request.intent.slots.Team;

  logger.info(`Received slot value of ${value}`);

  if (!result || result.length === 0) {
    return null;
  }

  const constructors = result.map((constructor) => ({
    ...constructor,
    distanceValue: levenshtein(constructor.constructor_name, value.toLowerCase()),
  }))
    .filter(
      (constructor) => (constructor.distanceValue !== null)
        && (constructor.distanceValue <= config.levenshteinConstructorThreshold),
    )
    .sort((constructor1, constructor2) => constructor1.distanceValue - constructor2.distanceValue);

  if (constructors.length === 1
      || (constructors.length > 0 && (constructors[0].distanceValue !== null)
      && (constructors[0].distanceValue < constructors[1].distanceValue))) {
    return constructors[0];
  }

  return null;
};

module.exports.validateYear = (handlerInput) => {
  if (!handlerInput.requestEnvelope || !handlerInput.requestEnvelope.request
        || !handlerInput.requestEnvelope.request.intent
        || !handlerInput.requestEnvelope.request.intent.slots
        || !handlerInput.requestEnvelope.request.intent.slots.Year
        || !handlerInput.requestEnvelope.request.intent.slots.Year.value) {
    return null;
  }

  const { value } = handlerInput.requestEnvelope.request.intent.slots.Year;

  logger.info(`Received slot value of ${value}`);

  if (Number.isNaN(Number.parseInt(value, 10))) {
    return null;
  }

  return value;
};

module.exports.getLastResult = async () => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled information');
  }

  const result = await axios.get(`${config.predictionEndpoint}/info/results/race`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from race results request: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.getLastQualifyingResult = async () => {
  if (!config.predictionEndpoint) {
    throw Error('Prediction endpoint missing - disabled information');
  }

  const result = await axios.get(`${config.predictionEndpoint}/info/results/qualifying`);

  if (result.status !== 200) {
    throw Error(`Did not receive status 200 from qualifying results request: ${result.status}`);
  }

  if (!result.data || typeof result.data !== 'object') {
    throw Error('Did not receive data object');
  }

  return result;
};

module.exports.getQualifyingLap = (driver) => {
  let lap = null;
  if (driver.qualifying_q3) {
    lap = driver.qualifying_q3;
  } else if (driver.qualifying_q2) {
    lap = driver.qualifying_q2;
  } else if (driver.qualifying_q1) {
    lap = driver.qualifying_q1;
  }

  const lapParts = lap.split(':');
  if (lapParts.length === 2) {
    return `${lapParts[0]} minute${lapParts[0] > 1 ? 's' : ''} ${lapParts[1]}`;
  }

  return lap;
};
