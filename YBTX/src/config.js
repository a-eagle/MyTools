DEBUG = false;

let SERVER_URL = '';

if (DEBUG) {
    SERVER_URL = 'http://localhost:8010'
} else {
    SERVER_URL = ''
}

export {
    SERVER_URL
}