const Alexa = require('ask-sdk-core');
const predictionIntents = require('./predictionIntents.js');
const continuationIntents = require('./continuationIntents.js');
const genericIntents = require('./genericIntents.js');
const calendarIntents = require('./calendarIntents.js');
const championshipIntents = require('./championshipIntents.js');
const resultIntents = require('./resultIntents.js');

const logger = require('./logger.js');

/**
 * The last resort error handler - generally all intents handle their own errors
 * internally, but in the unlikely event there is a problem which isn't caught
 * within, this error handler will still provide a response to the user.
 */
const ErrorHandler = {
  canHandle() {
    return true;
  },
  handle(handlerInput, error) {
    logger.error(`~~~~ Error handled: ${error.stack}`);
    const speakOutput = 'Sorry, I had trouble doing what you asked. Please try again.';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  },
};

/**
 * A generic intent that can be used for debugging - if an intent match is found
 * in the model, but no intent handler has been specified, this handler will be
 * triggered to return the triggered intent name to the user. It must always
 * place last in the request handlers list.
 */
const IntentReflectorHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest';
  },
  handle(handlerInput) {
    const intentName = Alexa.getIntentName(handlerInput.requestEnvelope);
    const speakOutput = `You just triggered ${intentName}`;

    return handlerInput.responseBuilder
      .speak(speakOutput)
    // .reprompt('add a reprompt if you want to keep the session open for the user to respond')
      .getResponse();
  },
};

/**
 * The Skill Handler provided by the Alexa SDK. Overlapping intents are processed
 * top first. Here, the arrays of all included files are spread into the addRequestHandlers
 * function as arguments, as the Alexa SDK requires.
 */
exports.handler = Alexa.SkillBuilders.custom()
  .addRequestHandlers(
    ...predictionIntents,
    ...continuationIntents,
    ...genericIntents,
    ...calendarIntents,
    ...championshipIntents,
    ...resultIntents,
    IntentReflectorHandler,
  )
  .addErrorHandlers(ErrorHandler)
  .lambda();
