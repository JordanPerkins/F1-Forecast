const alexaTest = require('alexa-skill-test-framework');
const nock = require('nock');

const driverData = require('./data/drivers-championship-data.json');
const constructorData = require('./data/constructors-championship-data.json');

const driver2009Data = require('./data/drivers-championship-data-2009.json');
const constructor2009Data = require('./data/constructors-championship-data-2009.json');

let lastInterceptor;

const setGoodResponse = (type, year) => {
    let data;
    if (year) {
        data = (type === 'drivers' ? driver2009Data : constructor2009Data)
    } else {
        data = (type === 'drivers' ? driverData : constructorData);
    }
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/info/championship/${type}${year ? `/${year}` : ''}`)
        .reply(200, data);

};

const set500Response = (type, year) => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/info/championship/${type}${year ? `/${year}` : ''}`)
        .reply(500, 'Internal Server Error')
};

const setEmptyResponse = (type, year) => {
    lastInterceptor = nock('https://prediction-endpoint')
        .get(`/info/championship/${type}${year ? `/${year}` : ''}`)
        .reply(200, {
            last_race_id: 1030,
            last_race_name: 'abu dhabi',
            last_race_year: 2019,
            standings: []
        })
};

describe("Championship Intents", () => {
	describe("ChampionshipLeaderIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('drivers');
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipLeaderIntent"),
                    says: "The driver's championship is currently led by British driver Lewis Hamilton with 413 points and 11 wins. The constructor's championship is currently led by German constructor Mercedes with 739 points and 15 wins.",
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('drivers');
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipLeaderIntent"),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('drivers');
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipLeaderIntent"),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("ChampionshipDriverIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipDriverIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'British driver Lewis Hamilton is currently <say-as interpret-as="ordinal">1</say-as> in the championship, with 413 points and 11 wins',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipDriverIntent", { NotDriver: 'Lewis Hamilton' }),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where is 44 in the standings',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipDriverIntent", { Driver: 'Bill Gates' }),
                    says: 'I could not find the driver you requested. Try using the driver number instead. For example, where is 44 in the standings',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipDriverIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipDriverIntent", { Driver: 'Lewis Hamilton' }),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("ChampionshipConstructorIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipConstructorIntent", { Team: 'Mercedes' }),
                    says: 'German constructor Mercedes is currently <say-as interpret-as="ordinal">1</say-as> in the championship, with 739 points and 15 wins',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipConstructorIntent", { NotTeam: 'Mercedes' }),
                    says: 'I could not find the constructor you requested. You can get a full championship breakdown by asking f. one forecast for the full constructors standings.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a non-matching slot", () => {
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipConstructorIntent", { Team: 'Ford' }),
                    says: 'I could not find the constructor you requested. You can get a full championship breakdown by asking f. one forecast for the full constructors standings.',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipConstructorIntent", { Team: 'Mercedes' }),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("ChampionshipConstructorIntent",  { Team: 'Mercedes' }),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
    describe("FullChampionshipDriverIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("FullChampionshipDriverIntent"),
                    says: 'Here are the full drivers standings for the 2019 season. <amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">1</say-as> Lewis Hamilton with 413 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">2</say-as> Valtteri Bottas with 326 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">3</say-as> Max Verstappen with 278 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">4</say-as> Charles Leclerc with 264 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">5</say-as> Sebastian Vettel with 240 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">6</say-as> Carlos Sainz with 96 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">7</say-as> Pierre Gasly with 95 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">8</say-as> Alexander Albon with 92 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">9</say-as> Daniel Ricciardo with 54 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">10</say-as> Sergio Pérez with 52 points. </amazon:emotion><break time="1s"/>Would you like me to continue?',
                    repromptsNothing: false,
                    shouldEndSession: false,
                    reprompts: "Would you like me to continue?",
                    hasAttributes: {
                        lastIntent: 'FullChampionshipDriverIntent',
                        lastPosition: 10,
                        lastResult: value => JSON.stringify(value) === JSON.stringify(driverData.standings)
                    }
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("FullChampionshipDriverIntent"),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('drivers');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("FullChampionshipDriverIntent"),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Can be continued with the YesIntent", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                    says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">11</say-as> Lando Norris with 49 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">12</say-as> Kimi Räikkönen with 43 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">13</say-as> Daniil Kvyat with 37 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">14</say-as> Nico Hülkenberg with 37 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">15</say-as> Lance Stroll with 21 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">16</say-as> Kevin Magnussen with 20 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">17</say-as> Antonio Giovinazzi with 14 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">18</say-as> Romain Grosjean with 8 points.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">19</say-as> Robert Kubica with 1 point.</amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">20</say-as> George Russell with 0 points.</amazon:emotion><break time="1s"/>Summary concluded',
                    repromptsNothing: true,
                    shouldEndSession: true,
                    withSessionAttributes: {
                        lastIntent: 'FullChampionshipDriverIntent',
                        lastPosition: 10,
                        lastResult: JSON.parse(JSON.stringify(driverData.standings))
                    },
                }
            ]);
        });
    });
    describe("FullChampionshipConstructorsIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("FullChampionshipConstructorsIntent"),
                    says: 'Here are the full constructors standings for the 2019 season. <amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">1</say-as> Mercedes with 739 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">2</say-as> Ferrari with 504 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">3</say-as> Red Bull with 417 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">4</say-as> McLaren with 145 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">5</say-as> Renault with 91 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">6</say-as> Toro Rosso with 85 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">7</say-as> Racing Point with 73 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">8</say-as> Alfa Romeo with 57 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">9</say-as> Haas F1 Team with 28 points. </amazon:emotion><amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">10</say-as> Williams with 1 point. </amazon:emotion><break time="1s"/>Would you like me to continue?',
                    repromptsNothing: false,
                    shouldEndSession: false,
                    reprompts: "Would you like me to continue?",
                    hasAttributes: {
                        lastIntent: 'FullChampionshipConstructorsIntent',
                        lastPosition: 10,
                        lastResult: value => JSON.stringify(value) === JSON.stringify(constructorData.standings)
                    }
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("FullChampionshipConstructorsIntent"),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('constructors');
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("FullChampionshipConstructorsIntent"),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Can be continued with the YesIntent", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("AMAZON.YesIntent"),
                    says: '<amazon:emotion name="excited" intensity="medium"><break time="1s"/><say-as interpret-as="ordinal">11</say-as> Brawn with 1 point.</amazon:emotion><break time="1s"/>Summary concluded',
                    repromptsNothing: true,
                    shouldEndSession: true,
                    withSessionAttributes: {
                        lastIntent: 'FullChampionshipConstructorsIntent',
                        lastPosition: 10,
                        lastResult: JSON.parse(JSON.stringify(constructorData.standings))
                    },
                }
            ]);
        });
    });
    describe("WorldChampionIntent", () => {
        describe("Returns correct result with a valid backend response", () => {
            setGoodResponse('drivers', 2009);
            setGoodResponse('constructors', 2009);
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("WorldChampionIntent", { Year: '2009' }),
                    says: "The driver's world champion in 2009 was British driver Jenson Button with 95 points and 6 wins. The constructor's world champion was British constructor Brawn with 172 points and 8 wins.",
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a missing slot", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("WorldChampionIntent", { NotYear: '2009' }),
                    says: 'Please provide a valid season year. For example, who was world champion in 2009',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an invalid slot", () => {
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("WorldChampionIntent", { Year: 'Beans' }),
                    says: 'Please provide a valid season year. For example, who was world champion in 2009',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with a 500 backend response", () => {
            set500Response('drivers', 2009);
            set500Response('constructors', 2009);
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("WorldChampionIntent", { Year: '2009' }),
                    says: 'I was unable to get the championship information at this time. Please check back later',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
        describe("Returns correct result with an empty backend response", () => {
            setEmptyResponse('drivers', 2009);
            setEmptyResponse('constructors', 2009);
            alexaTest.test([
                {
                    request: alexaTest.getIntentRequest("WorldChampionIntent", { Year: '2009' }),
                    says: 'Please provide a valid season year. For example, who was world champion in 2009',
                    repromptsNothing: true,
                    shouldEndSession: true
                }
            ]);
        });
    });
});