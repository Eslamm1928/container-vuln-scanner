FROM python:3.10-slim

WORKDIR /app

# 1. تسطيب الأدوات الأساسية وتنزيل Trivy مباشرة
# بنستخدم dpkg عشان نسطب ملف .deb مباشرة وده أضمن حل
RUN apt-get update && apt-get install -y wget && \
    wget https://github.com/aquasecurity/trivy/releases/download/v0.50.1/trivy_0.50.1_Linux-64bit.deb && \
    dpkg -i trivy_0.50.1_Linux-64bit.deb && \
    rm trivy_0.50.1_Linux-64bit.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. تسطيب مكتبات البايثون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. نقل كود الوركر
COPY worker.py .

# 4. أمر التشغيل
CMD ["python", "worker.py"]



