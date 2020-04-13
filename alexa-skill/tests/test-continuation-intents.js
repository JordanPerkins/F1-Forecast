const alexaTest = require('alexa-skill-test-framework');

alexaTest.initialize(
	require('../code/index.js'),
	"amzn1.ask.skill.b2fd259e-591d-4fec-add2-cabc6c46e0e4",
	"amzn1.ask.account.VOID");

describe("Continuation Intents", () => {
    describe("NoIntent replies correctly", () => {
        alexaTest.test([
            {
                request: alexaTest.getIntentRequest("AMAZON.NoIntent"),
                says: 'Ok. I will stop now. See you later!',
                repromptsNothing: true,
                shouldEndSession: true
            }
        ]);
    });
    describe("YesIntent replies correctly with no attributes present", () => {
        alexaTest.test([
            {
                request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                says: 'I was unable to carry out the requested action. Please check back later',
                repromptsNothing: true,
                shouldEndSession: true
            }
        ]);
    });
});