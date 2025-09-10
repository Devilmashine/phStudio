#!/bin/bash

# Kubernetes Deployment Script for Photo Studio CRM
# This script deploys the application to a Kubernetes cluster

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    print_error "Not connected to a Kubernetes cluster. Please configure kubectl."
    exit 1
fi

# Get current context
CURRENT_CONTEXT=$(kubectl config current-context)
print_status "Connected to cluster: $CURRENT_CONTEXT"

# Confirm deployment
echo
read -p "Do you want to deploy Photo Studio CRM to the $CURRENT_CONTEXT cluster? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Deployment cancelled."
    exit 0
fi

# Deploy namespace
print_status "Creating namespace..."
kubectl apply -f kubernetes/phstudio-namespace.yml

# Deploy ConfigMaps
print_status "Deploying ConfigMaps..."
kubectl apply -f kubernetes/configmap.yml

# Deploy PersistentVolumeClaims
print_status "Creating PersistentVolumeClaims..."
kubectl apply -f kubernetes/persistent-volume-claims.yml

# Wait for PVCs to be bound
print_status "Waiting for PVCs to be bound..."
kubectl wait --for=condition=ready pod --all -n phstudio --timeout=300s || true

# Deploy databases
print_status "Deploying PostgreSQL..."
kubectl apply -f kubernetes/postgres-deployment.yml

print_status "Deploying Redis..."
kubectl apply -f kubernetes/redis-deployment.yml

# Wait for databases to be ready
print_status "Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n phstudio --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n phstudio --timeout=300s

# Deploy monitoring
print_status "Deploying monitoring services..."
kubectl apply -f kubernetes/monitoring-deployment.yml

# Deploy main applications
print_status "Deploying backend..."
kubectl apply -f kubernetes/backend-deployment.yml

print_status "Deploying frontend..."
kubectl apply -f kubernetes/frontend-deployment.yml

# Wait for applications to be ready
print_status "Waiting for applications to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n phstudio --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n phstudio --timeout=300s

# Deploy ingress
print_status "Deploying ingress..."
kubectl apply -f kubernetes/ingress.yml

# Show deployment status
print_status "Deployment completed! Checking status..."
echo
print_status "Pods status:"
kubectl get pods -n phstudio
echo
print_status "Services status:"
kubectl get services -n phstudio
echo
print_status "Ingress status:"
kubectl get ingress -n phstudio

# Show endpoints
print_status "Application endpoints:"
echo "  Frontend: https://your-domain.com"
echo "  Backend API: https://your-domain.com/api"
echo "  Health check: https://your-domain.com/health"
echo "  Monitoring (Prometheus): https://your-domain.com/monitoring"
echo "  Dashboards (Grafana): https://your-domain.com/grafana"

print_status "Deployment finished successfully!"
print_warning "Remember to:"
print_warning "1. Update the secrets with real values"
print_warning "2. Configure your domain name in ingress.yml"
print_warning "3. Set up SSL certificates"
print_warning "4. Configure monitoring alerts"