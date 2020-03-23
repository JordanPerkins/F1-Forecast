// This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK (v2).
// Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
// session persistence, api calls, and more.
const Alexa = require('ask-sdk-core');
const { getRacePrediction, getQualifyingPrediction, searchForDriver } = require('./util.js');

const FORECAST_DRIVERS_MAX = process.env.OVERRIDE_FORECAST_DRIVERS_MAX ? Number.parseInt(process.env.OVERRIDE_FORECAST_DRIVERS_MAX, 10) : 7

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle(handlerInput) {
        const speakOutput = 'Welcome, you can say Hello or Help. Which would you like to try?';
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};
const PredictWinnerIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictWinnerIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getRacePrediction();
            const data = result.data;
            speakOutput = `The predicted winner of the ${data.year} ${data.name} grand prix is ${data.result[0].driver_nationality} driver ${data.result[0].driver_forename} ${data.result[0].driver_surname}`;
        } catch(e) {
            console.error(`Error fetching result for PredictWinnerIntent: ${e}`);
            speakOutput = 'I was unable to make a race prediction at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
const PredictQualifyingIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictQualifyingIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getQualifyingPrediction();
            const data = result.data;
            speakOutput = `The driver on pole position at the ${data.year} ${data.name} grand prix is predicted to be ${data.result[0].driver_nationality} driver ${data.result[0].driver_forename} ${data.result[0].driver_surname}`;
        } catch(e) {
            console.error(`Error fetching result for PredictQualifyingIntent: ${e}`);
            speakOutput = 'I was unable to make a qualifying prediction at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
const PredictRacePositionIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictRacePositionIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getRacePrediction();
            const searchedResult = searchForDriver(result.data, handlerInput);
            if (!searchedResult) {
                speakOutput = `I coud not find the driver you requested. Try using the driver number instead.
                For example, where will 44 finish at the next race`;
            } else {
                speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} ${searchedResult.driver_surname} is predicted to finish
                in <say-as interpret-as="ordinal">${searchedResult.position}</say-as> at the ${result.data.year} ${result.data.name} grand prix`;
            }
        } catch(e) {
            console.error(`Error fetching result for PredictRacePositionIntent: ${e}`);
            speakOutput = 'I was unable to make a race prediction at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
const PredictQualifyingPositionIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'PredictQualifyingPositionIntent';
    },
    async handle(handlerInput) {
        let speakOutput;
        try {
            const result = await getQualifyingPrediction();
            const searchedResult = searchForDriver(result.data, handlerInput);
            if (!searchedResult) {
                speakOutput = `I coud not find the driver you requested. Try using the driver number instead.
                For example, where will 44 qualify at the next race`;
            } else {
                speakOutput = `${searchedResult.driver_nationality} driver ${searchedResult.driver_forename} ${searchedResult.driver_surname} is predicted to qualify
                in <say-as interpret-as="ordinal">${searchedResult.position}</say-as> at the ${result.data.year} ${result.data.name} grand prix`;
                if (searchedResult.driver_quali_result) {
                    speakOutput += ` with a lap time ${searchedResult.driver_quali_result} seconds away from pole position`;
                }
            }
        } catch(e) {
            console.error(`Error fetching result for PredictQualifyingPositionIntent: ${e}`);
            speakOutput = 'I was unable to make a qualifying prediction at this time. Please check back later'
        }
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
const ReadRaceForecastIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ReadRaceForecastIntent';
    },
    async handle(handlerInput) {
        const attributes = handlerInput.attributesManager.getSessionAttributes();
        attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
        let speakOutput;
        try {
            const result = await getRacePrediction();
            const data = result.data;
            speakOutput = `Here is the race prediction forecast for the ${data.year} ${data.name} grand prix.`
            for (let i = 0; i < FORECAST_DRIVERS_MAX; i++) {
                if (i < data.result.length) {
                    speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${data.result[i].driver_forename} ${data.result[i].driver_surname}</amazon:emotion>`
                }
            }
            if (FORECAST_DRIVERS_MAX < data.result.length) {
                attributes.lastPosition = FORECAST_DRIVERS_MAX;
                attributes.lastResult = data;
                return handlerInput.responseBuilder
                .speak(speakOutput)
                .reprompt('Would you like me to continue?')
                .getResponse();
            }
            return handlerInput.responseBuilder
            .speak(speakOutput);
        } catch(e) {
            console.error(`Error fetching result for ReadRaceForecastIntent: ${e}`);
            speakOutput = 'I was unable to make a race prediction at this time. Please check back later'
            return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
        }
    }
};
const ReadQualifyingForecastIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'ReadQualifyingForecastIntent';
    },
    async handle(handlerInput) {
        const attributes = handlerInput.attributesManager.getSessionAttributes();
        attributes.lastIntent = Alexa.getIntentName(handlerInput.requestEnvelope);
        let speakOutput;
        try {
            const result = await getQualifyingPrediction();
            const data = result.data;
            speakOutput = `Here is the qualifying prediction forecast for the ${data.year} ${data.name} grand prix.`
            for (let i = 0; i < FORECAST_DRIVERS_MAX; i++) {
                if (i < data.result.length) {
                    speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${data.result[i].driver_forename} ${data.result[i].driver_surname}</amazon:emotion>`;
                }
            }
            if (FORECAST_DRIVERS_MAX < data.result.length) {
                attributes.lastPosition = FORECAST_DRIVERS_MAX;
                attributes.lastResult = data;
                return handlerInput.responseBuilder
                .speak(speakOutput)
                .reprompt('Would you like me to continue?')
                .getResponse();
            }
            return handlerInput.responseBuilder
            .speak(speakOutput);
        } catch(e) {
            console.error(`Error fetching result for ReadQualifyingForecastIntent: ${e}`);
            speakOutput = 'I was unable to make a qualifying prediction at this time. Please check back later'
            return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
        }
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
            if (attributes.lastIntent && (attributes.lastIntent === 'ReadRaceForecastIntent' || attributes.lastIntent === 'ReadQualifyingForecastIntent')) {
                if (attributes.lastPosition && attributes.lastResult) {
                    for (let i = attributes.lastPosition; i < attributes.lastPosition+FORECAST_DRIVERS_MAX; i++) {
                        if (i < attributes.lastResult.result.length) {
                            speakOutput += `<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">${i + 1}</say-as> ${attributes.lastResult.result[i].driver_forename} ${attributes.lastResult.result[i].driver_surname}</amazon:emotion>`;
                        }
                    }
                    if (attributes.lastPosition+FORECAST_DRIVERS_MAX < attributes.lastResult.result.length) {
                        attributes.lastPosition = attributes.lastPosition+FORECAST_DRIVERS_MAX;
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

const HelpIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent';
    },
    handle(handlerInput) {
        const speakOutput = 'You can say hello to me! How can I help?';

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};
const CancelAndStopIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
                || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
    },
    handle(handlerInput) {
        const speakOutput = 'Goodbye!';
        return handlerInput.responseBuilder
            .speak(speakOutput)
            .getResponse();
    }
};
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
const SessionEndedRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
    },
    handle(handlerInput) {
        // Any cleanup logic goes here.
        return handlerInput.responseBuilder.getResponse();
    }
};

