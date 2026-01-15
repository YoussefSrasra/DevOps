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
        stage('Install dependencies') {
            steps {
                bat '''
                docker run --rm -v "%cd%":/workspace -w /workspace %PYTHON_IMAGE% sh -c "python3 -m pip install --upgrade pip && pip3 install -r requirements.txt pytest flake8 bandit"
                '''
            }
        }
        stage('Test') {
            steps {
                bat '''
                docker run --rm -v "%cd%":/workspace -w /workspace %PYTHON_IMAGE% sh -c "pip3 install -r requirements.txt pytest && pytest"
                '''
            }
        }
        stage('Lint') {
            steps {
                bat '''
                docker run --rm -v "%cd%":/workspace -w /workspace %PYTHON_IMAGE% sh -c "pip3 install flake8 && flake8 app.py"
                '''
            }
        }
        stage('Security Scan (SAST)') {
            steps {
                bat '''
                docker run --rm -v "%cd%":/workspace -w /workspace %PYTHON_IMAGE% sh -c "pip3 install bandit && bandit -r app.py"
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
