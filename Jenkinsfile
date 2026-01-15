pipeline {
    agent any

    environment {
        IMGNAME = 'python_link_shortener'
        PYTHON_IMAGE = 'python:3.11-slim'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // Make sure the credential ID 'sonar-token' exists in Jenkins -> Credentials
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    bat """
                    docker run --rm ^
                    -e SONAR_HOST_URL=http://host.docker.internal:30091 ^
                    -e SONAR_TOKEN=%SONAR_TOKEN% ^
                    -v "%cd%":/usr/src ^
                    sonarsource/sonar-scanner-cli ^
                    -Dsonar.projectKey=my-bankend-app ^
                    -Dsonar.sources=.
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