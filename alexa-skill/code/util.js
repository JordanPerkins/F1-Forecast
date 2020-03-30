'use strict';

const axios = require('axios');
const levenshtein = require('js-levenshtein');

const config = require('./config.js')();

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
};

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
};

module.exports.getCalendar = async () => {
    if (!process.env.PREDICTION_ENDPOINT) {
        throw Error('Prediction endpoint missing - disabled information');
    }

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+'/info/calendar');

    if (result.status !== 200) {
        throw Error(`Did not receive status 200 from calendar request: ${result.status}`);
    }

    if (!result.data || typeof result.data !== 'object') {
        throw Error('Did not receive data object');
    }

    return result;
};

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
                const valueSplit = value.split(' ');
                if (valueSplit.length === 2) {
                    distanceValue = Math.min(
                        levenshtein(driver.driver_forename.toLowerCase(), valueSplit[0].toLowerCase()),
                        levenshtein(driver.driver_surname.toLowerCase(), valueSplit[1].toLowerCase())
                    );
                } else if (valueSplit.length === 1) {
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
                return (driver.distanceValue !== null) && (driver.distanceValue <= config.levenshteinThreshold);
            }
            return driver.driver_num === valueAsNum;
        })
        .sort((driver1, driver2) => driver1.distanceValue - driver2.distanceValue);

    if (drivers.length === 1 || (drivers.length > 0 && (drivers[0].distanceValue !== null) && (drivers[0].distanceValue < drivers[1].distanceValue))) {
        return drivers[0];
    }

    return null;
};

module.exports.searchForRace = (result, handlerInput) => {
    if (!handlerInput.requestEnvelope || !handlerInput.requestEnvelope.request ||
        !handlerInput.requestEnvelope.request.intent || !handlerInput.requestEnvelope.request.intent.slots ||
        !handlerInput.requestEnvelope.request.intent.slots.Race ||
        !handlerInput.requestEnvelope.request.intent.slots.Race.value) {
            return null;
    }

    const value = handlerInput.requestEnvelope.request.intent.slots.Race.value;

    console.info(`Received slot value of ${value}`);

    if (!result.calendar || result.calendar.length === 0) {
        return null;
    }

    const races = result.calendar.map(race => {
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
                distanceValue
            }
        })
        .filter(race => {
            return (race.distanceValue !== null) && (race.distanceValue <= config.levenshteinRaceThreshold);
        })
        .sort((race1, race2) => race1.distanceValue - race2.distanceValue);

    if (races.length === 1 || (races.length > 0 && (races[0].distanceValue !== null) && (races[0].distanceValue < races[1].distanceValue))) {
        return races[0];
    }

    return null;
};

module.exports.getNextRace = result => {
    if (!result.calendar|| result.calendar.length === 0) {
        throw Error('Calendar was empty');
    }

    const filteredRaces = result.calendar.filter(race => race.is_next_race);

    if (!filteredRaces.length) {
        throw Error('Filtered calendar results were empty');
    }

    return filteredRaces[0];
};

module.exports.getRemainingRaces = result => {
    if (!result.calendar|| result.calendar.length === 0) {
        throw Error('Calendar was empty');
    }

    const filteredRaces = result.calendar.filter(race => race.race_round >= result.next_race_round);

    if (!filteredRaces.length) {
        throw Error('Filtered calendar results were empty');
    }

    return filteredRaces;
};

module.exports.formatRaceDate = date => {
    const raceDate = new Date(date);
    const monthString = (raceDate.getMonth() + 1).toString().padStart(2, '0');
    const dateString = raceDate.getDate().toString().padStart(2, '0');
    const formattedDate = `${raceDate.getFullYear()}${monthString}${dateString}`;
    return formattedDate;
};

module.exports.getDriversChampionship = async (year = null) => {
    if (!process.env.PREDICTION_ENDPOINT) {
        throw Error('Prediction endpoint missing - disabled information');
    }

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+`/info/championship/drivers${year ? `/${year}` : ''}`);

    if (result.status !== 200) {
        throw Error(`Did not receive status 200 from drivers championship request for year ${year}: ${result.status}`);
    }

    if (!result.data || typeof result.data !== 'object') {
        throw Error('Did not receive data object');
    }

    return result;
};

module.exports.getConstructorsChampionship = async (year = null) => {
    if (!process.env.PREDICTION_ENDPOINT) {
        throw Error('Prediction endpoint missing - disabled information');
    }

    const result = await axios.get(process.env.PREDICTION_ENDPOINT+`/info/championship/constructors${year ? `/${year}` : ''}`);

    if (result.status !== 200) {
        throw Error(`Did not receive status 200 from constructors championship request for year ${year}: ${result.status}`);
    }

    if (!result.data || typeof result.data !== 'object') {
        throw Error('Did not receive data object');
    }

    return result;
};
