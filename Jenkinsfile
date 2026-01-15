pipeline {
    agent any

    environment {
        // The name of your deployment in Kubernetes
        DEPLOYMENT_NAME = 'devops-backend'
        // The name of the image in your Docker Hub repository
        IMGNAME = 'devops_project'
        DOCKER_REGISTRY = 'hadilt'
        PYTHON_IMAGE = 'python:3.11-slim'
        IMAGE_TAG = "${BUILD_NUMBER}"
        // Set to 'default' as per your previous kubectl output
        KUBE_NAMESPACE = 'default' 
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
                // Building the local image
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
                    // Update the 'backend' container inside 'devops-backend' deployment
                    bat """
                    kubectl set image deployment/%DEPLOYMENT_NAME% backend=%DOCKER_REGISTRY%/%IMGNAME%:%IMAGE_TAG% -n %KUBE_NAMESPACE%
                    kubectl rollout status deployment/%DEPLOYMENT_NAME% -n %KUBE_NAMESPACE% --timeout=5m
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    bat """
                    kubectl get pods -n %KUBE_NAMESPACE% -l app=%DEPLOYMENT_NAME%
                    kubectl get svc -n %KUBE_NAMESPACE% -l app=%DEPLOYMENT_NAME%
                    """
                }
            }
        }

        stage('Smoke Tests') {
            steps {
                script {
                    bat """
                    timeout /t 20 /nobreak
                    curl -f http://localhost:30001 || exit /b 1
                    """
                }
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline succeeded! Application deployed to Kubernetes.'
        }
        failure {
            echo '❌ Pipeline failed! Attempting rollback...'
            script {
                bat 'kubectl rollout undo deployment/%DEPLOYMENT_NAME% -n %KUBE_NAMESPACE% || exit /b 0'
            }
        }
        always {
            bat 'docker logout || exit /b 0'
            cleanWs()
        }
    }
}