# Kubernetes Jobs Implementation for Trivy Scans

This directory contains the Kubernetes Job-based implementation for Trivy vulnerability scanning.

## Architecture

Instead of a continuous worker Deployment, scans are executed as Kubernetes Jobs:
- **Job Creator**: Watches for PENDING scans and creates Kubernetes Jobs
- **Trivy Jobs**: Each scan runs as a separate Kubernetes Job
- **Job Watcher**: Monitors job completion and handles failures
- **Auto-cleanup**: Jobs are automatically deleted after 5 minutes (TTL)

## Files

### Core Job Files
- `trivy-job-template.yaml` - Template for Trivy scan jobs
- `trivy-configmap.yaml` - ConfigMap with database update script

### Job Management
- `job-creator.yaml` - Deployment that creates jobs for PENDING scans
- `job-creator-script.yaml` - ConfigMap with job creation logic
- `job-creator-rbac.yaml` - RBAC permissions for job creation

- `job-watcher.yaml` - Deployment that monitors job status
- `job-watcher-script.yaml` - ConfigMap with job monitoring logic
- `job-watcher-rbac.yaml` - RBAC permissions for job watching

## Deployment Order

1. **Deploy ConfigMaps**:
   ```bash
   kubectl apply -f trivy-configmap.yaml
   kubectl apply -f job-creator-script.yaml
   kubectl apply -f job-watcher-script.yaml
   ```

2. **Deploy RBAC**:
   ```bash
   kubectl apply -f job-creator-rbac.yaml
   kubectl apply -f job-watcher-rbac.yaml
   ```

3. **Deploy Job Management Services**:
   ```bash
   kubectl apply -f job-creator.yaml
   kubectl apply -f job-watcher.yaml
   ```

## How It Works

1. **API receives scan request** → Creates scan record with status PENDING
2. **Job Creator** polls database → Finds PENDING scans
3. **Job Creator** creates Kubernetes Job → One Job per scan
4. **Trivy Job runs** → Scans image and updates database
5. **Job Watcher** monitors → Handles failures if needed
6. **Job auto-deletes** → After 5 minutes (TTL)

## Benefits

- ✅ **Scalable**: Each scan runs independently
- ✅ **Resource efficient**: Jobs only consume resources when running
- ✅ **Fault tolerant**: Jobs can retry on failure
- ✅ **Auto-cleanup**: Jobs are automatically deleted
- ✅ **Kubernetes native**: Uses proper K8s Job resources

## Monitoring

```bash
# List all scan jobs
kubectl get jobs -l app=trivy-scanner

# Watch jobs
kubectl get jobs -l app=trivy-scanner -w

# View job logs
kubectl logs job/trivy-scan-1

# Check job creator logs
kubectl logs -l app=job-creator

# Check job watcher logs
kubectl logs -l app=job-watcher
```

## Troubleshooting

### Jobs not being created
```bash
# Check job creator logs
kubectl logs -l app=job-creator

# Verify RBAC permissions
kubectl auth can-i create jobs --as=system:serviceaccount:default:job-creator-sa
```

### Jobs failing
```bash
# Check job logs
kubectl logs job/trivy-scan-<scan-id>

# Check job status
kubectl describe job trivy-scan-<scan-id>
```

### Database connection issues
```bash
# Verify PostgreSQL is accessible
kubectl exec -it <postgres-pod> -- psql -U postgres -d vuln_scanner -c "SELECT * FROM scans LIMIT 5;"
```


