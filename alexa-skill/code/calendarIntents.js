'use strict';

const Alexa = require('ask-sdk-core');
const { getCalendar, getNextRace, formatRaceDate, getRemainingRaces, searchForRace } = require('./util.js');

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
            console.error(`Error fetching result for GetNextRaceIntentHandler: ${e}`);
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
                speakOutput += '<break time="1s"/>Would you like me to continue?';
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

const CalendarRaceIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'CalendarRaceIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getCalendar();
            const searchedRace = searchForRace(result.data.calendar, handlerInput);
            if (!searchedRace) {
                speakOutput = `I coud not find the race you requested. You can use the race name, circuit name, circuit location or circuit country.`;
            } else {
                const formattedDate = formatRaceDate(searchedRace.race_date);
                if (searchedRace.race_round < result.data.next_race_round) {
                    speakOutput = `The ${searchedRace.race_name}, which was the <say-as interpret-as="ordinal">${searchedRace.race_round}</say-as> round of the championship, took place at ${searchedRace.circuit_name} on <say-as interpret-as="date">${formattedDate}</say-as>`;
                } else {
                    speakOutput = `The ${searchedRace.race_name}, which is the <say-as interpret-as="ordinal">${searchedRace.race_round}</say-as> round of the championship, will take place at ${searchedRace.circuit_name} on <say-as interpret-as="date">${formattedDate}</say-as>, starting at ${searchedRace.race_time} GMT.`;
                }
            }
        } catch(e) {
            console.error(`Error fetching result for CalendarRaceIntent: ${e}`);
            speakOutput = 'I was unable to get the race calendar at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};



module.exports = {
    GetNextRaceIntentHandler,
    GetFullCalendarIntentHandler,
    CalendarRaceIntentHandler
};