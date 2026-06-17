# Exercise 1 - EKS Application Deployment via GitOps

## Objective

Deploy a microservice called **payment-service** on Amazon EKS using a complete GitOps workflow.

---

# Architecture

```text
GitHub
   ↓
GitHub Actions
   ↓
Amazon ECR
   ↓
ArgoCD
   ↓
Amazon EKS
   ↓
AWS ALB Ingress
   ↓
Payment Service

AWS Secrets Manager
   ↓
IRSA (IAM Roles for Service Accounts)
   ↓
Application

Prometheus
   ↓
Grafana
```

---

# Requirements

* Deploy application using Helm Chart
* Use ArgoCD Auto Sync
* Build and push Docker image to Amazon ECR using GitHub Actions
* Store secrets in AWS Secrets Manager
* Access AWS resources using IRSA
* Expose application using AWS ALB Ingress Controller
* Monitor cluster using Prometheus and Grafana

---

# Technologies Used

* AWS EKS
* AWS ECR
* AWS IAM
* AWS Secrets Manager
* OIDC Provider
* IRSA
* Docker
* Kubernetes
* Helm
* ArgoCD
* GitHub Actions
* Prometheus
* Grafana
* AWS Load Balancer Controller

---

# Project Structure

```text
devops-special-training
│
├── .github
│   └── workflows
│       └── build-and-push.yml
│
└── 01-eks-gitops-deployment
    │
    ├── argocd
    │   └── application.yaml
    │
    ├── payment-service
    │   ├── Dockerfile
    │   ├── index.html
    │   └── payment-service
    │       ├── Chart.yaml
    │       ├── values.yaml
    │       └── templates
    │
    ├── screenshots
    ├── commands.md
    └── theory.md
```

---

# Step 1 - Create EKS Cluster

Created Amazon EKS cluster in us-east-1 region.

```bash
eksctl create cluster \
--name devops-training \
--region us-east-1 \
--nodes 2 \
--node-type t3.small
```

Verification:

```bash
kubectl get nodes
kubectl cluster-info
```

---

# Step 2 - Install ArgoCD

Created ArgoCD namespace.

```bash
kubectl create namespace argocd
```

Installed ArgoCD:

```bash
kubectl apply -n argocd \
-f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verification:

```bash
kubectl get pods -n argocd
```

---

# Step 3 - Create Application

Created simple payment-service application.

Files:

```text
Dockerfile
index.html
```

Dockerfile:

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/index.html
```

---

# Step 4 - Create ECR Repository

Created ECR repository:

```bash
aws ecr create-repository \
--repository-name payment-service
```

Verification:

```bash
aws ecr describe-repositories
```

---

# Step 5 - Build and Push Docker Image

Authenticated Docker to ECR.

```bash
aws ecr get-login-password \
| docker login
```

Build image:

```bash
docker build -t payment-service .
```

Tag image:

```bash
docker tag payment-service:v1 \
<account-id>.dkr.ecr.us-east-1.amazonaws.com/payment-service:v1
```

Push image:

```bash
docker push \
<account-id>.dkr.ecr.us-east-1.amazonaws.com/payment-service:v1
```

Verification:

```bash
aws ecr list-images \
--repository-name payment-service
```

---

# Step 6 - GitHub Actions CI Pipeline

Created workflow:

```text
.github/workflows/build-and-push.yml
```

Pipeline tasks:

* Checkout Code
* Configure AWS Credentials
* Login to ECR
* Build Docker Image
* Tag Docker Image
* Push Docker Image to ECR

GitHub Secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

Verification:

GitHub Actions → Build Successful

---

# Step 7 - Create Helm Chart

Generated Helm chart.

```bash
helm create payment-service
```

Modified:

```text
Chart.yaml
values.yaml
deployment.yaml
service.yaml
```

Installed:

```bash
helm install payment-service ./payment-service
```

Verification:

```bash
kubectl get all
```

---

# Step 8 - Configure ArgoCD GitOps

Created:

```text
argocd/application.yaml
```

Configured:

