pipeline {
    agent any

    environment {
        IMGNAME = 'python_link_shortener'
        PYTHON_IMAGE = 'python:3.11-slim'
        DOCKER_REGISTRY = 'hadilt'
        IMAGE_TAG = "${BUILD_NUMBER}"
        KUBE_NAMESPACE = 'production'
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
                    -Dsonar.projectKey=my-backend-app ^
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
                bat 'docker build -t %IMGNAME%:latest -t %IMGNAME%:%IMAGE_TAG% .'
            }
        }

        stage('DAST Scan (OWASP ZAP)') {
            steps {
                script {
                    bat """
                        docker run --rm ^
                        -v "%cd%":/zap/wrk/:rw ^
                        -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py ^
                        -t http://host.docker.internal:30001 ^
                        -r zap_report.html ^
                        -I 
                        """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'zap_report.html', fingerprint: true
                }
            }
        }

        // ==================== CD STAGES ====================
        
        stage('Push to Docker Registry') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', 
                                                       usernameVariable: 'DOCKER_USER', 
                                                       passwordVariable: 'DOCKER_PASS')]) {
                        bat '''
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker tag %IMGNAME%:latest %DOCKER_REGISTRY%/%IMGNAME%:latest
                        docker tag %IMGNAME%:%IMAGE_TAG% %DOCKER_REGISTRY%/%IMGNAME%:%IMAGE_TAG%
                        docker push %DOCKER_REGISTRY%/%IMGNAME%:latest
                        docker push %DOCKER_REGISTRY%/%IMGNAME%:%IMAGE_TAG%
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    bat """
                    kubectl set image deployment/%IMGNAME% %IMGNAME%=%DOCKER_REGISTRY%/%IMGNAME%:%IMAGE_TAG% -n %KUBE_NAMESPACE%
                    kubectl rollout status deployment/%IMGNAME% -n %KUBE_NAMESPACE% --timeout=5m
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    bat """
                    kubectl get pods -n %KUBE_NAMESPACE% -l app=%IMGNAME%
                    kubectl get svc -n %KUBE_NAMESPACE% -l app=%IMGNAME%
                    """
                }
            }
        }

        stage('Smoke Tests') {
            steps {
                script {
                    bat """
                    timeout /t 20 /nobreak
                    curl -f http://localhost:5000 || exit /b 1
                    """
                }
            }
        }

    }

    post {
        success {
            echo '✅ Pipeline succeeded! Application deployed successfully to Kubernetes.'
        }
        failure {
            echo '❌ Pipeline failed! Attempting rollback...'
            script {
                bat 'kubectl rollout undo deployment/%IMGNAME% -n %KUBE_NAMESPACE% || exit /b 0'
            }
        }
        always {
            bat 'docker logout || exit /b 0'
            cleanWs()
        }
    }
}