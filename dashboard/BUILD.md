# Building the React Dashboard

## Quick Start

### Option 1: Build and Run with Docker (Recommended)

```bash
cd /home/ahmed/Desktop/container-vuln-scanner/dashboard

# Build the Docker image
docker build -t scanner-dashboard:1.0 .

# Stop old dashboard if running
docker stop scanner-dashboard 2>/dev/null
docker rm scanner-dashboard 2>/dev/null

# Run the new React dashboard
docker run -d --name scanner-dashboard -p 8080:80 scanner-dashboard:1.0
```

Access at: http://127.0.0.1:8080

### Option 2: Development Mode (for testing changes)

```bash
cd /home/ahmed/Desktop/container-vuln-scanner/dashboard

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

Access at: http://localhost:3000

## Features

✅ Submit new scans
✅ View all scans with status
✅ Click scan to view vulnerabilities
✅ Auto-refresh every 5 seconds
✅ Modern, responsive UI
✅ Color-coded severity levels

