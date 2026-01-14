pipeline {
    agent {
    docker {
      image 'python:3.11-slim'
    }
  }

    environment {
        IMGNAME = 'python_link_shortener'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Install dependencies') {
            steps {
                sh 'python3 -m pip install --upgrade pip'
                sh 'pip3 install -r requirements.txt pytest flake8 bandit'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest'
            }
        }
        stage('Lint') {
            steps {
                sh 'flake8 app.py test_app.py'
            }
        }
        stage('Security Scan (SAST)') {
            steps {
                sh 'bandit -r app.py'
            }
        }
        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMGNAME:latest .'
            }
        }
    }
}
