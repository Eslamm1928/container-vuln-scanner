# Deploy Trivy Kubernetes Jobs

## Quick Start

### 1. Deploy ConfigMaps (Scripts)

```bash
kubectl apply -f trivy-configmap.yaml
kubectl apply -f job-creator-script.yaml
kubectl apply -f job-watcher-script.yaml
```

### 2. Deploy RBAC (Permissions)

```bash
kubectl apply -f job-creator-rbac.yaml
kubectl apply -f job-watcher-rbac.yaml
```

### 3. Deploy Job Management Services

```bash
kubectl apply -f job-creator.yaml
kubectl apply -f job-watcher.yaml
```

### 4. Verify Deployment

```bash
# Check job creator
kubectl get pods -l app=job-creator
kubectl logs -l app=job-creator

# Check job watcher
kubectl get pods -l app=job-watcher
kubectl logs -l app=job-watcher
```

## How It Works

### Flow Diagram

```
API Request → Database (PENDING)
    ↓
Job Creator (polls DB)
    ↓
Creates Kubernetes Job
    ↓
Trivy Job Executes
    ↓
Updates Database (DONE/FAILED)
    ↓
Job Auto-deletes (5 min TTL)
```

### Components

1. **Job Creator**
   - Polls database every 5 seconds
   - Finds scans with status PENDING
   - Creates Kubernetes Job for each scan
   - Uses Kubernetes Python client

2. **Trivy Job**
   - Runs Trivy scan on specified image
   - Outputs results to JSON
   - Python script processes results
   - Updates database with vulnerabilities

3. **Job Watcher**
   - Monitors all Trivy jobs
   - Handles failed jobs
   - Updates scan status if needed

## Testing

### Submit a Scan

```bash
curl -X POST "http://<api-url>/scan" \
     -H "Content-Type: application/json" \
     -d '{"image_name": "nginx"}'
```

### Watch Jobs Being Created

```bash
# In one terminal
kubectl get jobs -l app=trivy-scanner -w

# In another terminal
kubectl logs -f -l app=job-creator
```

### Check Job Execution

```bash
# List jobs
kubectl get jobs -l app=trivy-scanner

# View job details
kubectl describe job trivy-scan-<scan-id>

# View job logs
kubectl logs job/trivy-scan-<scan-id>
```

## Troubleshooting

### Jobs Not Created

```bash
# Check job creator logs
kubectl logs -l app=job-creator

# Verify database connection
kubectl exec -it <job-creator-pod> -- python3 -c "
import psycopg2
conn = psycopg2.connect(host='postgres', database='vuln_scanner', user='postgres', password='root')
print('DB connection OK')
"
```

### Jobs Failing

```bash
# Check job logs
kubectl logs job/trivy-scan-<scan-id>

# Check job events
kubectl describe job trivy-scan-<scan-id>

# Verify Trivy image
kubectl run test-trivy --image=aquasec/trivy:latest --rm -it -- trivy --version
```

### RBAC Issues

```bash
# Test permissions
kubectl auth can-i create jobs --as=system:serviceaccount:default:job-creator-sa

# Check service account
kubectl get sa job-creator-sa
kubectl get rolebinding job-creator-binding
```

## Cleanup

### Remove Job Management

```bash
kubectl delete -f job-creator.yaml
kubectl delete -f job-watcher.yaml
kubectl delete -f job-creator-rbac.yaml
kubectl delete -f job-watcher-rbac.yaml
```

### Clean Up Completed Jobs

```bash
# Jobs auto-delete after 5 minutes (TTL)
# Or manually delete:
kubectl delete jobs -l app=trivy-scanner
```

## Migration from Worker Deployment

If you're migrating from the worker Deployment:

1. **Scale down worker**:
   ```bash
   kubectl scale deployment scanner-worker --replicas=0
   ```

2. **Deploy Job system** (follow steps above)

3. **Verify jobs are created** for new scans

4. **Remove worker deployment** (optional):
   ```bash
   kubectl delete deployment scanner-worker
   ```

## Notes

- Jobs have TTL of 5 minutes (auto-delete)
- Jobs retry up to 2 times on failure
- Each scan creates one independent Job
- Jobs run in parallel if multiple scans are pending
- Database is updated directly by the Job's Python script


