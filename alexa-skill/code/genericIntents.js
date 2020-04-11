
const Alexa = require('ask-sdk-core');

const LaunchRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
  },
  handle(handlerInput) {
    const speakOutput = 'Welcome to F1 forecast. You can ask me a question such as who do you think will win the \
    next grand prix or who was the last pole-sitter. For detailed information on the full capabilities of this \
    application, just ask for help. What would you like me to do?';
    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  },
};

const HelpIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.HelpIntent');
  },
  handle(handlerInput) {
    const speakOutput = 'F1 forecast can provide predictions for the upcoming qualifying and race sessions. \
    Just ask me who will win, where will Lewis Hamilton qualify or even get a prediction for the entire grid by \
    asking me for the forecast. The application can tell you about the upcoming race calendar, just ask me what the \
    next race is, when the British grand prix is, or ask for a full calendar. If you would like to know about the current \
    championship standings, just ask who is leading the championship, where Max Verstappen is in the standings, or even \
    ask for the full standings. Finally, you can find out about the results of the last grand prix by asking for the last \
    winner, where Charles Leclerc qualified in the last grand prix, or ask for the full result. How can I help?';

    return handlerInput.responseBuilder
      .speak(speakOutput)
      .reprompt(speakOutput)
      .getResponse();
  },
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
  },
};

const SessionEndedRequestHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'SessionEndedRequest';
  },
  handle(handlerInput) {
    const attributes = handlerInput.attributesManager.getSessionAttributes();
    attributes.lastPosition = undefined;
    attributes.lastResult = undefined;
    attributes.lastIntent = undefined;
    return handlerInput.responseBuilder.getResponse();
  },
};

const FallbackIntentHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && (Alexa.getIntentName(handlerInput.requestEnvelope) === 'AMAZON.FallbackIntent');
  },
  handle(handlerInput) {
    const speakOutput = 'I\'m sorry, I didn\'t get that. If you want to learn more about F1 forecast, just ask \
    me for help. What would you like to do?';

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
