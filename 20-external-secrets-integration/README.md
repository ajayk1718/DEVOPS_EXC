# Exercise 20 – External Secrets Integration

## Objective

Integrate AWS Secrets Manager with Kubernetes using External Secrets Operator.

Automatically synchronize secrets stored in AWS Secrets Manager into Kubernetes Secrets without manually creating or updating Kubernetes Secret resources.

---

## Scenario

A production application requires sensitive credentials such as:

- DB_USERNAME
- DB_PASSWORD
- JWT_SECRET

Instead of storing these credentials directly inside Kubernetes, they are securely stored in AWS Secrets Manager.

External Secrets Operator continuously synchronizes these secrets from AWS into Kubernetes.

---

## Architecture

```
AWS Secrets Manager
        │
        ▼
 payment-app-secret
        │
        ▼
External Secrets Operator
        │
        ▼
SecretStore
        │
        ▼
ExternalSecret
        │
        ▼
Kubernetes Secret
        │
        ▼
Application
```

---

# Project Structure

```
20-external-secrets-integration
│
├── manifests
│   ├── secretstore.yaml
│   └── externalsecret.yaml
│
├── docs
│
├── screenshots
│
└── README.md
```

---

# Prerequisites

- AWS Account
- EKS Cluster
- kubectl
- Helm
- AWS CLI
- IAM User with Secrets Manager permissions

---

# Step 1 – Create EKS Cluster

```bash
eksctl create cluster \
--name secrets-lab \
--region us-east-1 \
--node-type t3.small \
--nodes 2
```

Verify

```bash
kubectl get nodes
```

---

# Step 2 – Install External Secrets Operator

Add Helm Repository

```bash
helm repo add external-secrets https://charts.external-secrets.io
```

Update

```bash
helm repo update
```

Install

```bash
helm install external-secrets external-secrets/external-secrets \
-n external-secrets \
--create-namespace
```

Verify

```bash
kubectl get pods -n external-secrets
```

Expected

```
external-secrets
external-secrets-webhook
external-secrets-cert-controller
```

---

# Step 3 – Create Secret in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
--name payment-app-secret \
--secret-string '{
"DB_USERNAME":"admin",
"DB_PASSWORD":"Password@123",
"JWT_SECRET":"MyJwtSecret123"
}'
```

Verify

```bash
aws secretsmanager list-secrets
```

---

# Step 4 – Create AWS Credential Secret

Create Kubernetes Secret containing AWS credentials.

```bash
kubectl create secret generic aws-secret \
-n external-secrets \
--from-literal=access-key=<AWS_ACCESS_KEY_ID> \
--from-literal=secret-access-key=<AWS_SECRET_ACCESS_KEY>
```

Verify

```bash
kubectl get secret -n external-secrets
```

---

# Step 5 – Create SecretStore

Apply

```bash
kubectl apply -f manifests/secretstore.yaml
```

Verify

```bash
kubectl get secretstore -n external-secrets
```

Expected

```
READY : True
STATUS : Valid
```

---

# Step 6 – Create ExternalSecret

Apply

```bash
kubectl apply -f manifests/externalsecret.yaml
```

Verify

```bash
kubectl get externalsecret -n external-secrets
```

Expected

```
READY : True
STATUS : SecretSynced
```

---

# Step 7 – Verify Kubernetes Secret

```bash
kubectl get secret payment-secret \
-n external-secrets
```

Expected

```
DATA
3
```

Decode values

```bash
kubectl get secret payment-secret \
-n external-secrets \
-o jsonpath='{.data.DB_USERNAME}' | base64 -d

kubectl get secret payment-secret \
-n external-secrets \
-o jsonpath='{.data.DB_PASSWORD}' | base64 -d

kubectl get secret payment-secret \
-n external-secrets \
-o jsonpath='{.data.JWT_SECRET}' | base64 -d
```

Expected

```
admin
Password@123
MyJwtSecret123
```

---

# Validation

Verify External Secret

```bash
kubectl get externalsecret -n external-secrets
```

Verify Kubernetes Secret

```bash
kubectl get secret payment-secret -n external-secrets
```

Verify SecretStore

```bash
kubectl get secretstore -n external-secrets
```

---

# Root Cause (If Synchronization Fails)

Possible reasons include:

- Invalid AWS credentials
- Incorrect SecretStore configuration
- Wrong AWS region
- Secret does not exist in AWS Secrets Manager
- Missing IAM permissions
- Incorrect secret property names

---

# Production Benefits

- Secrets remain inside AWS Secrets Manager.
- No hardcoded credentials in Kubernetes manifests.
- Automatic synchronization.
- Supports secret rotation.
- Improved security and centralized secret management.

---

# Learning Outcomes

- Installed External Secrets Operator
- Integrated AWS Secrets Manager with Kubernetes
- Created SecretStore
- Created ExternalSecret
- Automatically synchronized AWS secrets into Kubernetes
- Validated successful secret synchronization

---

# Result

Exercise 20 completed successfully.

AWS Secrets Manager secrets were automatically synchronized into Kubernetes using External Secrets Operator.
