const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

class PythonBridge {
  constructor() {
    this.process = null;
    this.port = 9182;
    this.projectRoot = path.join(__dirname, '..', '..', '..');
  }

  async start() {
    const pythonPath = path.join(this.projectRoot, 'backend', 'venv', 'Scripts', 'python.exe');
    const wrapperPath = path.join(__dirname, 'server_wrapper.py');

    // Check if venv exists, fallback to system python
    const fs = require('fs');
    const actualPython = fs.existsSync(pythonPath) ? pythonPath : 'python';

    console.log(`Starting Python: ${actualPython}`);
    console.log(`Wrapper: ${wrapperPath}`);

    return new Promise((resolve, reject) => {
      this.process = spawn(actualPython, [wrapperPath], {
        cwd: this.projectRoot,  // DONA root — where backend/ lives
        env: {
          ...process.env,
          CURSOROS_HTTP_PORT: this.port.toString(),
          PYTHONPATH: this.projectRoot,  // Ensure Python can find backend/
        },
        stdio: ['pipe', 'pipe', 'pipe'],
      });

      this.process.stdout.on('data', (data) => {
        const msg = data.toString().trim();
        console.log(`[Python] ${msg}`);
        if (msg.includes('SERVER_READY')) {
          resolve();
        }
      });

      this.process.stderr.on('data', (data) => {
        console.error(`[Python ERR] ${data.toString().trim()}`);
      });

      this.process.on('exit', (code) => {
        console.log(`Python process exited with code ${code}`);
      });

      this.process.on('error', (err) => {
        console.error('Failed to spawn Python:', err);
        reject(err);
      });

      // Timeout fallback
      setTimeout(() => resolve(), 5000);
    });
  }

  async stop() {
    if (this.process) {
      this.process.kill();
    }
  }

  async call(endpoint, method = 'GET', body = null) {
    return new Promise((resolve, reject) => {
      const options = {
        hostname: 'localhost',
        port: this.port,
        path: endpoint,
        method: method,
        headers: { 'Content-Type': 'application/json' },
      };

      const req = http.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => (data += chunk));
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve(data);
          }
        });
      });

      req.on('error', (e) => {
        // Return empty events on error to keep polling alive
        if (endpoint === '/api/events') {
          resolve({ events: [] });
        } else {
          reject(e);
        }
      });

      req.setTimeout(30000, () => {
        req.destroy();
        if (endpoint === '/api/events') {
          resolve({ events: [] });
        } else {
          reject(new Error('Timeout'));
        }
      });

      if (body) req.write(JSON.stringify(body));
      req.end();
    });
  }
}

module.exports = PythonBridge;
