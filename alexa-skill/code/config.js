'use strict';

module.exports = () => ({
    listMax: process.env.OVERRIDE_LIST_MAX ? Number.parseInt(process.env.OVERRIDE_LIST_MAX, 10) : 10,
    levenshteinThreshold: process.env.OVERRIDE_LEVENSHTEIN_THRESHOLD ? Number.parseInt(process.env.OVERRIDE_LEVENSHTEIN_THRESHOLD, 10) : 4,
    levenshteinRaceThreshold: process.env.OVERRIDE_LEVENSHTEIN_RACE_THRESHOLD ? Number.parseInt(process.env.OVERRIDE_LEVENSHTEIN_RACE_THRESHOLD, 10) : 2
}); 