# docker_kubernetes
Multi-Tier Web Application Deployment with Docker and Kubernetes


# FastAPI App Deployment with Docker and Kubernetes

This project demonstrates how to deploy a FastAPI application using Docker and Kubernetes on AWS EKS.

## Prerequisites
- Docker
- AWS CLI
- eksctl
- kubectl

## Steps to Deploy

1. **Build the Docker Image**:
   
   docker build -t fastapi-app:latest .

2.Push the Docker Image to a Registry:

docker tag fastapi-app:latest <your-dockerhub-username>/fastapi-app:latest
docker push <your-dockerhub-username>/fastapi-app:latest

3.Create an EKS Cluster:

eksctl create cluster --name fastapi-cluster 
                     --region us-west-2 
                     --nodegroup-name standard-workers 
                     --node-type t3.medium 
                     --nodes 2
This command creates a cluster named fastapi-cluster in the us-west-2 region with 2 worker nodes.
Then we need to config kubectl:
aws eks --region us-west-2 update-kubeconfig --name fastapi-cluster

4.Deploy to Kubernetes:
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

5.Access the Application:
Get the external IP of the service:
kubectl get services
Visit http://<external-ip> in your browser.
