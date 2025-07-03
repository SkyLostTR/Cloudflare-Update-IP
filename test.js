const assert = require('assert');
const { execSync } = require('child_process');
const fs = require('fs');

// Ensure the Python script compiles without syntax errors
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
execSync(`${pythonCmd} -m py_compile CloudflareUpdate.py`);

const pkg = require('./package.json');
assert(pkg.bin && pkg.bin['cloudflare-update-ip'] === './cli.js');

// Verify the CLI script exists and is executable
fs.accessSync(pkg.bin['cloudflare-update-ip'], fs.constants.X_OK);

// Check that the CLI wrapper parses correctly
execSync('node --check cli.js');

console.log('All checks passed');
