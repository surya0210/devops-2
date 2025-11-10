pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://13.204.35.68:9000'
        SONAR_PROJECT_KEY = 'ACEest_Fitness'
        SONARQUBE_ENV = 'SonarQube'
        SONAR_TOKEN = credentials('SONAR_TOKEN')
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-login')
        DOCKER_IMAGE = 'surya0224/aceest_fitness_api'
        K8S_DEPLOYMENT = 'aceest-fitness-deployment'
    }

    options {
        timestamps()
        skipDefaultCheckout(false)
    }

    stages {

        // 1️⃣ Checkout Source
        stage('Checkout Source') {
            steps {
                echo "📥 Cloning source code from GitHub..."
                git branch: 'main', url: 'https://github.com/surya0210/devops-2.git'
            }
        }

        // 2️⃣ Ensure SonarQube Running
        stage('Ensure SonarQube Running') {
            steps {
                script {
                    echo "🧠 Checking SonarQube container status..."
                    sh '''
                        set -e
                        if [ "$(docker ps -aq -f name=sonarqube)" ]; then
                            if [ "$(docker ps -q -f name=sonarqube)" ]; then
                                echo "✅ SonarQube container is already running."
                            else
                                echo "♻️ Starting existing SonarQube container..."
                                docker start sonarqube
                            fi
                        else
                            echo "🚀 Launching new SonarQube container..."
                            docker run -d --name sonarqube -p 9000:9000 sonarqube:lts-community
                        fi

                        echo "⏳ Waiting for SonarQube to be healthy..."
                        for i in $(seq 1 30); do
                            if curl -s http://localhost:9000/api/system/health | grep -q '"status":"UP"'; then
                                echo "✅ SonarQube is healthy and ready."
                                exit 0
                            fi
                            sleep 5
                        done
                        echo "⚠️ SonarQube health not confirmed (continuing anyway)..."
                    '''
                }
            }
        }

        // 3️⃣ SonarQube Code Analysis
        stage('SonarQube Code Analysis') {
            steps {
                echo "🔍 Running SonarQube Analysis..."
                withSonarQubeEnv('SonarQube') {
                    withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.token=${SONAR_TOKEN}
                        '''
                    }
                }
            }
        }

        // 4️⃣ Quality Gate Check
        stage('Quality Gate') {
            steps {
                script {
                    echo "🧰 Waiting for Quality Gate result..."
                    timeout(time: 3, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "❌ Quality Gate failed: ${qg.status}"
                        } else {
                            echo "✅ Quality Gate passed!"
                        }
                    }
                }
            }
        }

        // 5️⃣ Build Docker Image
        stage('Build Docker Image') {
            steps {
                script {
                    echo "🐳 Building Docker image..."
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:latest -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
                    '''
                }
            }
        }

        // 6️⃣ Run Unit Tests (Pytest)
        stage('Run Unit Tests (pytest)') {
            steps {
                script {
                    echo "🧪 Running pytest in container..."
                    sh '''
                        docker run --rm ${DOCKER_IMAGE}:latest pytest --maxfail=1 --disable-warnings -q
                    '''
                }
            }
        }

        // 7️⃣ Push Docker Image to DockerHub
        stage('Push Docker Image to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-login',
                                                 usernameVariable: 'DOCKER_USER',
                                                 passwordVariable: 'DOCKER_PASS')]) {
                    script {
                        echo "🔐 Logging into DockerHub and pushing image..."
                        sh '''
                            echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                            docker push ${DOCKER_IMAGE}:latest
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                            docker logout
                        '''
                    }
                }
            }
        }

        // 8️⃣ Ensure Minikube Running
        stage('Ensure Minikube Running') {
            steps {
                script {
                    echo "🔍 Checking Minikube status..."
                    def status = sh(script: "minikube status --format '{{.Host}}' || echo 'Stopped'", returnStdout: true).trim()

                    if (status != 'Running') {
                        echo "🚀 Starting Minikube..."
                        sh '''
                            minikube delete || true
                            minikube start --driver=docker --memory=2048mb --disk-size=20g
                            mkdir -p /var/lib/jenkins/.kube /var/lib/jenkins/.minikube
                            chown -R jenkins:jenkins /var/lib/jenkins/.kube /var/lib/jenkins/.minikube
                            chmod -R 755 /var/lib/jenkins/.kube /var/lib/jenkins/.minikube
                        '''
                    } else {
                        echo "✅ Minikube is already running."
                    }
                }
            }
        }

        // 9️⃣ Update Deployment Tag (💥 NEW STAGE)
        stage('Update K8s Deployment Tag') {
            steps {
                script {
                    echo "📝 Updating image tag in Kubernetes deployment YAML..."
                    sh '''
                        sed -i "s|image: ${DOCKER_IMAGE}:.*|image: ${DOCKER_IMAGE}:${BUILD_NUMBER}|g" kube/deployment.yaml
                        echo "✅ Updated image line:"
                        grep "image:" kube/deployment.yaml
                    '''
                }
            }
        }

        // 🔟 Deploy to Kubernetes
        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo "🚀 Deploying application to Kubernetes..."
                    sh '''
                        kubectl apply -f kube/ --validate=false
                        echo "⏳ Waiting for rollout to complete (max 5 min)..."
                        kubectl rollout status deployment/${K8S_DEPLOYMENT} --timeout=300s || {
                            echo "⚠️ Rollout taking too long, checking pod status..."
                            kubectl get pods -o wide
                            kubectl describe pods
                            exit 1
                        }
                    '''
                }
            }
        }

        // 1️⃣1️⃣ Verify Rollout
        stage('Verify Rollout') {
            steps {
                script {
                    echo "🔎 Verifying Deployment..."
                    sh 'kubectl get pods -o wide'
                    sh 'kubectl get svc'
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker images..."
            sh 'docker image prune -f || true'
        }
        success {
            echo "✅ Pipeline executed successfully!"
        }
        failure {
            echo "❌ Pipeline failed! Please check Jenkins logs for details."
        }
    }
}
