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
        +-------------+------------+-------------+--------------+------------+
        |             |                          |                           |
        v             v                          v                           v
  +-----+----+  +------+-----+         +---------+-----+             +-------+------+
  |  Build   |  | SAST (Sonar)|        | DAST (Trivy)  |             | Secrets Mgmt  |
  +-----+----+  +------+-----+         +---------+-----+             |   (Vault)     |
        |             |                          |                  +-------+------+
        +------+------+                          |                          |
               |                                 |                          |
               v                                 v                          v
        +------+---------------------------------+--------------------------+------+
        |                    Docker Image Registry (DockerHub)                    |
        +----------------------+--------------------------+------------------------+
                               |                          |
                               v                          v
                    +----------+-----------+      +------+--------+
                    | Kubernetes Cluster   |      | Monitoring    |
                    +----------+-----------+      | Stack         |
                               |                  +------+--------+
               +---------------+-----------+             |
               |                           |             v
       +-------+--------+         +--------+-------+   Grafana
       | user-service  |         | product-service| 
       +----------------+         +----------------+
                                              |
                                              v
                                         Prometheus
```

---

## 📂 Project Structure

```
devsecops-tp/
├── user-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── Jenkinsfile
├── product-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── Jenkinsfile
├── global-pipeline/              # (To be added later)
│   └── Jenkinsfile               # Full DevSecOps orchestration
├── README.md
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

## 🛡️ Step 5: Trivy for Image Scanning

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

## 🚨 Step 6: Nuclei for Vulnerability Scanning

```bash
brew install projectdiscovery/tap/nuclei
```

### Example Scan:

```bash
nuclei -u http://localhost:5555
nuclei -u http://localhost:5556
```

---

## 🔐 Step 7: Vault for Secrets Management

```bash
docker run --cap-add=IPC_LOCK -d --name=dev-vault \
  -p 8200:8200 vault
```

* Access: [http://localhost:8200](http://localhost:8200)

---

## ☸️ Step 8: Kubernetes (K8s)

* Use Minikube or Docker Desktop K8s
* Write `deployment.yaml` and `service.yaml` for both services

---

## 📊 Step 9: Monitoring with Prometheus & Grafana

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

* Access: [http://localhost:3000](http://localhost:3000)
* Login: admin / admin

---

## 📦 Jenkins Pipeline Example

### `user-service/Jenkinsfile`

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t user-service ./user-service'
            }
        }
        stage('Trivy Scan') {
            steps {
                sh 'trivy image user-service'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                echo 'SonarQube analysis step here'
            }
        }
        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh 'docker login -u $USER -p $PASS'
                    sh 'docker push user-service'
                }
            }
        }
        stage('Nuclei Scan') {
            steps {
                sh 'nuclei -u http://user-service-url'
            }
        }
    }
}
```

---

### `product-service/Jenkinsfile`

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t product-service ./product-service'
            }
        }
        stage('Trivy Scan') {
            steps {
                sh 'trivy image product-service'
            }
        }
        stage('SonarQube Analysis') {
            steps {
                echo 'SonarQube analysis step here'
            }
        }
        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', passwordVariable: 'PASS', usernameVariable: 'USER')]) {
                    sh 'docker login -u $USER -p $PASS'
                    sh 'docker push product-service'
                }
            }
        }
        stage('Nuclei Scan') {
            steps {
                sh 'nuclei -u http://product-service-url'
            }
        }
    }
}
```

---

## ✅ Done So Far

* [x] Created both microservices
* [x] Added Jenkinsfiles for both services
* [x] Configured GitHub repositories
* [x] Installed and configured Jenkins
* [x] Added SonarQube and Trivy
* [x] Integrated Prometheus & Grafana
* [x] Replaced OWASP ZAP with Nuclei

## 🚧 In Progress

* [ ] Full CI/CD Pipeline orchestration
* [ ] K8s deployment files and automation
* [ ] Vault integration for secrets
* [ ] Jenkins global pipeline file
* [ ] Nuclei configuration with templates

---

## 📌 Contributor

* **Walid Azhari** - DevSecOps Engineer in training

Let’s build security into DevOps — by design!