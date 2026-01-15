pipeline {
    agent any

    environment {
        IMGNAME = 'python_link_shortener'
        PYTHON_IMAGE = 'python:3.11-slim'
        // Using the K8s internal DNS name for SonarQube
        SONAR_URL = 'http://sonarqube.sonarqube.svc.cluster.local:9000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    // Changed 'bat' to 'sh' and corrected the variable syntax
                    sh """
                    docker run --rm -e SONAR_HOST_URL=${SONAR_URL} -e SONAR_TOKEN=${SONAR_TOKEN} -v "\$(pwd)":/usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=python_link_shortener
                    """
                }
            }
        }

        stage('Install dependencies') {
            steps {
                // Changed 'bat' to 'sh'
                sh """
                docker run --rm -v "\$(pwd)":/workspace -w /workspace ${PYTHON_IMAGE} sh -c "python3 -m pip install --upgrade pip && pip3 install -r requirements.txt pytest flake8 bandit"
                """
            }
        }
        
        stage('Build Docker Image') {
            steps {
                // Changed 'bat' to 'sh'
                sh "docker build -t ${IMGNAME}:latest ."
            }
        }
    }
}