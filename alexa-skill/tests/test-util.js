

const util = require('../code/util.js');

const { expect } = require('chai');

describe("Utilities", () => {
    describe("searchForDriver", () => {
        it("Returns null if slot is missing", () => {
            const result = util.searchForDriver([], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {

                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
        it("Throws error if result empty", () => {
            try {
                util.searchForDriver([], {
                    requestEnvelope: {
                        request: {
                            intent: {
                                slots: {
                                    Driver: { value: 'Lewis Hamilton' }
                                }
                            }
                        }
                    }
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Result was empty');
            }
        });
        it("Returns correct driver if number used", () => {
            const result = util.searchForDriver([
                {
                    driver_forename: 'Lewis',
                    driver_surname: 'Hamilton',
                    driver_num: 44
                },
                {
                    driver_forename: 'Valtteri',
                    driver_surname: 'Bottas',
                    driver_num: 77
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Driver: { value: '44' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                driver_forename: 'Lewis',
                driver_surname: 'Hamilton',
                driver_num: 44,
                position: 1,
                distanceValue: null
            });
        });
        it("Returns correct driver if only surname used", () => {
            const result = util.searchForDriver([
                {
                    driver_forename: 'Lewis',
                    driver_surname: 'Hamilton',
                    driver_num: 44
                },
                {
                    driver_forename: 'Valtteri',
                    driver_surname: 'Bottas',
                    driver_num: 77
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Driver: { value: 'Hamiltoon' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                driver_forename: 'Lewis',
                driver_surname: 'Hamilton',
                driver_num: 44,
                position: 1,
                distanceValue: 1
            });
        });
        it("Returns correct driver if only forename used", () => {
            const result = util.searchForDriver([
                {
                    driver_forename: 'Lewis',
                    driver_surname: 'Hamilton',
                    driver_num: 44
                },
                {
                    driver_forename: 'Valtteri',
                    driver_surname: 'Bottas',
                    driver_num: 77
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Driver: { value: 'Lewiis' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                driver_forename: 'Lewis',
                driver_surname: 'Hamilton',
                driver_num: 44,
                position: 1,
                distanceValue: 1
            });
        });
        it("Works for Romain Grosjean case", () => {
            const result = util.searchForDriver([
                {
                    driver_forename: 'Romain',
                    driver_surname: 'Grosjean',
                    driver_num: 8
                },
                {
                    driver_forename: 'Valtteri',
                    driver_surname: 'Bottas',
                    driver_num: 77
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Driver: { value: 'Roman Grosjean' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                driver_forename: 'Romain',
                driver_surname: 'Grosjean',
                driver_num: 8,
                distanceValue: 0,
                position: 1
            });
        });
        it("Does  not return a value if there is uncertainty", () => {
            const result = util.searchForDriver([
                {
                    driver_forename: 'Sebastian',
                    driver_surname: 'Vettel',
                    driver_num: 55
                },
                {
                    driver_forename: 'Sebastian',
                    driver_surname: 'Loeb',
                    driver_num: 16
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Driver: { value: 'Sebastian' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
    });
    it("Does not return a value if lev limit is reached", () => {
        const result = util.searchForDriver([
            {
                driver_forename: 'Lewis',
                driver_surname: 'Hamilton',
                driver_num: 44
            },
            {
                driver_forename: 'Valtteri',
                driver_surname: 'Bottas',
                driver_num: 77
            }
        ], {
            requestEnvelope: {
                request: {
                    intent: {
                        slots: {
                            Driver: { value: 'Derren Gibson' }
                        }
                    }
                }
            }
        });
        expect(result).to.deep.equal(null);
    });
    describe("searchForRace", () => {
        it("Returns null if slot is missing", () => {
            const result = util.searchForRace([], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {

                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
        it("Throws error if result empty", () => {
            try {
                util.searchForRace([], {
                    requestEnvelope: {
                        request: {
                            intent: {
                                slots: {
                                    Race: { value: 'Bahrain' }
                                }
                            }
                        }
                    }
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Result was empty');
            }
        });
        it("Returns correct race if race name used", () => {
            const result = util.searchForRace([
                {
                    race_name: 'Belgian Grand Prix',
                    circuit_location: 'Spa',
                    circuit_country: 'Belgium',
                    circuit_ref: 'spa'
                },
                {
                    race_name: 'Austrian Grand Prix',
                    circuit_location: 'Spielburg',
                    circuit_country: 'austria',
                    circuit_ref: 'red_bull_ring'
                },
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Race: { value: 'Belgian' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                race_name: 'Belgian Grand Prix',
                circuit_location: 'Spa',
                circuit_country: 'Belgium',
                circuit_ref: 'spa',
                distanceValue: 0
            });
        });
        it("Returns correct race if race location used", () => {
            const result = util.searchForRace([
                {
                    race_name: 'Belgian Grand Prix',
                    circuit_location: 'Spa',
                    circuit_country: 'Belgium',
                    circuit_ref: 'spa'
                },
                {
                    race_name: 'Austrian Grand Prix',
                    circuit_location: 'Spielburg',
                    circuit_country: 'austria',
                    circuit_ref: 'red_bull_ring'
                },
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Race: { value: 'spielburg' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                race_name: 'Austrian Grand Prix',
                circuit_location: 'Spielburg',
                circuit_country: 'austria',
                circuit_ref: 'red_bull_ring',
                distanceValue: 0
            });
        });
        it("Returns correct race if race country used", () => {
            const result = util.searchForRace([
                {
                    race_name: 'Belgian Grand Prix',
                    circuit_location: 'Spa',
                    circuit_country: 'Belgium',
                    circuit_ref: 'spa'
                },
                {
                    race_name: 'Austrian Grand Prix',
                    circuit_location: 'Spielburg',
                    circuit_country: 'austria',
                    circuit_ref: 'red_bull_ring'
                },
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Race: { value: 'austria' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                race_name: 'Austrian Grand Prix',
                circuit_location: 'Spielburg',
                circuit_country: 'austria',
                circuit_ref: 'red_bull_ring',
                distanceValue: 0
            });
        });
        it("Returns correct race if race circuit used", () => {
            const result = util.searchForRace([
                {
                    race_name: 'Belgian Grand Prix',
                    circuit_location: 'Spa',
                    circuit_country: 'Belgium',
                    circuit_ref: 'spa'
                },
                {
                    race_name: 'Austrian Grand Prix',
                    circuit_location: 'Spielburg',
                    circuit_country: 'austria',
                    circuit_ref: 'red_bull_ring'
                },
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Race: { value: 'red bull ring' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                race_name: 'Austrian Grand Prix',
                circuit_location: 'Spielburg',
                circuit_country: 'austria',
                circuit_ref: 'red_bull_ring',
                distanceValue: 0
            });
        });
        it("Does  not return a value if there is uncertainty", () => {
            const result = util.searchForRace([
                {
                    race_name: 'British Grand Prix',
                    circuit_location: 'Silverstone',
                    circuit_country: 'England',
                    circuit_ref: 'silverstone'
                },
                {
                    race_name: 'European Grand Prix',
                    circuit_location: 'Donnington',
                    circuit_country: 'England',
                    circuit_ref: 'donnington'
                },
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Race: { value: 'England' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
        it("Does not return a value if lev limit reached", () => {
            const result = util.searchForRace([
                {
                    race_name: 'Belgian Grand Prix',
                    circuit_location: 'Spa',
                    circuit_country: 'Belgium',
                    circuit_ref: 'spa'
                },
                {
                    race_name: 'Austrian Grand Prix',
                    circuit_location: 'Spielburg',
                    circuit_country: 'austria',
                    circuit_ref: 'red_bull_ring'
                },
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Race: { value: 'United States' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
    });
    describe("getNextRace", () => {
        it("Throws error if result empty", () => {
            try {
                util.getNextRace({
                    calendar: []
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Calendar was empty');
            }
        });
        it("Correctly returns the next race", () => {
            const result = util.getNextRace({
                calendar: [
                    {
                        race_name: 'British Grand Prix'
                    },
                    {
                        race_name: 'Austrian Grand Prix',
                        is_next_race: true
                    },
                    {
                        race_name: 'Russian Grand Prix'
                    }
                ]
            });
            expect(result).to.deep.equal({
                race_name: 'Austrian Grand Prix',
                is_next_race: true
            });
        });
        it("Throws error if there are no relevant races", () => {
            try {
                util.getNextRace({
                    calendar: [
                        {
                            race_name: 'British Grand Prix'
                        },
                        {
                            race_name: 'Austrian Grand Prix'
                        },
                        {
                            race_name: 'Russian Grand Prix'
                        }
                    ]
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Filtered calendar results were empty');
            }
        });
    });
    describe("getRemainingRaces", () => {
        it("Throws error if result empty", () => {
            try {
                util.getRemainingRaces({
                    calendar: []
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Calendar was empty');
            }
        });
        it("Correctly returns the next set of races", () => {
            const result = util.getRemainingRaces({
                next_race_round: 2,
                calendar: [
                    {
                        race_name: 'British Grand Prix',
                        race_round: 1
                    },
                    {
                        race_name: 'Austrian Grand Prix',
                        race_round: 2
                    },
                    {
                        race_name: 'Russian Grand Prix',
                        race_round: 3
                    }
                ]
            });
            expect(result).to.deep.equal([
                {
                    race_name: 'Austrian Grand Prix',
                    race_round: 2
                },
                {
                    race_name: 'Russian Grand Prix',
                    race_round: 3
                }
            ]);
        });
        it("Throws error if there are no relevant races", () => {
            try {
                util.getRemainingRaces({
                    next_race_round: 4,
                    calendar: [
                        {
                            race_name: 'British Grand Prix',
                            race_round: 1
                        },
                        {
                            race_name: 'Austrian Grand Prix',
                            race_round: 2
                        },
                        {
                            race_name: 'Russian Grand Prix',
                            race_round: 3
                        }
                    ]
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Filtered calendar results were empty');
            }
        });
    });
    describe("formatDate", () => {
        it('Correctly formats race date', () => {
            const result = util.formatRaceDate(new Date('2020-04-13T18:09:23.529Z'));
            expect(result).to.deep.equal('20200413');
        });
    });
    describe("searchForConstructor", () => {
        it("Returns null if slot is missing", () => {
            const result = util.searchForConstructor([], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {

                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
        it("Throws error if result empty", () => {
            try {
                util.searchForConstructor([], {
                    requestEnvelope: {
                        request: {
                            intent: {
                                slots: {
                                    Team: { value: 'Mercedes' }
                                }
                            }
                        }
                    }
                });
                expect.fail('Should have thrown');
            } catch(e) {
                expect(e.message).to.deep.equal('Result was empty');
            }
        });
        it("Returns correct race if constructor name used", () => {
            const result = util.searchForConstructor([
                {
                    constructor_name: 'Mercedes'
                },
                {
                    constructor_name: 'Red Bull'
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Team: { value: 'Mercedees' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal({
                constructor_name: 'Mercedes',
                distanceValue: 2
            });
        });
        it("Does  not return a value if there is uncertainty", () => {
            const result = util.searchForConstructor([
                {
                    constructor_name: 'Mercedes'
                },
                {
                    constructor_name: 'Mercedes'
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Team: { value: 'Mercedes' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
        it("Does  not return a value if lev limit is reached", () => {
            const result = util.searchForConstructor([
                {
                    constructor_name: 'Mercedes'
                },
                {
                    constructor_name: 'Red Bull'
                }
            ], {
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Team: { value: 'Ford' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
    });
    describe("validateYear", () => {
        it("Returns null if slot is missing", () => {
            const result = util.validateYear({
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {

                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
        it("Returns correct year value if present", () => {
            const result = util.validateYear({
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Year: { value: '2009' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal('2009');
        });
        it("Does not return a value if year is not valid", () => {
            const result = util.validateYear({
                requestEnvelope: {
                    request: {
                        intent: {
                            slots: {
                                Year: { value: 'Not A Year' }
                            }
                        }
                    }
                }
            });
            expect(result).to.deep.equal(null);
        });
    });
    describe("getQualifyingLap", () => {
        it('Returns correct result for a Q3 lap', () => {
            const result = util.getQualifyingLap(
                {
                    qualifying_q3: '1:37.249',
                    qualifying_q2: '1:38.439',
                    qualifying_q1: '1:39.124'
                }
            );
            expect(result).to.deep.equal('1 minute 37.249');
        });
        it('Returns correct result for a Q2 lap', () => {
            const result = util.getQualifyingLap(
                {
                    qualifying_q3: null,
                    qualifying_q2: '2:38.439',
                    qualifying_q1: '2:39.124'
                }
            );
            expect(result).to.deep.equal('2 minutes 38.439');
        });
        it('Returns correct result for a Q1 lap', () => {
            const result = util.getQualifyingLap(
                {
                    qualifying_q3: null,
                    qualifying_q2: null,
                    qualifying_q1: '2:39.124'
                }
            );
            expect(result).to.deep.equal('2 minutes 39.124');
        });
        it('Returns correct result for a result with missing laps', () => {
            const result = util.getQualifyingLap(
                {
                    qualifying_q3: null,
                    qualifying_q2: null,
                    qualifying_q1: null
                }
            );
            expect(result).to.deep.equal(null);
        });
    });
});