#!/usr/bin/env node
/** Stop dev servers on ports 8000 and 5173 (cross-platform). */
const { execSync } = require('child_process');

function killPort(port) {
  try {
    if (process.platform === 'win32') {
      const out = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf8' });
      const pids = new Set();
      for (const line of out.split('\n')) {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && /^\d+$/.test(pid) && pid !== '0') pids.add(pid);
      }
      for (const pid of pids) {
        try { execSync(`taskkill /PID ${pid} /F`); } catch (_) {}
      }
    } else {
      execSync(`lsof -ti :${port} | xargs kill -9 2>/dev/null || true`, { shell: true });
    }
  } catch (_) {}
}

killPort(8000);
killPort(5173);
console.log('Ports 8000 et 5173 libérés (si des processus tournaient).');
