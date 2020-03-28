'use strict';

module.exports = () => ({
    forecastDriversMax: process.env.OVERRIDE_FORECAST_DRIVERS_MAX ? Number.parseInt(process.env.OVERRIDE_FORECAST_DRIVERS_MAX, 10) : 7,
    levenshteinThreshold: process.env.OVERRIDE_LEVENSHTEIN_THRESHOLD ? Number.parseInt(process.env.OVERRIDE_LEVENSHTEIN_THRESHOLD, 10) : 4
}); 