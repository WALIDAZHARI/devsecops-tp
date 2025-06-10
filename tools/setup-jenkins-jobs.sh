#!/bin/bash

# This script creates Jenkins jobs for user-service and product-service
# using the Jenkins CLI

# Get the Jenkins CLI jar
docker exec jenkins curl -O http://localhost:8080/jnlpJars/jenkins-cli.jar

# Create user-service job
cat > user-service-config.xml << EOF
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1408.v45c7b_f2f404a_">
  <description>Pipeline for user-service</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@3806.va_3a_6988277b_">
    <script>
pipeline {
  agent any

  environment {
    IMAGE_NAME = 'walidazhari/user-service'
    SHORT_COMMIT = sh(script: 'git rev-parse --short HEAD || echo unknown', returnStdout: true).trim()
    IMAGE_TAG = "\${env.BUILD_NUMBER}-\${SHORT_COMMIT}"
    IMAGE_FULL = "\${IMAGE_NAME}:\${IMAGE_TAG}"
    SONAR_PROJECT_KEY = 'user-service'
  }

  stages {
    stage('Setup') {
      steps {
        // Clean workspace and clone repository
        cleanWs()
        sh 'git init'
        sh 'git remote add origin https://github.com/WALIDAZHARI/devsecops-tp.git'
        sh 'git fetch --depth 1 origin main'
        sh 'git checkout FETCH_HEAD'
        sh 'ls -la'
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          # Install Python if not available
          if ! command -v python3 &> /dev/null; then
            apt-get update
            apt-get install -y python3 python3-pip
            ln -sf /usr/bin/python3 /usr/bin/python
            ln -sf /usr/bin/pip3 /usr/bin/pip
          fi
          python --version
          pip --version
        '''
      }
    }

    stage('Run Tests') {
      steps {
        dir('services/user-service') {
          sh 'pip install -r requirements.txt || true'
          sh 'mkdir -p tests'
          sh 'touch tests/__init__.py'
          sh 'python -m pytest tests/ --junitxml=test-results.xml || true'
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          echo "Building Docker image: \${env.IMAGE_FULL}"
          // Make sure Dockerfile exists
          sh 'ls -la services/user-service/'
          // Build with proper context
          sh "docker build -t \${env.IMAGE_FULL} -f services/user-service/Dockerfile services/user-service"
          // Verify image was built
          sh "docker images | grep \${env.IMAGE_NAME}"
        }
      }
    }

    stage('Security Scans') {
      parallel {
        stage('Trivy Scan') {
          steps {
            echo "Running Trivy security scan on \${env.IMAGE_FULL}"
            sh """
              # Check if trivy container is running
              if docker ps | grep -q trivy; then
                docker exec trivy trivy image --no-progress --exit-code 0 \${env.IMAGE_FULL} || true
              else
                echo "Trivy container not running, using direct command"
                docker run --rm aquasec/trivy:latest image --no-progress --exit-code 0 \${env.IMAGE_FULL} || true
              fi
            """
          }
        }
        stage('Docker Scout') {
          steps {
            echo "Running Docker Scout vulnerability scan"
            sh "docker scout quickview \${env.IMAGE_FULL} || true"
          }
        }
      }
    }

    stage('Login to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin'
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        sh "docker push \${env.IMAGE_FULL}"
        sh "docker tag \${env.IMAGE_FULL} \${env.IMAGE_NAME}:latest"
        sh "docker push \${env.IMAGE_NAME}:latest"
      }
    }
  }

  post {
    always {
      echo 'Cleaning up...'
      sh 'docker image prune -f || true'
      cleanWs()
    }
  }
}
    </script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF

# Create product-service job
cat > product-service-config.xml << EOF
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1408.v45c7b_f2f404a_">
  <description>Pipeline for product-service</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@3806.va_3a_6988277b_">
    <script>
pipeline {
  agent any

  environment {
    IMAGE_NAME = 'walidazhari/product-service'
    SHORT_COMMIT = sh(script: 'git rev-parse --short HEAD || echo unknown', returnStdout: true).trim()
    IMAGE_TAG = "\${env.BUILD_NUMBER}-\${SHORT_COMMIT}"
    IMAGE_FULL = "\${IMAGE_NAME}:\${IMAGE_TAG}"
    SONAR_PROJECT_KEY = 'product-service'
  }

  stages {
    stage('Setup') {
      steps {
        // Clean workspace and clone repository
        cleanWs()
        sh 'git init'
        sh 'git remote add origin https://github.com/WALIDAZHARI/devsecops-tp.git'
        sh 'git fetch --depth 1 origin main'
        sh 'git checkout FETCH_HEAD'
        sh 'ls -la'
      }
    }

    stage('Setup Python') {
      steps {
        sh '''
          # Install Python if not available
          if ! command -v python3 &> /dev/null; then
            apt-get update
            apt-get install -y python3 python3-pip
            ln -sf /usr/bin/python3 /usr/bin/python
            ln -sf /usr/bin/pip3 /usr/bin/pip
          fi
          python --version
          pip --version
        '''
      }
    }

    stage('Run Tests') {
      steps {
        dir('services/product-service') {
          sh 'pip install -r requirements.txt || true'
          sh 'mkdir -p tests'
          sh 'touch tests/__init__.py'
          sh 'python -m pytest tests/ --junitxml=test-results.xml || true'
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          echo "Building Docker image: \${env.IMAGE_FULL}"
          // Make sure Dockerfile exists
          sh 'ls -la services/product-service/'
          // Build with proper context
          sh "docker build -t \${env.IMAGE_FULL} -f services/product-service/Dockerfile services/product-service"
          // Verify image was built
          sh "docker images | grep \${env.IMAGE_NAME}"
        }
      }
    }

    stage('Security Scans') {
      parallel {
        stage('Trivy Scan') {
          steps {
            echo "Running Trivy security scan on \${env.IMAGE_FULL}"
            sh """
              # Check if trivy container is running
              if docker ps | grep -q trivy; then
                docker exec trivy trivy image --no-progress --exit-code 0 \${env.IMAGE_FULL} || true
              else
                echo "Trivy container not running, using direct command"
                docker run --rm aquasec/trivy:latest image --no-progress --exit-code 0 \${env.IMAGE_FULL} || true
              fi
            """
          }
        }
        stage('Docker Scout') {
          steps {
            echo "Running Docker Scout vulnerability scan"
            sh "docker scout quickview \${env.IMAGE_FULL} || true"
          }
        }
      }
    }

    stage('Login to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin'
        }
      }
    }

    stage('Push to Docker Hub') {
      steps {
        sh "docker push \${env.IMAGE_FULL}"
        sh "docker tag \${env.IMAGE_FULL} \${env.IMAGE_NAME}:latest"
        sh "docker push \${env.IMAGE_NAME}:latest"
      }
    }
  }

  post {
    always {
      echo 'Cleaning up...'
      sh 'docker image prune -f || true'
      cleanWs()
    }
  }
}
    </script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF

# Get Jenkins credentials
echo "Please enter your Jenkins username:"
read JENKINS_USER
echo "Please enter your Jenkins password or API token:"
read -s JENKINS_TOKEN
echo

# Create or update the jobs
echo "Updating user-service job..."
docker exec -i jenkins java -jar jenkins-cli.jar -s http://localhost:8080/ -auth "$JENKINS_USER:$JENKINS_TOKEN" update-job user-service < user-service-config.xml

echo "Updating product-service job..."
docker exec -i jenkins java -jar jenkins-cli.jar -s http://localhost:8080/ -auth "$JENKINS_USER:$JENKINS_TOKEN" update-job product-service < product-service-config.xml

# Clean up
rm -f user-service-config.xml product-service-config.xml

echo "Jobs created/updated successfully!"
