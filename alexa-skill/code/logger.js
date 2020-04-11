const winston = require('winston');

const LOG_LEVEL = process.env.LOG_LEVEL ? process.env.LOG_LEVEL : 'warn';

const logger = winston.createLogger({
  transports: [
    new winston.transports.Console({ level: LOG_LEVEL }),
  ],
});

module.exports = logger;