// The intent reflector is used for interaction model testing and debugging.
// It will simply repeat the intent the user said. You can create custom handlers
// for your intents by defining them above, then also adding them to the request
// handler chain below.
const IntentReflectorHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest';
    },
    handle(handlerInput) {
        const intentName = Alexa.getIntentName(handlerInput.requestEnvelope);
        const speakOutput = `You just triggered ${intentName}`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            //.reprompt('add a reprompt if you want to keep the session open for the user to respond')
            .getResponse();
    }
};

// Generic error handling to capture any syntax or routing errors. If you receive an error
// stating the request handler chain is not found, you have not implemented a handler for
// the intent being invoked or included it in the skill builder below.
const ErrorHandler = {
    canHandle() {
        return true;
    },
    handle(handlerInput, error) {
        console.log(`~~~~ Error handled: ${error.stack}`);
        const speakOutput = `Sorry, I had trouble doing what you asked. Please try again.`;

        return handlerInput.responseBuilder
            .speak(speakOutput)
            .reprompt(speakOutput)
            .getResponse();
    }
};

// The SkillBuilder acts as the entry point for your skill, routing all request and response
// payloads to the handlers above. Make sure any new handlers or interceptors you've
// defined are included below. The order matters - they're processed top to bottom.
exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(
        LaunchRequestHandler,
        PredictWinnerIntentHandler,
        PredictQualifyingIntentHandler,
        PredictRacePositionIntentHandler,
        PredictQualifyingPositionIntentHandler,
        ReadRaceForecastIntentHandler,
        ReadQualifyingForecastIntentHandler,
        HelpIntentHandler,
        YesIntentHandler,
        NoIntentHandler,
        CancelAndStopIntentHandler,
        SessionEndedRequestHandler,
        IntentReflectorHandler, // make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
        ) 
    .addErrorHandlers(
        ErrorHandler,
        )
    .lambda();
