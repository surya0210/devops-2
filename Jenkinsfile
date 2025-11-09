pipeline {
    agent any

    environment {
        // Jenkins credentials ID for Docker Hub (add this in Jenkins UI)
        DOCKER_CREDENTIALS = credentials('dockerhub-login')

        //Your Docker Hub username and image name
        DOCKER_USER = 'surya0224'
        IMAGE_NAME = 'aceest_fitness_api'

        //  Flask app port
        APP_PORT = '5000'
    }

    stages {

        // 1️⃣ Checkout Code from GitHub
        stage('Checkout Source') {
            steps {
                echo ' Cloning source code from GitHub...'
                git branch: 'main', url: 'https://github.com/surya0210/devops-2.git'
            }
        }

        //  Build Docker Image
        stage('Build Docker Image') {
            steps {
                script {
                    echo ' Building Docker image...'
                    sh 'docker build -t ${DOCKER_USER}/${IMAGE_NAME}:latest .'
                }
            }
        }

        // Push Docker Image to Docker Hub
        stage('Push to Docker Hub') {
            steps {
                script {
                    echo ' Logging in and pushing image to Docker Hub...'
                    sh 'echo $DOCKER_CREDENTIALS_PSW | docker login -u $DOCKER_CREDENTIALS_USR --password-stdin'
                    sh 'docker push ${DOCKER_USER}/${IMAGE_NAME}:latest'
                }
            }
        }

        // � Deploy the Docker Container on Server
        stage('Deploy Container') {
            steps {
                script {
                    echo ' Deploying container on Ubuntu server...'

                    // Stop & remove old container if exists
                    sh '''
                    if [ "$(docker ps -q -f name=aceest_fitness_api)" ]; then
                        echo "Stopping old container..."
                        docker stop aceest_fitness_api
                        docker rm aceest_fitness_api
                    fi
                    '''

                    // Run latest version
                    sh '''
                    echo "Starting new container..."
                    docker run -d -p ${APP_PORT}:5000 --name aceest_fitness_api ${DOCKER_USER}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        //  Verify Deployment
        stage('Verify Deployment') {
            steps {
                script {
                    echo 'Checking container status...'
                    sh 'docker ps | grep aceest_fitness_api || echo "Container not running!"'

                }
            }
        }
    }

    post {
        success {
            echo ' CI/CD Pipeline completed successfully. App is live on port 5000!'
        }
        failure {
            echo ' Pipeline failed! Please review Jenkins console logs for errors.'
        }
    }
}
