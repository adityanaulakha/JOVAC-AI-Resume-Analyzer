pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        GITHUB_TOKEN = credentials('github-token')
        IMAGE_NAME = "adityanaulakha/ai-resume-analyzer"
    }

    stages {

        stage('Checkout from GitHub') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/adityanaulakha/JOVAC-AI-Resume-Analyzer.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "🔧 Building Docker image..."
                    docker build -t $IMAGE_NAME:latest .
                '''
            }
        }

        stage('Docker Login') {
            steps {
                sh '''
                    echo "🔐 Logging into Docker Hub..."
                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login -u "$DOCKERHUB_CREDENTIALS_USR" --password-stdin
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh '''
                    echo "📤 Pushing image to Docker Hub..."
                    docker push $IMAGE_NAME:latest
                '''
            }
        }

        stage('Deploy Locally on EC2') {
            steps {
                sh '''
                    echo "Deploying locally on EC2..."
                    sudo usermod -aG docker jenkins || true

                    echo "Stopping old container"
                    docker stop ai-resume || true
                    docker rm ai-resume || true

                    echo "Pulling latest Docker image"
                    docker pull $IMAGE_NAME:latest

                    echo "Starting new container"
                    docker run -d \
                        -p 5000:5000 \
                        --name ai-resume \
                        $IMAGE_NAME:latest

                    echo "Deployment complete!"
                '''
            }
        }
    }
}
