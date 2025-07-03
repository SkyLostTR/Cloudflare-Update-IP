#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

// Determine python executable
const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');

const script = path.join(__dirname, 'CloudflareUpdate.py');
const args = process.argv.slice(2);

const child = spawn(python, [script, ...args], { stdio: 'inherit' });
child.on('exit', code => process.exit(code));
