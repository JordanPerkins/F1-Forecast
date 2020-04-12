const alexaTest = require('alexa-skill-test-framework');
const nock = require('nock');

const raceData = require('./data/race-prediction-data.json');
const qualifyingData = require('./data/qualifying-prediction-data.json');

let lastInterceptor;

const setGoodResponse = type => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/predict/${type}`)
        .reply(200, type === 'race' ? raceData : qualifyingData);

};

const set500Response = type => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/predict/${type}`)
        .reply(500, 'Internal Server Error')
};

const setEmptyResponse = type => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/predict/${type}`)
        .reply(200, {
            result: [],
            id: 1031,
            name: 'french',
            year: 2020
        })
};

describe("Prediction Intents", () => {
	describe("PredictWinnerIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictWinnerIntent"),
                    says: 'The predicted winner of the 2020 french grand prix is Finnish driver Valtteri Bottas',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictWinnerIntent"),
                    says: 'I was unable to make a race prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictWinnerIntent"),
                    says: 'I was unable to make a race prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
	describe("PredictQualifyingIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingIntent"),
                    says: 'The driver on pole position at the 2020 french grand prix is predicted to be Finnish driver Valtteri Bottas',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingIntent"),
                    says: 'I was unable to make a qualifying prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingIntent"),
                    says: 'I was unable to make a qualifying prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("PredictRacePositionIntent", () => {
        describe("Returns correct result with a valid backend response #1", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictRacePositionIntent", { Driver: 'Lewis Hamilton'}),
                    says: 'British driver Lewis Hamilton is predicted to finish in <say-as interpret-as="ordinal">2</say-as> at the 2020 french grand prix',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a valid backend response #2", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictRacePositionIntent", { Driver: '77' }),
                    says: 'Finnish driver Valtteri Bottas is predicted to finish in <say-as interpret-as="ordinal">1</say-as> at the 2020 french grand prix',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictRacePositionIntent", { NotDriver: 'Lewis Hamilton'}),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where will 44 finish at the next race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictRacePositionIntent", {Driver: 'Bill Gates'}),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where will 44 finish at the next race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictRacePositionIntent", { Driver: 'Bill Gates'}),
                    says: 'I was unable to make a race prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictRacePositionIntent", { Driver: 'Bill Gates'}),
                    says: 'I was unable to make a race prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("PredictQualifyingPositionIntent", () => {
        describe("Returns correct result with a valid backend response #1", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingPositionIntent", { Driver: 'Lewis Hamilton'}),
                    says: 'British driver Lewis Hamilton is predicted to qualify in <say-as interpret-as="ordinal">2</say-as> at the 2020 french grand prix with a lap time 0.025 seconds away from pole position',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a valid backend response #2", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingPositionIntent", { Driver: '77' }),
                    says: 'Finnish driver Valtteri Bottas is predicted to qualify in <say-as interpret-as="ordinal">1</say-as> at the 2020 french grand prix',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingPositionIntent", { NotDriver: 'Lewis Hamilton'}),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where will 44 qualify at the next race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingPositionIntent", {Driver: 'Bill Gates'}),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where will 44 qualify at the next race',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingPositionIntent", { Driver: 'Bill Gates'}),
                    says: 'I was unable to make a qualifying prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("PredictQualifyingPositionIntent", { Driver: 'Bill Gates'}),
                    says: 'I was unable to make a qualifying prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("ReadRaceForecastIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ReadRaceForecastIntent"),
                    says: 'Here is the race prediction forecast for the 2020 french grand prix.<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">1</say-as> Valtteri Bottas </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">2</say-as> Lewis Hamilton </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">3</say-as> Charles Leclerc </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">4</say-as> Max Verstappen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">5</say-as> Lando Norris </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">6</say-as> Carlos Sainz </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">7</say-as> Daniel Ricciardo </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">8</say-as> Pierre Gasly </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">9</say-as> Antonio Giovinazzi </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">10</say-as> Kimi Räikkönen </amazon:emotion><break time="1s"/>Would you like me to continue?',
                    repromptsNothing: false,
                    shouldEndSession: false,
                    reprompts: "Would you like me to continue?",
                    hasAttributes: {
                        lastIntent: 'ReadRaceForecastIntent',
                        lastPosition: 10,
                        lastResult: value => JSON.stringify(value) === JSON.stringify(raceData.result)
                    }
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ReadRaceForecastIntent"),
                    says: 'I was unable to make a race prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('race');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ReadRaceForecastIntent"),
                    says: 'I was unable to make a race prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Can be continued with the YesIntent", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                    says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">11</say-as> Nico Hülkenberg </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">12</say-as> Sergio Pérez </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">13</say-as> Kevin Magnussen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">14</say-as> Alexander Albon </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">15</say-as> Sebastian Vettel </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">16</say-as> Daniil Kvyat </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">17</say-as> Romain Grosjean </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">18</say-as> Lance Stroll </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">19</say-as> George Russell </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">20</say-as> Robert Kubica </amazon:emotion><break time="1s"/>Summary concluded',
                    repromptsNothing: true,
                    shouldEndSession: true,
                    withSessionAttributes: {
                        lastIntent: 'ReadRaceForecastIntent',
                        lastPosition: 10,
                        lastResult: JSON.parse(JSON.stringify(raceData.result))
                    },
                }
            ]);
        });
    });
    describe("ReadQualifyingForecastIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ReadQualifyingForecastIntent"),
                    says: 'Here is the qualifying prediction forecast for the 2020 french grand prix.<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">1</say-as> Valtteri Bottas </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">2</say-as> Lewis Hamilton </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">3</say-as> Charles Leclerc </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">4</say-as> Max Verstappen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">5</say-as> Lando Norris </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">6</say-as> Sebastian Vettel </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">7</say-as> Carlos Sainz </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">8</say-as> Daniel Ricciardo </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">9</say-as> Pierre Gasly </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">10</say-as> Antonio Giovinazzi </amazon:emotion><break time="1s"/>Would you like me to continue?',
                    repromptsNothing: false,
                    shouldEndSession: false,
                    reprompts: "Would you like me to continue?",
                    hasAttributes: {
                        lastIntent: 'ReadQualifyingForecastIntent',
                        lastPosition: 10,
                        lastResult: value => JSON.stringify(value) === JSON.stringify(qualifyingData.result)
                    }
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ReadQualifyingForecastIntent"),
                    says: 'I was unable to make a qualifying prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('qualifying');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ReadQualifyingForecastIntent"),
                    says: 'I was unable to make a qualifying prediction at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Can be continued with the YesIntent", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                    says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">11</say-as> Alexander Albon </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">12</say-as> Kimi Räikkönen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">13</say-as> Nico Hülkenberg </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">14</say-as> Sergio Pérez </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">15</say-as> Kevin Magnussen </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">16</say-as> Daniil Kvyat </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">17</say-as> Romain Grosjean </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">18</say-as> Lance Stroll </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">19</say-as> George Russell </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">20</say-as> Robert Kubica </amazon:emotion><break time="1s"/>Summary concluded',
                    repromptsNothing: true,
                    shouldEndSession: true,
                    withSessionAttributes: {
                        lastIntent: 'ReadQualifyingForecastIntent',
                        lastPosition: 10,
                        lastResult: JSON.parse(JSON.stringify(qualifyingData.result))
                    },
                }
            ]);
        });
    });
});