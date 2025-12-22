# 🛡️ Container Vulnerability Scanner (Kubernetes Edition)

A full-stack DevSecOps application designed to scan Docker images for security vulnerabilities using **Trivy**. The project is containerized and orchestrated entirely on **Kubernetes (KinD)** following a microservices architecture.

## 🚀 Features

- **Microservices Architecture**: Separated concerns into API, Worker, Database, and Dashboard.
- **Event-Driven Scanning**: Uses Kubernetes **Jobs** to spin up ephemeral workers for each scan request (Resource Efficient).
- **Vulnerability Database**: Stores detailed scan results (Critical, High, Medium, Low) in **PostgreSQL**.
- **Interactive Dashboard**: A modern **React** UI to submit scans and visualize vulnerability data (Packages, Versions, Fixes).
- **Security**: Utilizes **Trivy** (by Aqua Security) for comprehensive vulnerability detection.

## 🛠️ Tech Stack

- **Infrastructure**: Kubernetes (KinD), Docker.
- **Backend**: FastAPI (Python).
- **Worker**: Python script wrapping Trivy CLI (Runs as K8s Job).
- **Frontend**: React.js.
- **Database**: PostgreSQL.
- **Orchestration**: Kubernetes Manifests (Deployments, Services, Jobs, PVCs).

## 🏗️ Architecture Workflow

1.  **Dashboard**: User submits an image name (e.g., `nginx:alpine`).
2.  **API**: Receives the request and triggers a **Kubernetes Job**.
3.  **Worker (Job)**:
    - Pulls the image inside the cluster.
    - Runs `trivy image`.
    - Parses the JSON report.
    - Saves individual vulnerabilities to PostgreSQL.
4.  **Dashboard**: Polls the API to display the results in real-time.

## ⚙️ Setup & Installation

### Prerequisites
- Docker
- Kubernetes CLI (`kubectl`)
- KinD (Kubernetes in Docker)

### 1. Setup Cluster
Create a local Kubernetes cluster using KinD:
```bash
kind create cluster --name vuln-scanner
2. Build Docker Images
Since we use a local KinD cluster, we build images locally and load them directly into the cluster nodes.

Bash

# Build Database (Optional if using standard postgres image)
# Build API
cd api
docker build -t scanner-api:latest .
cd ..

# Build Worker
cd worker
DOCKER_BUILDKIT=0 docker build -t vuln-scanner-worker:latest .
cd ..

# Build Dashboard
cd dashboard
DOCKER_BUILDKIT=0 docker build -t scanner-dashboard:latest .
cd ..
3. Load Images into KinD
Transfer the built images to the KinD nodes:

Bash

kind load docker-image scanner-api:latest --name vuln-scanner
kind load docker-image vuln-scanner-worker:latest --name vuln-scanner
kind load docker-image scanner-dashboard:latest --name vuln-scanner
4. Deploy to Kubernetes
Apply the manifests to create deployments and services:

Bash

# 1. Database & Storage
kubectl apply -f k8s/db-pvc.yaml
kubectl apply -f k8s/db-deployment.yaml
kubectl apply -f k8s/db-service.yaml

# 2. API (Backend)
kubectl apply -f k8s/scan-job-role.yaml  # Permissions to create Jobs
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml

# 3. Dashboard (Frontend)
kubectl apply -f k8s/dashboard-deployment.yaml
kubectl apply -f k8s/dashboard-service.yaml
5. Access the Application
Once all pods are running (kubectl get pods), access the dashboard via the NodePort:

URL: http://localhost:30280 (or your Node IP)

📸 Usage Guide
Open the Dashboard.

Enter a Docker image name (e.g., redis, python:3.9-slim).

Click Start Scan.

The status will update from PENDING -> RUNNING -> DONE.

Click on the completed scan to view the list of vulnerabilities, severity levels, and fix versions.

📂 Project Structure
container-vuln-scanner/
├── api/                  # FastAPI Application
├── worker/               # Python/Trivy Worker Script
├── dashboard/            # React Frontend
├── k8s/                  # Kubernetes Manifests
│   ├── api-deployment.yaml
│   ├── db-deployment.yaml
│   ├── dashboard-deployment.yaml
│   ├── scan-job-template.yaml
│   └── ...
└── README.md

