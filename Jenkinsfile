pipeline {
    agent any

    environment {
        IMGNAME = 'python_link_shortener'
        PYTHON_IMAGE = 'python:3.11-slim'
        // Pointing to your SonarQube service inside Kubernetes
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
                // This uses the Secret Text credential you created
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    bat """
                    docker run --rm -e SONAR_HOST_URL=${SONAR_URL} -e SONAR_TOKEN=%SONAR_TOKEN% -v "%cd%":/usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=python_link_shortener
                    """
                }
            }
        }

        stage('Install dependencies') {
            steps {
                bat '''
                docker run --rm -v "%cd%":/workspace -w /workspace %PYTHON_IMAGE% sh -c "python3 -m pip install --upgrade pip && pip3 install -r requirements.txt pytest flake8 bandit"
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMGNAME%:latest .'
            }
        }
    }
}