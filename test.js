const assert = require('assert');
const { execSync } = require('child_process');
const fs = require('fs');

// Ensure the Python script compiles without syntax errors
execSync('python3 -m py_compile CloudflareUpdate.py');

const pkg = require('./package.json');
assert(pkg.bin && pkg.bin['cloudflare-update-ip'] === './cli.js');

// Verify the CLI script exists and is executable
fs.accessSync(pkg.bin['cloudflare-update-ip'], fs.constants.X_OK);

// Ensure the CLI can run and show help without errors
execSync('node cli.js --help', { stdio: 'ignore' });

console.log('All checks passed');
