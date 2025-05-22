require('whatwg-fetch');
require('@testing-library/jest-dom');

// ...existing setup...
const { TextEncoder, TextDecoder } = require('util');
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
