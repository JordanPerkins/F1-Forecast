const alexaTest = require('alexa-skill-test-framework');

alexaTest.initialize(
	require('../code/index.js'),
	"amzn1.ask.skill.b2fd259e-591d-4fec-add2-cabc6c46e0e4",
	"amzn1.ask.account.VOID");

describe("Generic Intents", () => {
	describe("LaunchRequestHandler", () => {
        const message = 'Welcome to F1 forecast. You can ask me a question such as who do you think will win the next grand prix or who was the last pole-sitter. For detailed information on the full capabilities of this application, just ask for help. What would you like me to do?';
		alexaTest.test([
			{
				request: alexaTest.getLaunchRequest(),
                says: message,
                repromptsNothing: false,
                shouldEndSession: false,
                reprompts: message
			}
		]);
    });

    describe("HelpIntentHandler", () => {
        const message = 'F1 forecast can provide predictions for the upcoming qualifying and race sessions. Just ask me who will win, where will Lewis Hamilton qualify or even get a prediction for the entire grid by asking me for the forecast. The application can tell you about the upcoming race calendar, just ask me what the next race is, when the British grand prix is, or ask for a full calendar. If you would like to know about the current championship standings, just ask who is leading the championship, where Max Verstappen is in the standings, or even ask for the full standings. Finally, you can find out about the results of the last grand prix by asking for the last winner, where Charles Leclerc qualified in the last grand prix, or ask for the full result. How can I help?';
		alexaTest.test([
			{
				request: alexaTest.getIntentRequest("AMAZON.HelpIntent"),
                says: message,
                repromptsNothing: false,
                shouldEndSession: false,
                reprompts: message
			}
		]);
    });

    describe("CancelAndStopIntentHandler", () => {
		alexaTest.test([
			{
				request: alexaTest.getIntentRequest("AMAZON.CancelIntent"),
                says: "Goodbye!",
                repromptsNothing: true,
                shouldEndSession: true
			}
		]);
    });

    describe("FallbackIntentHandler", () => {
        const message = "I'm sorry, I didn't get that. If you want to learn more about F1 forecast, just ask me for help. What would you like to do?";
		alexaTest.test([
			{
				request: alexaTest.getIntentRequest("AMAZON.FallbackIntent"),
                says: message,
                repromptsNothing: false,
                shouldEndSession: false,
                reprompts: message
			}
		]);
    });
});