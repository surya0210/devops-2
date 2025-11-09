pipeline {
    agent any

    environment {
        APP_NAME = "ACEest_Fitness_API"
        DOCKER_IMAGE = "surya0224/aceest_fitness_api:v1.0"
        PORT = "5000"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out source code..."
                checkout scm
            }
        }

        stage('Set up Python Environment') {
            steps {
                echo "Setting up Python environment..."
                sh '''
                    sudo apt update -y
                    sudo apt install -y python3 python3-pip python3-venv
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install flask pytest reportlab
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                echo "Running API tests using pytest..."
                sh '''
                    source venv/bin/activate
                    pytest -v test_fitness_api.py --maxfail=1 --disable-warnings
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image for ${APP_NAME}..."
                sh '''
                    docker build -t $DOCKER_IMAGE .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub_token', variable: 'DOCKER_TOKEN')]) {
                    sh '''
                        echo "$DOCKER_TOKEN" | docker login -u surya0224 --password-stdin
                        docker push $DOCKER_IMAGE
                    '''
                }
            }
        }

        stage('Deploy Container') {
            steps {
                echo "Deploying Docker container on port ${PORT}..."
                sh '''
                    docker rm -f aceest_api || true
                    docker run -d -p ${PORT}:5000 --name aceest_api $DOCKER_IMAGE
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful! API running on port ${PORT}"
        }
        failure {
            echo "❌ Build Failed! Check logs above."
        }
    }
}
