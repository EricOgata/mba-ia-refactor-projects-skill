const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };
const configuredLevel = Object.prototype.hasOwnProperty.call(LEVELS, process.env.LOG_LEVEL)
    ? LEVELS[process.env.LOG_LEVEL]
    : LEVELS.info;

function write(level, meta, message) {
    if (LEVELS[level] > configuredLevel) return;

    const entry = {
        level,
        time: new Date().toISOString(),
        message,
        ...(meta || {}),
    };
    const line = JSON.stringify(entry);

    if (level === 'error') console.error(line);
    else console.log(line);
}

module.exports = {
    error: (meta, message) => write('error', meta, message),
    warn: (meta, message) => write('warn', meta, message),
    info: (meta, message) => write('info', meta, message),
    debug: (meta, message) => write('debug', meta, message),
};
