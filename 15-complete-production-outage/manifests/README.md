# Exercise 15 – Complete Production Outage

## Objective

Investigate a complete production outage caused by secret rotation and identify the root cause by analyzing every layer of the infrastructure.

---

# Scenario

At **09:00**, a new deployment completed successfully.

At **09:05**, users started receiving:

```
HTTP 503 Service Unavailable
```

Available Evidence:

- ArgoCD → Healthy
- Pods → Running
- Ingress → Healthy
- Application Logs → Cannot connect to Redis
- Redis Logs → Authentication failed
- AWS Secrets Manager → Secret rotated at 08:55

---

# Architecture

```
AWS Secrets Manager
        │
        ▼
External Secrets Operator
        │
        ▼
Kubernetes Secret
        │
        ▼
Payment Application
        │
        ▼
Redis
```

---

# Project Structure

```
15-complete-production-outage
│
├── manifests
│   ├── app-configmap.yaml
│   ├── deployment.yaml
│   ├── secretstore.yaml
│   └── externalsecret.yaml
│
├── docs
├── screenshots
└── README.md
```

---

# Prerequisites

- AWS Account
- Amazon EKS Cluster
- kubectl
- Helm
- AWS CLI
- External Secrets Operator

---

# Step 1 – Create EKS Cluster

```bash
eksctl create cluster \
--name outage-lab \
--region us-east-1 \
--node-type t3.small \
--nodes 2
```

Verify

```bash
kubectl get nodes
```

---

# Step 2 – Install Redis

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami

helm repo update

helm install redis bitnami/redis \
--set architecture=standalone \
--set auth.enabled=true \
--set auth.password=Redis@123 \
--set master.persistence.enabled=false
```

Verify

```bash
kubectl get pods
```

Expected

```
redis-master-0    Running
```

---

# Step 3 – Install External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io

helm repo update

helm install external-secrets external-secrets/external-secrets \
-n external-secrets \
--create-namespace
```

Verify

```bash
kubectl get pods -n external-secrets
```

---

# Step 4 – Create Secret in AWS Secrets Manager

```bash
aws secretsmanager create-secret \
--name redis-secret \
--secret-string '{
  "REDIS_PASSWORD":"Redis@123"
}' \
--region us-east-1
```

Verify

```bash
aws secretsmanager get-secret-value \
--secret-id redis-secret \
--region us-east-1
```

---

# Step 5 – Create AWS Credential Secret

```bash
kubectl create secret generic aws-secret \
--from-literal=access-key=<AWS_ACCESS_KEY_ID> \
--from-literal=secret-access-key=<AWS_SECRET_ACCESS_KEY>
```

Verify

```bash
kubectl get secret
```

---

# Step 6 – Create SecretStore

Apply

```bash
kubectl apply -f manifests/secretstore.yaml
```

Verify

```bash
kubectl get secretstore
```

Expected

```
READY : True
STATUS : Valid
```

---

# Step 7 – Create ExternalSecret

Apply

```bash
kubectl apply -f manifests/externalsecret.yaml
```

Verify

```bash
kubectl get externalsecret

kubectl get secret redis-secret
```

Decode Secret

```bash
kubectl get secret redis-secret \
-o jsonpath='{.data.REDIS_PASSWORD}' | base64 -d
```

Expected

```
Redis@123
```

---

# Step 8 – Deploy Payment Application

Apply

```bash
kubectl apply -f manifests/app-configmap.yaml

kubectl apply -f manifests/deployment.yaml
```

Verify

```bash
kubectl get pods
```

Application Logs

```bash
kubectl logs deployment/payment-service
```

Expected

```
Starting Payment Service...
Connecting to Redis...
PONG
Redis connection successful
```

---

# Step 9 – Rotate Secret

Rotate password inside AWS Secrets Manager.

```bash
aws secretsmanager update-secret \
--secret-id redis-secret \
--secret-string '{
  "REDIS_PASSWORD":"Redis@456"
}' \
--region us-east-1
```

Wait for External Secrets synchronization.

Verify Kubernetes Secret

```bash
kubectl get secret redis-secret \
-o jsonpath='{.data.REDIS_PASSWORD}' | base64 -d
```

Expected

```
Redis@456
```

---

# Step 10 – Restart Application

```bash
kubectl rollout restart deployment payment-service
```

Verify

```bash
kubectl get pods
```

---

# Step 11 – Observe Failure

Check logs

```bash
kubectl logs deployment/payment-service
```

Observed

```
Starting Payment Service...
Connecting to Redis...

AUTH failed: WRONGPASS invalid username-password pair or user is disabled.

NOAUTH Authentication required.

Cannot connect to Redis

HTTP 503 Service Unavailable
```

---

# Investigation

## ArgoCD

Status

```
Healthy
```

Deployment completed successfully.

No synchronization issues.

---

## AWS Secrets Manager

Verify

```bash
aws secretsmanager get-secret-value \
--secret-id redis-secret \
--region us-east-1
```

Result

```
REDIS_PASSWORD = Redis@456
```

Secret rotation completed successfully.

---

## External Secrets

Verify

```bash
kubectl get externalsecret
```

Result

```
SecretSynced
```

Synchronization successful.

---

## Kubernetes Secret

Verify

```bash
kubectl get secret redis-secret \
-o jsonpath='{.data.REDIS_PASSWORD}' | base64 -d
```

Result

```
Redis@456
```

Kubernetes Secret updated successfully.

---

## Application

Logs

```
Cannot connect to Redis

HTTP 503
```

Application is using the rotated password.

---

## Redis

Redis server still expects

```
Redis@123
```

Application sends

```
Redis@456
```

Authentication fails.

---

# Timeline

```
08:55

AWS Secrets Manager password rotated

↓

08:56

External Secrets synchronized

↓

08:57

Kubernetes Secret updated

↓

09:00

Application restarted

↓

Application loaded Redis@456

↓

Redis still configured with Redis@123

↓

09:05

Redis authentication failed

↓

Application unavailable

↓

HTTP 503
```

---

# Root Cause

AWS Secrets Manager successfully rotated the Redis password.

External Secrets synchronized the updated password into Kubernetes.

The application restarted and began using the new password.

However, the Redis server itself still used the previous password.

Because the application and Redis were using different credentials, Redis rejected authentication requests, causing repeated connection failures and HTTP 503 errors.

---

# Immediate Fix

- Update Redis to use the rotated password.
- Restart dependent applications if required.
- Verify application connectivity after rotation.

---

# Long-Term Prevention

- Perform coordinated secret rotation across all dependent services.
- Use automated rolling restarts for applications that load secrets only during startup.
- Validate secret rotation in a staging environment before production deployment.
- Implement versioned secret rotation with rollback capability.

---

# Monitoring Improvements

Create alerts for:

- Redis authentication failures
- HTTP 503 response rate
- External Secret synchronization failures
- Secret rotation failures
- Application connection failures

Create dashboards showing:

- External Secret synchronization status
- Redis authentication metrics
- HTTP 5xx errors
- Application health
- Secret rotation history

---

# Learning Outcomes

- Deployed Redis with authentication.
- Integrated AWS Secrets Manager with Kubernetes using External Secrets.
- Synchronized secrets automatically.
- Simulated production secret rotation.
- Investigated authentication failures.
- Performed complete Root Cause Analysis.
- Implemented production troubleshooting workflow.

---

# Result

Exercise 15 completed successfully.

A production outage caused by Redis authentication failure after AWS Secret rotation was successfully reproduced, investigated, and resolved through end-to-end Root Cause Analysis.
