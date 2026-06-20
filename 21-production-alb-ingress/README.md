# Exercise 21: Production ALB Ingress Setup

## Objective

Configure an AWS Application Load Balancer (ALB) Ingress to expose multiple applications running on Amazon EKS through a single entry point.

The setup must support:

* SSL Termination
* HTTP to HTTPS Redirection
* Target Group Health Checks
* Path-Based Routing

---

## Requirements

### Routes

```text
/api/*
/admin/*
/dashboard/*
```

### Additional Requirements

* SSL Support
* HTTP → HTTPS Redirect
* Target Group Health Checks

### Expected Output

* Kubernetes Ingress Manifest

---

# Architecture

```text
                    Internet
                        │
                        ▼
               AWS Application Load Balancer
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼

    /api/*         /admin/*      /dashboard/*
        │               │               │
        ▼               ▼               ▼

   api-service   admin-service   dashboard-service
        │               │               │
        ▼               ▼               ▼

     api-app       admin-app     dashboard-app
```

---

# Project Structure

```text
21-production-alb-ingress
├── README.md
├── commands.md
├── manifests
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── admin-deployment.yaml
│   ├── admin-service.yaml
│   ├── dashboard-deployment.yaml
│   ├── dashboard-service.yaml
│   └── alb-ingress.yaml
└── screenshots
```

---

# Step 1: Create API Application

Created Deployment:

api-deployment.yaml

Configuration:

* Deployment Name: api-app
* Replicas: 2
* Image: nginx
* Container Port: 80

Created Service:

api-service.yaml

Configuration:

* Service Name: api-service
* Type: ClusterIP
* Port: 80

Purpose:

Handles requests arriving at:

```text
/api/*
```

---

# Step 2: Create Admin Application

Created Deployment:

admin-deployment.yaml

Configuration:

* Deployment Name: admin-app
* Replicas: 2
* Image: nginx
* Container Port: 80

Created Service:

admin-service.yaml

Configuration:

* Service Name: admin-service
* Type: ClusterIP
* Port: 80

Purpose:

Handles requests arriving at:

```text
/admin/*
```

---

# Step 3: Create Dashboard Application

Created Deployment:

dashboard-deployment.yaml

Configuration:

* Deployment Name: dashboard-app
* Replicas: 2
* Image: nginx
* Container Port: 80

Created Service:

dashboard-service.yaml

Configuration:

* Service Name: dashboard-service
* Type: ClusterIP
* Port: 80

Purpose:

Handles requests arriving at:

```text
/ dashboard/*
```

---

# Step 4: Create ALB Ingress

Created:

alb-ingress.yaml

Purpose:

Expose all three applications through a single AWS Application Load Balancer.

---

# ALB Features Configured

## Internet Facing Load Balancer

```yaml
alb.ingress.kubernetes.io/scheme: internet-facing
```

Allows external internet access.

---

## Target Type

```yaml
alb.ingress.kubernetes.io/target-type: ip
```

Routes traffic directly to Kubernetes pods.

---

## SSL Support

```yaml
alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'
```

Enables HTTPS listener on port 443.

Production environments should use an ACM Certificate:

```yaml
alb.ingress.kubernetes.io/certificate-arn: <ACM-Certificate-ARN>
```

---

## HTTP to HTTPS Redirect

```yaml
alb.ingress.kubernetes.io/ssl-redirect: '443'
```

Automatically redirects all HTTP requests to HTTPS.

---

## Health Checks

```yaml
alb.ingress.kubernetes.io/healthcheck-path: /
```

ALB continuously checks application health.

Success Code:

```yaml
alb.ingress.kubernetes.io/success-codes: "200"
```

Healthy targets remain available.

Unhealthy targets are automatically removed from traffic routing.

---

# Path-Based Routing

Configured routes:

```text
/api/*       → api-service
/admin/*     → admin-service
/dashboard/* → dashboard-service
```

This allows a single ALB to serve multiple applications.

---

# Routing Flow

```text
Client Request
      │
      ▼

AWS ALB
      │

 ┌────┼─────────────┐
 │    │             │

 ▼    ▼             ▼

/api  /admin   /dashboard

 │      │           │

 ▼      ▼           ▼

api   admin    dashboard

service service service
```

---

# Security Features

Implemented:

✓ HTTPS Listener

✓ SSL Termination

✓ HTTP to HTTPS Redirect

✓ Health Checks

✓ Path-Based Routing

✓ Internet Facing ALB

---

# Files Created

```text
api-deployment.yaml
api-service.yaml

admin-deployment.yaml
admin-service.yaml

dashboard-deployment.yaml
dashboard-service.yaml

alb-ingress.yaml
```

---

# Outcome

Successfully designed a production-ready AWS ALB Ingress configuration supporting:

✓ Multiple Applications

✓ Path-Based Routing

✓ SSL Support

✓ HTTPS Enforcement

✓ Health Monitoring

✓ Kubernetes Ingress Integration

✓ Production Load Balancer Architecture

---

# Conclusion

This exercise demonstrated how to expose multiple Kubernetes applications through a single AWS Application Load Balancer using path-based routing. The ALB was configured with SSL support, automatic HTTP-to-HTTPS redirection, and target group health checks to provide a secure, scalable, and production-ready ingress architecture for Amazon EKS environments.
