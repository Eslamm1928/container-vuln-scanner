import os
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kubernetes import client, config

app = FastAPI(title="Container Vulnerability Scanner API")

# إعدادات الكلاستر
try:
    config.load_incluster_config()
except:
    try:
        config.load_kube_config()
    except:
        print("Warning: Could not load Kubernetes config.")

# إعدادات الداتابيز
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "vuln_scanner")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_PORT = os.getenv("DB_PORT", "5432")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )

class ScanRequest(BaseModel):
    image_name: str

def create_k8s_job(scan_id, image_name):
    batch_v1 = client.BatchV1Api()
    job_name = f"scan-job-{scan_id}"
    
    container = client.V1Container(
        name="scanner-worker",
        image="vuln-scanner-worker:latest",
        image_pull_policy="Never",
        env=[
            client.V1EnvVar(name="SCAN_ID", value=str(scan_id)),
            client.V1EnvVar(name="IMAGE_NAME", value=image_name),
            client.V1EnvVar(name="DB_HOST", value="postgres-service"),
            client.V1EnvVar(name="DB_PASSWORD", value="root")
        ]
    )

    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "scanner-worker"}),
        spec=client.V1PodSpec(restart_policy="Never", containers=[container])
    )

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(template=template, ttl_seconds_after_finished=60)
    )

    batch_v1.create_namespaced_job(body=job, namespace="default")

@app.get("/")
def health():
    return {"status": "API running"}

@app.post("/scan")
def scan_image(request: ScanRequest):
    image_name = request.image_name
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("INSERT INTO images (name, tag) VALUES (%s, %s) RETURNING id;", (image_name, "latest"))
        image_id = cur.fetchone()[0]

        cur.execute("INSERT INTO scans (image_id, status) VALUES (%s, %s) RETURNING id;", (image_id, "PENDING"))
        scan_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()

        create_k8s_job(scan_id, image_name)

        return {"status": "queued", "scan_id": scan_id, "job_triggered": True}

    except Exception as e:
        print("Error:", e)
        return {"status": "error", "detail": str(e)}

# --- الدوال التي كانت ناقصة ---

@app.get("/scans")
def get_scans():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # نجيب البيانات مع اسم الصورة
        query = """
            SELECT scans.id, images.name, scans.status, scans.scan_date 
            FROM scans 
            JOIN images ON scans.image_id = images.id 
            ORDER BY scans.id DESC;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "image_name": row[1],
                "status": row[2],
                "scan_date": str(row[3])
            })
        
        cur.close()
        conn.close()
        return results # يرجع ليست مليانة أو فاضية، عمره ما يرجع null
    except Exception as e:
        print(f"Error fetching scans: {e}")
        return []

@app.get("/scans/{scan_id}/vulnerabilities")
def get_vulns(scan_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT package_name, severity, description, fixed_version 
            FROM vulnerabilities 
            WHERE scan_id = %s
        """, (scan_id,))
        rows = cur.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "package_name": row[0],
                "severity": row[1],
                "description": row[2],
                "fixed_version": row[3]
            })
            
        cur.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Error fetching vulns: {e}")
        return []
