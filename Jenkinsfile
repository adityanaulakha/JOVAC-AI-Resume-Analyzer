pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'flask-resume-analyzer'
        CONTAINER_NAME = 'resume-analyzer-container'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/adityanaulakha/JOVAC-AI-Resume-Analyzer.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE .'
            }
        }

        stage('Run Container') {
            steps {
                sh 'docker stop $CONTAINER_NAME || true'
                sh 'docker rm $CONTAINER_NAME || true'
                sh 'docker run -d -p 5000:5000 --name $CONTAINER_NAME $DOCKER_IMAGE'
            }
        }
    }
}
