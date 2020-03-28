'use strict';

const Alexa = require('ask-sdk-core');

const config = require('./config.js')();

module.exports.NoIntentHandler = {
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

module.exports.YesIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.YesIntent';
    },
    async handle(handlerInput) {
        let speakOutput = '';
        const attributes = handlerInput.attributesManager.getSessionAttributes();
        try {
            if (attributes.lastIntent && (attributes.lastIntent === 'ReadRaceForecastIntent' || attributes.lastIntent === 'ReadQualifyingForecastIntent')) {
                if (attributes.lastPosition && attributes.lastResult) {
                    for (let i = attributes.lastPosition; i < attributes.lastPosition+config.forecastDriversMax; i++) {
                        if (i < attributes.lastResult.result.length) {
                            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${attributes.lastResult.result[i].driver_forename} ${attributes.lastResult.result[i].driver_surname}</amazon:emotion>`;
                        }
                    }
                    if (attributes.lastPosition+config.forecastDriversMax < attributes.lastResult.result.length) {
                        attributes.lastPosition = attributes.lastPosition+config.forecastDriversMax;
                        attributes.lastResult = attributes.lastResult;
                        attributes.lastIntent = attributes.lastIntent;
                        return handlerInput.responseBuilder
                        .speak(speakOutput)
                        .reprompt('Would you like me to continue?')
                        .getResponse();
                    }
                    speakOutput += '<break time="1s"/>Forecast concluded'
                    return handlerInput.responseBuilder
                    .speak(speakOutput)
                    .getResponse();
                }
            }
        } catch (e) {
            console.error(`Error fetching result for ReadRaceForecastIntent: ${e}`);
            speakOutput = 'I was unable to carry out the requested action. Please check back later'
            return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
        }
    }
};
