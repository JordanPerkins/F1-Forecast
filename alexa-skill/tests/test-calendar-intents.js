const alexaTest = require('alexa-skill-test-framework');
const nock = require('nock');

const data = require('./data/calender-data.json');

const setGoodResponse = () => {
    nock('https://prediction-endpoint')
    .get('/info/calendar')
    .reply(200, data);
};

const set500Response = () => {
    nock('https://prediction-endpoint')
    .get('/info/calendar')
    .reply(500, 'Internal Server Error');
};

const setEmptyResponse = () => {
    nock('https://prediction-endpoint')
    .get('/info/calendar')
    .reply(200, {
        calendar: [],
        next_race_id: null,
        next_race_round: null,
        year: null
    });
};

alexaTest.initialize(
	require('../code/index.js'),
	"amzn1.ask.skill.b2fd259e-591d-4fec-add2-cabc6c46e0e4",
	"amzn1.ask.account.VOID");

describe("Calendar Intents", () => {
	describe("GetNextRaceIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("GetNextRaceIntent"),
                    says: 'The next Grand Prix, which is the <say-as interpret-as="ordinal">11</say-as> round of the championship, is the Austrian Grand Prix at the Red Bull Ring on <say-as interpret-as="date">20200705</say-as>, starting at 13:10:00 GMT.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("GetNextRaceIntent"),
                    says: 'I was unable to get the race calendar at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("GetNextRaceIntent"),
                    says: 'I was unable to get the race calendar at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
	describe("CalendarRaceIntent", () => {
        describe("Returns correct result with a valid backend response #1", () => {
            setGoodResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("CalendarRaceIntent", { Race: 'French'}),
                    says: 'The French Grand Prix, which was the <say-as interpret-as="ordinal">10</say-as> round of the championship, took place at Circuit Paul Ricard on <say-as interpret-as="date">20200628</say-as>',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a valid backend response #2", () => {
            setGoodResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("CalendarRaceIntent", { Race: 'Austrian'}),
                    says: 'The Austrian Grand Prix, which is the <say-as interpret-as="ordinal">11</say-as> round of the championship, will take place at Red Bull Ring on <say-as interpret-as="date">20200705</say-as>, starting at 13:10:00 GMT.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("CalendarRaceIntent", { NotRace: 'Austrian'}),
                    says: 'I could not find the race you requested. You can use the race name, circuit name, circuit location or circuit country.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("CalendarRaceIntent", { Race: 'Bahrain'}),
                    says: 'I could not find the race you requested. You can use the race name, circuit name, circuit location or circuit country.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("CalendarRaceIntent", { Race: 'Bahrain'}),
                    says: 'I was unable to get the race calendar at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("CalendarRaceIntent", { Race: 'Bahrain'}),
                    says: 'I was unable to get the race calendar at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("GetFullCalendarIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("GetFullCalendarIntent"),
                    says: 'Here is the full race calendar for the 2020 season. <amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 11. The Austrian Grand Prix on <say-as interpret-as="date">20200705</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 12. The British Grand Prix on <say-as interpret-as="date">20200719</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 13. The Hungarian Grand Prix on <say-as interpret-as="date">20200802</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 14. The Belgian Grand Prix on <say-as interpret-as="date">20200830</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 15. The Italian Grand Prix on <say-as interpret-as="date">20200906</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 16. The Singapore Grand Prix on <say-as interpret-as="date">20200920</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 17. The Russian Grand Prix on <say-as interpret-as="date">20200927</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 18. The Japanese Grand Prix on <say-as interpret-as="date">20201011</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 19. The United States Grand Prix on <say-as interpret-as="date">20201025</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 20. The Mexico City Grand Prix on <say-as interpret-as="date">20201101</say-as> </amazon:emotion><break time="1s"/>Would you like me to continue?',
                    repromptsNothing: false,
                    shouldEndSession: false,
                    reprompts: "Would you like me to continue?",
                    hasAttributes: {
                        lastIntent: 'GetFullCalendarIntent',
                        lastPosition: 10,
                        lastResult: value => JSON.stringify(value) === JSON.stringify(data.calendar.slice(1))
                    }
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("GetFullCalendarIntent"),
                    says: 'I was unable to get the race calendar at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse();
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("GetFullCalendarIntent"),
                    says: 'I was unable to get the race calendar at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Can be continued with the YesIntent", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                    says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 21. The Brazilian Grand Prix on <say-as interpret-as="date">20201115</say-as> </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/>Round 22. The Abu Dhabi Grand Prix on <say-as interpret-as="date">20201129</say-as> </amazon:emotion><break time="1s"/>Summary concluded',
                    repromptsNothing: true,
                    shouldEndSession: true,
                    withSessionAttributes: {
                        lastIntent: 'GetFullCalendarIntent',
                        lastPosition: 10,
                        lastResult: JSON.parse(JSON.stringify(data.calendar.slice(1)))
                    },
                }
            ]);
        });
    });
});