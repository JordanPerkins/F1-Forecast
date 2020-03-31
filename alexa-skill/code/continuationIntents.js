'use strict';

const Alexa = require('ask-sdk-core');

const { formatRaceDate } = require('./util.js');

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
    }
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
            if (attributes.lastPosition && attributes.lastResult && attributes.lastIntent) {
                console.info(`Yes received for ${attributes.lastIntent}: Last position is ${attributes.lastPosition}`);
                for (let i = attributes.lastPosition; i < attributes.lastPosition+config.listMax; i++) {
                    if (i < attributes.lastResult.length) {
                        if (attributes.lastIntent === 'ReadRaceForecastIntent' || attributes.lastIntent === 'ReadQualifyingForecastIntent' || attributes.lastIntent === 'GetFullRaceResultIntent' || attributes.lastIntent === 'GetFullQualifyingResultIntent') {
                            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${attributes.lastResult[i].driver_forename} ${attributes.lastResult[i].driver_surname} </amazon:emotion>`;
                        } else if (attributes.lastIntent === 'GetFullCalendarIntent') {
                            const formattedDate = formatRaceDate(attributes.lastResult[i].race_date);
                            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round ${attributes.lastResult[i].race_round}. The ${attributes.lastResult[i].race_name} on <say-as interpret-as="date">${formattedDate}</say-as> </amazon:emotion>`;                          
                        } else if (attributes.lastIntent === 'FullChampionshipDriverIntent') {
                            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${attributes.lastResult[i].driver_forename} ${attributes.lastResult[i].driver_surname} with ${attributes.lastResult[i].driver_points} points</amazon:emotion>`;  
                        } else if (attributes.lastIntent === 'FullChampionshipConstructorsIntent') {
                            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${attributes.lastResult[i].constructor_name} with ${attributes.lastResult[i].constructor_points} points</amazon:emotion>`;  
                        }
                    }
                }
                if (attributes.lastPosition+config.listMax < attributes.lastResult.length) {
                    speakOutput += '<break time="1s"/>Would you like me to continue?';
                    attributes.lastPosition = attributes.lastPosition+config.listMax;
                    attributes.lastResult = attributes.lastResult;
                    attributes.lastIntent = attributes.lastIntent;
                    return handlerInput.responseBuilder
                    .speak(speakOutput)
                    .reprompt('<break time="1s"/>Would you like me to continue?')
                    .getResponse();
                }
                speakOutput += '<break time="1s"/>Summary concluded'
                return handlerInput.responseBuilder
                .speak(speakOutput)
                .getResponse();
            }
        } catch (e) {
            console.error(`Error fetching result for YesIntent: ${e}`);
            speakOutput = 'I was unable to carry out the requested action. Please check back later'
            return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
        }
    }
};

module.exports = [
    NoIntentHandler,
    YesIntentHandler
];
