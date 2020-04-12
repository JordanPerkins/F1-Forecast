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
                    says: 'I coud not find the driver you requested. Try using the driver number instead. For example, where will 44 finish at the next race',
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
                    says: 'I coud not find the driver you requested. Try using the driver number instead. For example, where will 44 finish at the next race',
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
});