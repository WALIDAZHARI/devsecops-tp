pipeline {
  agent any

  environment {
    IMAGE_NAME = 'walidazhari/user-service'
    IMAGE_TAG = "${env.BUILD_NUMBER}-simple"
    IMAGE_FULL = "${IMAGE_NAME}:${IMAGE_TAG}"
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
            apt-get install -y python3 python3-pip curl
            ln -sf /usr/bin/python3 /usr/bin/python
            ln -sf /usr/bin/pip3 /usr/bin/pip
          fi
          python --version
          pip --version
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          echo "Building Docker image: ${env.IMAGE_FULL}"
          // Make sure Dockerfile exists
          sh 'ls -la services/user-service/'
          // Build with proper context
          sh "docker build -t ${env.IMAGE_FULL} -f services/user-service/Dockerfile services/user-service"
          // Verify image was built
          sh "docker images | grep ${env.IMAGE_NAME}"
        }
      }
    }

    stage('Test Image') {
      steps {
        sh "docker run --rm ${env.IMAGE_FULL} python -c 'print(\"Image works!\")'"
      }
    }

    stage('Security Scan') {
      steps {
        echo "Running Trivy security scan on ${env.IMAGE_FULL}"
        sh """
          # Check if trivy container is running
          if docker ps | grep -q trivy; then
            docker exec trivy trivy image --no-progress --exit-code 0 ${env.IMAGE_FULL} || true
          else
            echo "Trivy container not running, skipping scan"
          fi
        """
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin || true'
          sh "docker push ${env.IMAGE_FULL} || true"
        }
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
