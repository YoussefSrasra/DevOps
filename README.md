# 🚀 Link Shortener - DevSecOps Pipeline

A professional-grade **DevSecOps** project featuring a Python Flask application, fully automated through a Jenkins CI/CD pipeline, secured with SAST/DAST, and monitored via Prometheus and Grafana on Kubernetes.



## 🛠 Tech Stack
* **Application:** Python 3.11 (Flask)
* **CI/CD:** Jenkins (Pipeline as Code)
* **Security (SAST):** SonarQube
* **Security (DAST):** OWASP ZAP
* **Containerization:** Docker
* **Orchestration:** Kubernetes (K3s / Docker Desktop)
* **Monitoring:** Prometheus & Grafana
* **Database:** PostgreSQL (for SonarQube)

---

## 🏗 Pipeline Architecture
The Jenkins pipeline (`Jenkinsfile`) automates the following lifecycle:

1.  **Checkout:** Pulls the latest code from the Git repository.
2.  **SonarQube Analysis (SAST):** Scans source code for vulnerabilities, bugs, and maintainability issues.
3.  **Install Dependencies:** Isolated environment setup to verify `requirements.txt`.
4.  **Build Docker Image:** Packages the application with a unique version tag (`BUILD_NUMBER`).
5.  **DAST Scan (OWASP ZAP):** Performs a dynamic security scan on the running application to identify runtime threats like missing security headers.
6.  **Push to Registry:** Authenticates and pushes the verified image to Docker Hub (`hadilt/devops_project`).
7.  **Deploy to Kubernetes:** Triggers a rolling update of the `devops-backend` deployment.
8.  **Verify & Smoke Test:** Confirms the deployment was successful and the endpoint is reachable.

---

## 🚀 How to Run the Project

### 1. Prerequisites
* **Docker Desktop** with Kubernetes enabled.
* **Jenkins** installed locally with the following credentials:
    * `sonar-token`: Secret text for SonarQube.
    * `docker-hub-credentials`: Username/Password for Docker Hub.

### 2. Infrastructure Setup
Deploy the environment from the `k8s/` directory. **Note:** PVCs ensure your data (Sonar projects/DB) persists even after shutdown.

```powershell
# Create the namespace for security tools
kubectl create namespace sonarqube

# Deploy the stack
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/sonarqube.yaml
kubectl apply -f k8s/prometheus-rbac.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```
## 📊 Accessing the Tools

| Service | Local URL | Port Type |
| :--- | :--- | :--- |
| **Flask Application** | [http://localhost:30001](http://localhost:30001) | NodePort |
| **SonarQube** | [http://localhost:30091](http://localhost:30091) | NodePort |
| **Prometheus** | [http://localhost:30090](http://localhost:30090) | NodePort |
| **Grafana** | [http://localhost:30002](http://localhost:30002) | NodePort |

---

## 🔒 Security & Monitoring
* **SAST:** Integrated SonarQube scans provide a Quality Gate for every code change.
* **DAST:** Automated OWASP ZAP scans generate a `zap_report.html` artifact stored in Jenkins.
* **Monitoring:** Prometheus scrapes application metrics via Kubernetes Service Discovery. Grafana visualizes these metrics for real-time performance tracking.

---

## 🧹 Deactivation & Persistence

To stop the application while **keeping your data safe** (retaining SonarQube projects and Database records):

```powershell
kubectl delete deployment --all
kubectl delete service --all
```

To completely remove all resources including data:
```powershell
kubectl delete ns sonarqube
kubectl delete pvc --all
```
