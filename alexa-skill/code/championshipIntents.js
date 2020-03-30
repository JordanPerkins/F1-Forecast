'use strict';

const Alexa = require('ask-sdk-core');
const { getDriversChampionship,  getConstructorsChampionship } = require('./util.js');

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

            speakOutput = `The driver's championship is currently lead by ${driversLeader.driver_nationality} driver ${driversLeader.driver_forename} ${driversLeader.driver_surname} with ${driversLeader.driver_points} points and ${driversLeader.driver_wins} wins. `;
            speakOutput += `The constructor's championship is currently lead by ${constructorsLeader.constructor_nationality} constructor ${constructorsLeader.constructor_name} with ${constructorsLeader.constructor_points} points and ${constructorsLeader.constructor_wins} wins.`
        } catch(e) {
            console.error(`Error fetching result for ChampionshipLeaderIntentHandler: ${e}`);
            speakOutput = 'I was unable to get the championship information at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};


module.exports = {
    ChampionshipLeaderIntentHandler
};