* Repository URL
* Helm Chart Path
* Auto Sync
* Self Heal
* Prune

Applied:

```bash
kubectl apply -f application.yaml
```

Verification:

```bash
kubectl get applications -n argocd
```

Output:

```text
payment-service   Synced   Healthy
```

---

# Step 9 - AWS Secrets Manager

Created secret:

```bash
aws secretsmanager create-secret \
--name payment-service-secret \
--secret-string '{"username":"admin","password":"devops123"}'
```

Verification:

```bash
aws secretsmanager list-secrets
```

---

# Step 10 - Configure OIDC Provider

Enabled OIDC:

```bash
eksctl utils associate-iam-oidc-provider \
--cluster devops-training \
--region us-east-1 \
--approve
```

Verification:

OIDC provider successfully created.

---

# Step 11 - Create IAM Policy

Created file:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }
  ]
}
```

Created policy:

```bash
aws iam create-policy \
--policy-name PaymentServiceSecretsPolicy \
--policy-document file://secrets-policy.json
```

---

# Step 12 - Configure IRSA

Created Service Account:

```bash
eksctl create iamserviceaccount \
--name payment-service-sa \
--namespace default \
--cluster devops-training \
--attach-policy-arn \
arn:aws:iam::<account-id>:policy/PaymentServiceSecretsPolicy \
--approve
```

Verification:

```bash
kubectl describe sa payment-service-sa
```

Output contains:

```text
eks.amazonaws.com/role-arn
```

---

# Step 13 - Install AWS Load Balancer Controller

Installed:

* IAM Policy
* Service Account
* Helm Chart

Verification:

```bash
kubectl get pods -n kube-system
```

Output:

```text
aws-load-balancer-controller
```

Running.

---

# Step 14 - Create ALB Ingress

Created:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
```

Applied:

```bash
kubectl apply -f alb-ingress.yaml
```

Verification:

```bash
kubectl get ingress
```

Output:

```text
k8s-default-payments-xxxxxxxx.elb.amazonaws.com
```

---

# Step 15 - Install Prometheus and Grafana

Added repository:

```bash
helm repo add prometheus-community \
https://prometheus-community.github.io/helm-charts
```

Installed:

```bash
helm install monitoring \
prometheus-community/kube-prometheus-stack \
--namespace monitoring \
--create-namespace
```

Initially deployment failed because:

```text
Too many pods
```

on two-node cluster.

Scaled node group to three nodes.

After scaling:

* Prometheus Running
* Grafana Running
* Alertmanager Running

---

# Step 16 - Access Grafana

Get password:

```bash
kubectl get secret monitoring-grafana \
-n monitoring \
-o jsonpath="{.data.admin-password}" | base64 -d
```

Port forward:

```bash
kubectl port-forward \
svc/monitoring-grafana \
3000:80 \
-n monitoring
```

Access:

```text
http://localhost:3000
```

Login:

```text
Username: admin
Password: generated password
```

---

# Monitoring Results

Observed metrics:

* CPU Utilisation
* Memory Utilisation
* Namespace Metrics
* Node Metrics
* Cluster Metrics

Dashboard:

```text
Kubernetes / Compute Resources / Cluster
```

---

# Validation

```text
Helm Deployment                 SUCCESS
GitHub Actions CI               SUCCESS
Amazon ECR Push                 SUCCESS
ArgoCD Auto Sync                SUCCESS
Secrets Manager                 SUCCESS
OIDC Provider                   SUCCESS
IRSA                            SUCCESS
AWS Load Balancer Controller    SUCCESS
ALB Ingress                     SUCCESS
Prometheus                      SUCCESS
Grafana                         SUCCESS
Monitoring Dashboard            SUCCESS
```

---

# Outcome

Successfully implemented a production-style GitOps deployment pipeline on Amazon EKS using:

* GitHub Actions
* Amazon ECR
* Helm
* ArgoCD
* AWS Secrets Manager
* IRSA
* ALB Ingress Controller
* Prometheus
* Grafana

This project demonstrates end-to-end Kubernetes deployment, security, observability, and GitOps practices used in real-world DevOps environments.
