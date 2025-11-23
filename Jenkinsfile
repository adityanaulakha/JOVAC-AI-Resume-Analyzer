pipeline {
    agent any

    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub')
        EC2_SSH = credentials('ec2-ssh-key')
        GITHUB_TOKEN = credentials('github-token')
        EC2_IP = "13.232.168.255"
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

        stage('Deploy on EC2 Server') {
            steps {
                sh '''
                    echo "🚀 Deploying on EC2..."

                    ssh -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'EOF'
                        echo "🔁 Pulling latest image..."
                        docker pull $IMAGE_NAME:latest

                        echo "🛑 Stopping existing container..."
                        docker stop ai-resume || true
                        docker rm ai-resume || true

                        echo "▶️ Running new container..."
                        docker run -d \
                            -p 5000:5000 \
                            --name ai-resume \
                            $IMAGE_NAME:latest
                    EOF
                '''
            }
        }
    }
}
