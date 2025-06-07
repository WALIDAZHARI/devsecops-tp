# DevSecOps Project - Microservices Pipeline

## 🧠 Project Overview

This project demonstrates a complete **DevSecOps CI/CD pipeline** for two interactive microservices:

* `user-service`
* `product-service`

It incorporates security and automation tools into the development lifecycle, from coding and building to testing, deploying, monitoring, and fixing vulnerabilities.

---

## 🧱 System Architecture

```
                                      +---------------------+
                                      |   Developers (You)  |
                                      +----------+----------+
                                                 |
                                                 v
                                   +-------------+--------------+
                                   |       Git / GitHub         |
                                   +-------------+--------------+
                                                 |
                                                 v
                                   +-------------+--------------+
                                   |         Jenkins CI         |
                                   +-------------+--------------+
                                                 |
                 +------------------+------------------+-----------------+
                 |                  |                  |                 |
                 v                  v                  v                 v
        +--------+------+  +--------+--------+ +--------+------+ +--------+--------+
        |   Build & Test |  |   SAST (SonarQ) | |  DAST (Trivy) | | Secrets (Vault) |
        +--------+------+  +--------+--------+ +--------+------+ +--------+--------+
                 |                                                           |
                 v                                                           v
        +--------+------------------------------------------------------------+
        |                        Docker Image Registry (Local/DockerHub)      |
        +-------------------------------+-------------------------------------+
                                        |
                                        v
                             +----------+-----------+
                             |   Kubernetes Cluster |
                             +----------+-----------+
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
                 v                      v                      v
        +--------+--------+   +---------+---------+  +---------+---------+
        |  user-service   |   |  product-service  |  |  Monitoring Tools  |
        +--------+--------+   +---------+---------+  +---------+---------+
                                                |              |
                                                v              v
                                           Prometheus       Grafana
```

---

## 📂 Project Structure

```
devsecops-tp/
├── user-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── product-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── Jenkinsfile
├── docker-compose.yml (optional)
└── README.md
```

---

## 🚀 Step-by-Step Instructions

### ✅ Step 1: Git Initialization

```bash
cd devsecops-tp
git init
git remote add origin https://github.com/your-username/devsecops-tp.git
git add .
git commit -m "Initial commit"
git push -u origin master
```

---

## 🧪 Step 2: Run Microservices

### Build Images

```bash
docker build -t user-service ./user-service
docker build -t product-service ./product-service
```

### Run Containers

```bash
docker run -d -p 5555:5555 --name user-service user-service
docker run -d -p 5556:5556 --name product-service product-service
```

### Test with Postman

* `GET http://localhost:5555/users`
* `POST http://localhost:5555/users`
* `GET http://localhost:5556/products`
* `POST http://localhost:5556/products`

---

## ⚙️ Step 3: Jenkins Installation (with Docker)

```bash
docker run -d \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  --name jenkins \
  jenkins/jenkins:lts
```

* Access: [http://localhost:8080](http://localhost:8080)
* Unlock password:

```bash
docker exec -it jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## 🔐 Step 4: SonarQube for SAST

```bash
docker run -d --name sonarqube \
  -p 9000:9000 sonarqube:community
```

* Access: [http://localhost:9000](http://localhost:9000)
* Default login: admin / admin

---

## 🛡️ Step 5: Trivy for DAST

### Install:

```bash
brew install aquasecurity/trivy/trivy
```

### Scan Images:

```bash
trivy image user-service
trivy image product-service
```

---

## 🔐 Step 6: Vault (Secrets Management)

```bash
docker run --cap-add=IPC_LOCK -d --name=dev-vault \
  -p 8200:8200 vault
```

---

## ☸️ Step 7: Kubernetes

* Use **Minikube** or **Docker Desktop K8s**
* Write deployment and service YAMLs for both microservices

---

## 📊 Step 8: Monitoring

### Prometheus

```bash
docker run -d -p 9090:9090 --name prometheus \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Grafana

```bash
docker run -d -p 3000:3000 --name=grafana grafana/grafana
```

* Login: admin / admin

---

## 📦 Final Jenkins Pipeline (Sample)

**Jenkinsfile**

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t user-service ./user-service'
                sh 'docker build -t product-service ./product-service'
            }
        }
        stage('SAST') {
            steps {
                sh 'sonar-scanner ...'
            }
        }
        stage('DAST') {
            steps {
                sh 'trivy image user-service'
                sh 'trivy image product-service'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploy to K8s or Docker Compose'
            }
        }
    }
}
```

---

## 🛠️ Coming Next

* [ ] Finalize `Jenkinsfile`
* [ ] Add unit tests
* [ ] Simulate vulnerabilities
* [ ] Monitor live services
* [ ] Secure secrets with Vault

---

## 📌 Contributors

* **Walid Azhari** - DevSecOps Engineer in training

---

## ✅ Done So Far:

* [x] Microservices up
* [x] Git initialized
* [x] Jenkins + SonarQube working

## 🚧 In Progress:

* [ ] Full pipeline automation
* [ ] Vulnerability injection & fixing
* [ ] Monitoring integration
* [ ] Vault integration

---

Let’s build security into DevOps — by design!