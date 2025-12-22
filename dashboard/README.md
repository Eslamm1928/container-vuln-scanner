# Vulnerability Scanner Dashboard

Modern React-based dashboard for the Container Vulnerability Scanner.

## Features

- ✅ Submit new scans
- ✅ View all scans with real-time updates
- ✅ View vulnerabilities for each scan
- ✅ Group vulnerabilities by severity (CRITICAL, HIGH, MEDIUM, LOW)
- ✅ Auto-refresh every 5 seconds
- ✅ Modern, responsive UI
- ✅ Status badges with icons
- ✅ Color-coded severity indicators

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Install Dependencies

```bash
cd dashboard
npm install
```

### Run Development Server

```bash
npm start
```

The app will open at http://localhost:3000

### Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

## Docker Build

```bash
cd dashboard
docker build -t scanner-dashboard:1.0 .
docker run -d --name scanner-dashboard -p 8080:80 scanner-dashboard:1.0
```

## Project Structure

```
dashboard/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/
│   │   ├── ScanForm.js     # Form to submit new scans
│   │   ├── ScanList.js     # List of all scans
│   │   └── VulnerabilityList.js  # Vulnerabilities viewer
│   ├── services/
│   │   └── api.js          # API service functions
│   ├── App.js              # Main app component
│   ├── App.css             # App styles
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
└── Dockerfile              # Docker build configuration
```

## API Integration

The dashboard connects to the FastAPI backend:
- Default: `http://127.0.0.1:8000` (local development)
- Kubernetes: `http://scanner-api:8000` (containerized)

## Components

### ScanForm
- Input field for container image name
- Submit button
- Success/error messages

### ScanList
- Displays all scans
- Status badges (PENDING, RUNNING, DONE, FAILED)
- Click to view vulnerabilities
- Auto-refreshes every 5 seconds

### VulnerabilityList
- Shows vulnerabilities for selected scan
- Groups by severity
- Summary statistics
- Detailed package and version information

