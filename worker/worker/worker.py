import os
import json
import subprocess
import psycopg2

# إعدادات الاتصال بالداتابيز
DB_HOST = os.getenv("DB_HOST", "postgres-service")
DB_NAME = os.getenv("DB_NAME", "vuln_scanner")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_PORT = os.getenv("DB_PORT", "5432")

SCAN_ID = os.getenv("SCAN_ID")
IMAGE_NAME = os.getenv("IMAGE_NAME")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )

def main():
    print(f"Starting scan for image: {IMAGE_NAME} (Scan ID: {SCAN_ID})")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. ضمان وجود جدول الثغرات (للأمان)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id SERIAL PRIMARY KEY,
            scan_id INTEGER,
            package_name TEXT,
            severity TEXT,
            description TEXT,
            fixed_version TEXT
        );
    """)
    conn.commit()
    
    # تحديث الحالة إلى Running
    cur.execute("UPDATE scans SET status='RUNNING' WHERE id=%s", (SCAN_ID,))
    conn.commit()
    
    try:
        # تشغيل Trivy
        trivy_cmd = [
            "trivy", "image", 
            "--format", "json", 
            "--output", "result.json",
            "--timeout", "20m",
            "--scanners", "vuln",
            IMAGE_NAME
        ]
        
        print("Running Trivy command...")
        subprocess.run(trivy_cmd, check=True)
        
        print("Reading results...")
        with open("result.json", "r") as f:
            scan_results = json.load(f)
        
        # حفظ JSON الخام (اختياري)
        cur.execute(
            "UPDATE scans SET status='DONE', results=%s WHERE id=%s", 
            (json.dumps(scan_results), SCAN_ID)
        )
        
        # ---------------------------------------------------------
        # التعديل الجديد: تفريغ الثغرات في جدول vulnerabilities
        # ---------------------------------------------------------
        print("Parsing and saving individual vulnerabilities...")
        vuln_count = 0
        
        # التأكد من وجود نتائج
        if "Results" in scan_results:
            for result in scan_results["Results"]:
                if "Vulnerabilities" in result:
                    for vuln in result["Vulnerabilities"]:
                        pkg_name = vuln.get("PkgName", "Unknown")
                        severity = vuln.get("Severity", "UNKNOWN")
                        description = vuln.get("Description", "No description available")
                        fixed_version = vuln.get("FixedVersion", "N/A")
                        
                        # إدخال الثغرة في الجدول
                        cur.execute(
                            """
                            INSERT INTO vulnerabilities 
                            (scan_id, package_name, severity, description, fixed_version) 
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (SCAN_ID, pkg_name, severity, description, fixed_version)
                        )
                        vuln_count += 1
        
        conn.commit()
        print(f"Successfully saved {vuln_count} vulnerabilities to the database.")
        # ---------------------------------------------------------

    except subprocess.CalledProcessError as e:
        print(f"Trivy scan failed: {e}")
        error_json = json.dumps({"error": "Scan process failed", "details": str(e)})
        cur.execute("UPDATE scans SET status='FAILED', results=%s WHERE id=%s", (error_json, SCAN_ID))
        conn.commit()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        error_json = json.dumps({"error": str(e)})
        cur.execute("UPDATE scans SET status='FAILED', results=%s WHERE id=%s", (error_json, SCAN_ID))
        conn.commit()
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
