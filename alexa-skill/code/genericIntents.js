
const Alexa = require('ask-sdk-core');

const logger = require('./logger.js');

/**
 * The intent for handling a new session launch. It returns information which
 * can help the user navigate the application.
 */
const LaunchRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
  },
  handle(handlerInput) {
    logger.info('LaunchRequestHandler has been invoked');
    const speakOutput = 'Welcome to F1 forecast. You can ask me a question such as who do you think will win the ' +
    'next grand prix or who was the last pole-sitter. For detailed information on the full capabilities of this ' +
    'application, just ask for help. What would you like me to do?';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  },
};

/**
 * The intent for handling a request for help. It returns a comprehensive summary
 * of the actions available in the application.
 */
const HelpIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent');
  },
  handle(handlerInput) {
    logger.info('HelpIntentHandler has been invoked');
    const speakOutput = 'F1 forecast can provide predictions for the upcoming qualifying and race sessions. ' +
    'Just ask me who will win, where will Lewis Hamilton qualify or even get a prediction for the entire grid by ' +
    'asking me for the forecast. The application can tell you about the upcoming race calendar, just ask me what the ' +
    'next race is, when the British grand prix is, or ask for a full calendar. If you would like to know about the current ' +
    'championship standings, just ask who is leading the championship, where Max Verstappen is in the standings, or even ' +
    'ask for the full standings. Finally, you can find out about the results of the last grand prix by asking for the last ' +
    'winner, where Charles Leclerc qualified in the last grand prix, or ask for the full result. How can I help?';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  },
};

/**
 * The intent for handling stopping or cancelling the session.
 */
const CancelAndStopIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.CancelIntent'
                || Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.StopIntent');
  },
  handle(handlerInput) {
    logger.info('CancelAndStopIntentHandler has been invoked');
    const speakOutput = 'Goodbye!';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .getResponse();
  },
};

/**
 * The intent for handling ending the session.
 */
const SessionEndedRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
  },
  handle(handlerInput) {
    logger.info('SessionEndedRequestHandler has been invoked');
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastPosition = undefined;
    attributes.lastResult = undefined;
    attributes.lastIntent = undefined;
    return handlerInput.responseBuilder.getResponse();
  },
};

/**
 * The intent which is triggered when no other intent has been triggered, informing
 * the user it did not understand the request, and providing guidance.
 */
const FallbackIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.FallbackIntent');
  },
  handle(handlerInput) {
    logger.info('FallbackIntentHandler has been invoked');
    const speakOutput = 'I\'m sorry, I didn\'t get that. If you want to learn more about F1 forecast, just ask ' +
    'me for help. What would you like to do?';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  },
};


module.exports = [
  LaunchRequestHandler,
  HelpIntentHandler,
  CancelAndStopIntentHandler,
  SessionEndedRequestHandler,
  FallbackIntentHandler,
];
