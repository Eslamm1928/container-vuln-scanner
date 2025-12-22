#!/bin/bash
echo "🔵 Opening Dashboard Tunnel..."
echo "👉 Click here: http://localhost:8080"
kubectl port-forward svc/scanner-dashboard 8080:80
