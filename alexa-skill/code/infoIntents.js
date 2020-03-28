'use strict';

const Alexa = require('ask-sdk-core');
const { getCalendar, getNextRace, formatRaceDate, getRemainingRaces } = require('./util.js');

const config = require('./config.js')();

const GetNextRaceIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetNextRaceIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getCalendar();
            const nextRace = getNextRace(result.data);
            const formattedDate = formatRaceDate(nextRace.race_date);
            speakOutput = `The next Grand Prix, which is the <say-as interpret-as="ordinal">${nextRace.race_round}</say-as> round of the championship, is the ${nextRace.race_name} at the ${nextRace.circuit_name} on <say-as interpret-as="date">${formattedDate}</say-as>, starting at ${nextRace.race_time} GMT.`;
        } catch(e) {
            console.error(`Error fetching result for GetNextRaceIntentIntent: ${e}`);
            speakOutput = 'I was unable to get the race calendar at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};

const GetFullCalendarIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'GetFullCalendarIntent';
    },
    async handle(handlerInput) {
        const attributes = handlerInput.attributesManager.getSessionAttributes();
        attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
        let speakOutput;
        try {
            const result = await getCalendar();
            const filteredRaces = getRemainingRaces(result.data);
            speakOutput = `Here is the full race calendar for the ${result.data.year} season. `
            for (let i = 0; i < config.listMax; i++) {
                if (i < filteredRaces.length) {
                    const formattedDate = formatRaceDate(filteredRaces[i].race_date);
                    speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round ${filteredRaces[i].race_round}. The ${filteredRaces[i].race_name} on <say-as interpret-as="date">${formattedDate}</say-as> </amazon:emotion>`;
                }
            }
            if (config.listMax < filteredRaces.length) {
                attributes.lastPosition = config.listMax;
                attributes.lastResult = filteredRaces;
                return handlerInput.responseBuilder
                .speak(speakOutput)
                .reprompt('Would you like me to continue?')
                .getResponse();
            }
            return handlerInput.responseBuilder
            .speak(speakOutput);
        } catch(e) {
            console.error(`Error fetching result for GetFullCalendarIntentHandler: ${e}`);
            speakOutput = 'I was unable to get the race calendar at this time. Please check back later'
            return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
        }
    }
};


module.exports = {
    GetNextRaceIntentHandler,
    GetFullCalendarIntentHandler
};