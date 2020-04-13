const alexaTest = require('alexa-skill-test-framework');
const nock = require('nock');

const raceData = require('./data/results-race.json');
const qualifyingData = require('./data/results-qualifying.json');

let lastInterceptor;

const setGoodResponse = type => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/info/results/${type}`)
        .reply(200, type === 'race' ? raceData : qualifyingData);

};

const set500Response = type => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/info/results/${type}`)
        .reply(500, 'Internal Server Error')
};

const setEmptyResponse = type => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/info/results/${type}`)
        .reply(200, {
            last_race_id: 1030,
            last_race_name: 'abu dhabi',
            last_race_year: 2019,
            results: []
        })
};

describe("Results Intents", () => {
	describe("LastWinnerIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastWinnerIntent"),
                    says: 'British driver Lewis Hamilton won the 2019 abu dhabi grand prix after starting on the grid in <say-as interpret-as="ordinal">1</say-as> position, scoring 26 points',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastWinnerIntent"),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastWinnerIntent"),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
	describe("LastPoleIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastPoleIntent"),
                    says: 'British driver Lewis Hamilton started on pole position at the 2019 abu dhabi grand prix after a lap time of 1 minute 34.779.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastPoleIntent"),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastPoleIntent"),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("LastRacePositionIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastRacePositionIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'British driver Lewis Hamilton finished in <say-as interpret-as="ordinal">1</say-as> at the 2019 abu dhabi grand prix, scoring 26 points.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastRacePositionIntent", { NotDriver: 'Lewis Hamilton' }),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where did 44 finish at the last race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastRacePositionIntent", { Driver: 'Bill Gates' }),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where did 44 finish at the last race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastRacePositionIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("LastRacePositionIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("QualifyingPositionIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("QualifyingPositionIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'British driver Lewis Hamilton qualified in <say-as interpret-as="ordinal">1</say-as> at the 2019 abu dhabi grand prix, with a lap time of 1 minute 34.779',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("QualifyingPositionIntent", { NotDriver: 'Lewis Hamilton' }),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where did 44 qualify at the last race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("QualifyingPositionIntent", { Driver: 'Bill Gates' }),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where did 44 qualify at the last race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("QualifyingPositionIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("QualifyingPositionIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'I was unable to retrieve race result information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("GetFullRaceResultIntent", () => {
            describe("Returns correct result with a valid backend response", () => {
                setGoodResponse('race');
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("GetFullRaceResultIntent"),
                        says: 'Here are the full results of the 2019 abu dhabi grand prix. <amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">1</say-as> Lewis Hamilton</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">2</say-as> Max Verstappen</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">3</say-as> Charles Leclerc</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">4</say-as> Valtteri Bottas</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">5</say-as> Sebastian Vettel</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">6</say-as> Alexander Albon</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">7</say-as> Sergio Pérez</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">8</say-as> Lando Norris</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">9</say-as> Daniil Kvyat</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">10</say-as> Carlos Sainz</amazon:emotion><break time="1s"/>Would you like me to continue?',
                        repromptsNothing: false,
                        shouldEndSession: false,
                        reprompts: "Would you like me to continue?",
                        hasAttributes: {
                            lastIntent: 'GetFullRaceResultIntent',
                            lastPosition: 10,
                            lastResult: value => JSON.stringify(value) === JSON.stringify(raceData.results)
                        }
                    }
                ]);
            });
            describe("Returns correct result with a 500 backend response", () => {
                set500Response('race');
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("GetFullRaceResultIntent"),
                        says: 'I was unable to retrieve race result information at this time. Please check back later',
                        repromptsNothing: true,
                        shouldEndSession: true
                    }
                ]);
            });
            describe("Returns correct result with an empty backend response", () => {
                setEmptyResponse('race');
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("GetFullRaceResultIntent"),
                        says: 'I was unable to retrieve race result information at this time. Please check back later',
                        repromptsNothing: true,
                        shouldEndSession: true
                    }
                ]);
            });
            describe("Can be continued with the YesIntent", () => {
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                        says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">11</say-as> Daniel Ricciardo </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">12</say-as> Nico Hülkenberg </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">13</say-as> Kimi Räikkönen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">14</say-as> Kevin Magnussen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">15</say-as> Romain Grosjean </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">16</say-as> Antonio Giovinazzi </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">17</say-as> George Russell </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">18</say-as> Pierre Gasly </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">19</say-as> Robert Kubica </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">20</say-as> Lance Stroll </amazon:emotion><break time="1s"/>Summary concluded',
                        repromptsNothing: true,
                        shouldEndSession: true,
                        withSessionAttributes: {
                            lastIntent: 'GetFullRaceResultIntent',
                            lastPosition: 10,
                            lastResult: JSON.parse(JSON.stringify(raceData.results))
                        },
                    }
                ]);
            });
        });
        describe("GetFullQualifyingResultIntent", () => {
            describe("Returns correct result with a valid backend response", () => {
                setGoodResponse('qualifying');
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("GetFullQualifyingResultIntent"),
                        says: 'Here are the full results of the 2019 abu dhabi grand prix qualifying session. <amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">1</say-as> Lewis Hamilton</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">2</say-as> Valtteri Bottas</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">3</say-as> Max Verstappen</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">4</say-as> Charles Leclerc</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">5</say-as> Sebastian Vettel</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">6</say-as> Alexander Albon</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">7</say-as> Lando Norris</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">8</say-as> Daniel Ricciardo</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">9</say-as> Carlos Sainz</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">10</say-as> Nico Hülkenberg</amazon:emotion><break time="1s"/>Would you like me to continue?',
                        repromptsNothing: false,
                        shouldEndSession: false,
                        reprompts: "Would you like me to continue?",
                        hasAttributes: {
                            lastIntent: 'GetFullQualifyingResultIntent',
                            lastPosition: 10,
                            lastResult: value => JSON.stringify(value) === JSON.stringify(qualifyingData.results)
                        }
                    }
                ]);
            });
            describe("Returns correct result with a 500 backend response", () => {
                set500Response('qualifying');
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("GetFullQualifyingResultIntent"),
                        says: 'I was unable to retrieve race result information at this time. Please check back later',
                        repromptsNothing: true,
                        shouldEndSession: true
                    }
                ]);
            });
            describe("Returns correct result with an empty backend response", () => {
                setEmptyResponse('qualifying');
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("GetFullQualifyingResultIntent"),
                        says: 'I was unable to retrieve race result information at this time. Please check back later',
                        repromptsNothing: true,
                        shouldEndSession: true
                    }
                ]);
            });
            describe("Can be continued with the YesIntent", () => {
                alexaTest.test([
                    {
                        request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                        says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">11</say-as> Sergio Pérez </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">12</say-as> Pierre Gasly </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">13</say-as> Lance Stroll </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">14</say-as> Daniil Kvyat </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">15</say-as> Kevin Magnussen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">16</say-as> Romain Grosjean </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">17</say-as> Antonio Giovinazzi </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">18</say-as> Kimi Räikkönen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">19</say-as> George Russell </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">20</say-as> Robert Kubica </amazon:emotion><break time="1s"/>Summary concluded',
                        repromptsNothing: true,
                        shouldEndSession: true,
                        withSessionAttributes: {
                            lastIntent: 'GetFullQualifyingResultIntent',
                            lastPosition: 10,
                            lastResult: JSON.parse(JSON.stringify(qualifyingData.results))
                        },
                    }
                ]);
            });
        });
    });
});