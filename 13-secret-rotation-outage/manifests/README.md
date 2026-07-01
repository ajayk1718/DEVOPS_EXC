# Exercise 13 – Secret Rotation Outage

## Objective

Investigate why a secret rotation in AWS Secrets Manager did not immediately update a running Kubernetes application.

---

## Incident

After rotating a secret in AWS Secrets Manager, users started receiving:

```
401 Unauthorized
```

Application logs:

```
Token validation failed
```

Kubernetes Secret:

```
payment-secret
```

was successfully updated.

---

## Architecture

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
```

---

## Technologies

- Amazon EKS
- AWS Secrets Manager
- External Secrets Operator
- Kubernetes
- Docker
- Amazon ECR
- Flask

---

## Project Structure

```
13-secret-rotation-outage
│
├── manifests
│   ├── aws-secret.yaml
│   ├── secretstore.yaml
│   ├── externalsecret.yaml
│   └── payment-app
│       ├── app.py
│       ├── Dockerfile
│       ├── deployment.yaml
│       ├── requirements.txt
│       └── service.yaml
│
├── screenshots
└── docs
```

---

## Flow

```
AWS Secret

↓

External Secret

↓

Kubernetes Secret

↓

Application Environment Variable
```

---

## Incident Simulation

Initial Secret

```
API_TOKEN=token-v1
```

Application starts using:

```
API_TOKEN=token-v1
```

Secret rotated in AWS:

```
API_TOKEN=token-v2
```

External Secrets updates Kubernetes Secret.

Running Pod still contains:

```
API_TOKEN=token-v1
```

Result:

```
401 Unauthorized
```

---

## Investigation

Verified:

- AWS Secret updated
- External Secret synchronized
- Kubernetes Secret updated
- Running Pod still used old environment variable

---

## Root Cause

The application consumed the secret through an environment variable.

Environment variables are loaded only when the container starts.

Updating a Kubernetes Secret does not update environment variables in already running Pods.

---

## Resolution

Restart the Deployment.

```
kubectl rollout restart deployment/payment-app
```

Pods start with the latest secret.

---

## Prevention

- Use Stakater Reloader
- Reload secrets dynamically
- Use mounted secret volumes when possible
- Include secret rotation validation in deployment procedures

---

## Result

Successfully reproduced and resolved a production secret rotation outage.
