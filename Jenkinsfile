pipeline {
    agent any
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
                sh '''
                if ! command -v python3 >/dev/null 2>&1; then 
                  echo "Python3 not found, installing...";
                  if [ -x "$(command -v apt-get)" ]; then sudo apt-get update && sudo apt-get install -y python3 python3-pip;
                  elif [ -x "$(command -v apk)" ]; then sudo apk add --no-cache python3 py3-pip;
                  elif [ -x "$(command -v yum)" ]; then sudo yum install -y python3 python3-pip;
                  else echo "No supported package manager found!"; exit 1; fi;
                fi
                python3 -m pip install --upgrade pip
                pip3 install -r requirements.txt pytest flake8 bandit
                '''
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
