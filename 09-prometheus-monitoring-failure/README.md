# Exercise 9: Prometheus Monitoring Failure

## Objective

Investigate and resolve a Prometheus monitoring failure where application metrics disappeared from Grafana.

---

## Incident

### Symptoms

Grafana:

```text
No Data
```

Prometheus Targets:

```text
payment-service DOWN
```

Prometheus Logs:

```text
context deadline exceeded
```

ServiceMonitor:

```yaml
port: metrics
```

Service:

```yaml
name: prometheus
```

---

## Environment

* Amazon EKS
* Kubernetes
* Prometheus Operator
* Prometheus
* Grafana
* ServiceMonitor
* Helm

---

## Project Structure

```text
09-prometheus-monitoring-failure/

├── docs
├── manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   └── servicemonitor.yaml
└── screenshots
```

---

## Cluster Creation

```bash
eksctl create cluster \
--name monitoring-lab \
--region us-east-1 \
--nodegroup-name workers \
--node-type t3.small \
--nodes 2
```

---

## Prometheus Installation

Add repository:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm repo update
```

Install monitoring stack:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
-n monitoring \
--create-namespace
```

Verify:

```bash
kubectl get pods -n monitoring
```

All monitoring components became healthy.

---

## Application Deployment

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service

spec:
  replicas: 1

  selector:
    matchLabels:
      app: payment-service

  template:
    metadata:
      labels:
        app: payment-service

    spec:
      containers:
      - name: payment-service
        image: nginx

        ports:
        - containerPort: 80
          name: prometheus
```

Deploy:

```bash
kubectl apply -f deployment.yaml
```

---

## Service Configuration

### service.yaml

```yaml
apiVersion: v1
kind: Service

metadata:
  name: payment-service

  labels:
    app: payment-service

spec:
  selector:
    app: payment-service

  ports:
  - name: prometheus
    port: 80
    targetPort: 80
```

Deploy:

```bash
kubectl apply -f service.yaml
```

---

## Reproducing The Incident

Created a ServiceMonitor with an incorrect port name.

### Broken ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor

metadata:
  name: payment-service

spec:
  selector:
    matchLabels:
      app: payment-service

  endpoints:
  - port: metrics
    interval: 15s
```

Apply:

```bash
kubectl apply -f servicemonitor.yaml
```

---

## Investigation

### ServiceMonitor Configuration

```yaml
port: metrics
```

### Service Configuration

```yaml
name: prometheus
```

### Observation

Prometheus attempted to discover a port named:

```text
metrics
```

However the Service exposed:

```text
prometheus
```

The port names did not match.

---

## Impact

Prometheus could not scrape application metrics.

Result:

```text
payment-service DOWN
```

Grafana displayed:

```text
No Data
```

Prometheus logs showed:

```text
context deadline exceeded
```

---

## Root Cause

A port name mismatch existed between ServiceMonitor and Service.

### ServiceMonitor

```yaml
port: metrics
```

### Service

```yaml
name: prometheus
```

Because Prometheus discovers scrape targets using the Service port name, the endpoint could not be resolved.

---

## Resolution

Updated ServiceMonitor to use the correct port name.

### Fixed ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor

metadata:
  name: payment-service

spec:
  selector:
    matchLabels:
      app: payment-service

  endpoints:
  - port: prometheus
    interval: 15s
```

Apply:

```bash
kubectl apply -f servicemonitor.yaml
```

---

## Verification

Verify ServiceMonitor:

```bash
kubectl get servicemonitor payment-service -o yaml
```

Confirm:

```yaml
port: prometheus
```

Open Prometheus Targets page:

```text
http://localhost:9090/targets
```

Result:

```text
payment-service UP
```

Metrics became available again.

Grafana dashboards displayed data successfully.

---

## Prevention

* Maintain consistent Service and ServiceMonitor port names.
* Validate ServiceMonitor configurations before deployment.
* Monitor Prometheus Targets page after configuration changes.
* Use infrastructure reviews and configuration validation checks.
* Include monitoring verification in CI/CD pipelines.

---

## Skills Demonstrated

* Prometheus Monitoring
* Grafana Troubleshooting
* Kubernetes Services
* ServiceMonitor Configuration
* Prometheus Operator
* Root Cause Analysis
* Production Incident Investigation
* Kubernetes Monitoring Stack

---

## Outcome

Successfully reproduced, investigated, resolved, and verified a Prometheus monitoring failure caused by a ServiceMonitor and Service port name mismatch.
