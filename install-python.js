const { spawnSync } = require('child_process');

const python = process.env.PYTHON || (process.platform === 'win32' ? 'python' : 'python3');

const result = spawnSync(python, ['-m', 'pip', 'install', '-r', 'requirements.txt'], { stdio: 'inherit' });

if (result.error) {
  console.error('Failed to install Python dependencies:', result.error.message);
  process.exit(1);
}
process.exit(result.status);
