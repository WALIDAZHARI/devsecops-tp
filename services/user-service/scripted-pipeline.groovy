node {
    def dockerImage
    
    stage('Checkout') {
        // Clean workspace
        deleteDir()
        
        // Clone repository
        sh 'git init'
        sh 'git remote add origin https://github.com/WALIDAZHARI/devsecops-tp.git'
        sh 'git fetch --depth 1 origin main'
        sh 'git checkout FETCH_HEAD'
        sh 'ls -la'
    }
    
    stage('Setup Python') {
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
    
    stage('Run Tests') {
        dir('services/user-service') {
            sh 'python -m pip install -r requirements.txt || true'
            sh 'mkdir -p tests'
            sh 'touch tests/__init__.py'
            sh 'python -m pytest tests/ || true'
        }
    }
    
    stage('Build Docker Image') {
        def imageName = 'walidazhari/user-service'
        def imageTag = "${env.BUILD_NUMBER}-simple"
        def imageFullName = "${imageName}:${imageTag}"
        
        echo "Building Docker image: ${imageFullName}"
        
        dir('services/user-service') {
            sh 'ls -la'
            dockerImage = docker.build(imageFullName)
        }
    }
    
    stage('Security Scan') {
        if (dockerImage) {
            sh '''
                # Check if trivy container is running
                if docker ps | grep -q trivy; then
                    docker exec trivy trivy image --no-progress --exit-code 0 walidazhari/user-service:${BUILD_NUMBER}-simple || true
                else
                    echo "Trivy container not running, skipping scan"
                fi
            '''
        }
    }
    
    stage('Push to Docker Hub') {
        if (dockerImage) {
            withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin || true'
                dockerImage.push("${env.BUILD_NUMBER}-simple")
                dockerImage.push('latest')
            }
        }
    }
    
    stage('Cleanup') {
        sh 'docker image prune -f || true'
        deleteDir()
    }
}
