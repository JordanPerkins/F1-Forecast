'use strict';

const Alexa = require('ask-sdk-core');
const { getDriversChampionship,  getConstructorsChampionship, searchForDriver, searchForConstructor } = require('./util.js');
const config = require('./config.js')();

const ChampionshipLeaderIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ChampionshipLeaderIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const [driversResult, constructorsResult] = await Promise.all([
                getDriversChampionship(),
                getConstructorsChampionship()
            ]);
            if (!driversResult.data.standings || !driversResult.data.standings.length === 0) {
                throw Error('Drivers standings were empty');
            }

            if (!constructorsResult.data.standings || !constructorsResult.data.standings.length === 0) {
                throw Error('Constructors standings were empty');
            }

            const driversLeader = driversResult.data.standings[0];
            const constructorsLeader = constructorsResult.data.standings[0];

            speakOutput = `The driver's championship is currently led by ${driversLeader.driver_nationality} driver ${driversLeader.driver_forename} ${driversLeader.driver_surname} with ${driversLeader.driver_points} points and ${driversLeader.driver_wins} wins. `;
            speakOutput += `The constructor's championship is currently led by ${constructorsLeader.constructor_nationality} constructor ${constructorsLeader.constructor_name} with ${constructorsLeader.constructor_points} points and ${constructorsLeader.constructor_wins} wins.`
        } catch(e) {
            console.error(`Error fetching result for ChampionshipLeaderIntentHandler: ${e}`);
            speakOutput = 'I was unable to get the championship information at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const ChampionshipDriverIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ChampionshipDriverIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getDriversChampionship();
            const searchedResult = searchForDriver(result.data.standings, handlerInput);
            if (!searchedResult) {
                speakOutput = `I coud not find the driver you requested. Try using the driver number instead.
                For example, where is 44 in the standings`;
            } else {
                speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} ${searchedResult.driver_surname} is currently
                <say-as interpret-as="ordinal">${searchedResult.driver_position}</say-as> in the championship, with ${searchedResult.driver_points} points and ${searchedResult.driver_wins} wins`;
            }
        } catch(e) {
            console.error(`Error fetching result for ChampionshipDriverIntentHandler: ${e}`);
            speakOutput = 'I was unable to get the championship information at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const ChampionshipConstructorIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ChampionshipConstructorIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getConstructorsChampionship();
            const searchedResult = searchForConstructor(result.data.standings, handlerInput);
            if (!searchedResult) {
                speakOutput = `I coud not find the constructor you requested. You can get a full championship breakdown by asking f. one forecast for the full constructors standings.`;
            } else {
                speakOutput = `${searchedResult.constructor_nationality} constructor ${searchedResult.constructor_name} is currently
                <say-as interpret-as="ordinal">${searchedResult.constructor_position}</say-as> in the championship, with ${searchedResult.constructor_points} points and ${searchedResult.constructor_wins} wins`;
            }
        } catch(e) {
            console.error(`Error fetching result for ChampionshipConstructorIntentHandler: ${e}`);
            speakOutput = 'I was unable to get the championship information at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};


module.exports = [
    ChampionshipLeaderIntentHandler,
    ChampionshipDriverIntentHandler,
    ChampionshipConstructorIntentHandler
];
