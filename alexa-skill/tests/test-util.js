

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
    });
});