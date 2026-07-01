# Exercise 14 – Distributed Tracing Investigation

## Objective

Investigate a slow Checkout API using Metrics, Logs and Distributed Tracing.

The goal is to identify the bottleneck service using Prometheus, Grafana and Tempo.

---

## Incident

Users report that the Checkout API is taking several seconds to respond.

Observed Symptoms:

- Checkout API Slow
- Request Count Normal
- High P95 Latency
- Distributed Trace shows payment-service consuming most of the response time.

---

## Architecture

```
                Client
                   |
                   v
          checkout-service
                   |
                   v
         inventory-service
                   |
                   v
          payment-service
```

---

## Technologies Used

- Amazon EKS
- Kubernetes
- Docker
- Amazon ECR
- Flask
- OpenTelemetry
- Grafana
- Prometheus
- Tempo

---

## Folder Structure

```
14-distributed-tracing-investigation
│
├── manifests
│   ├── checkout-service
│   ├── inventory-service
│   └── payment-service
│
├── screenshots
│
└── docs
```

---

## Services

### checkout-service

Receives client requests.

Calls inventory-service.

---

### inventory-service

Receives requests from checkout-service.

Calls payment-service.

---

### payment-service

Processes payment requests.

Artificially delayed by:

```python
time.sleep(4.2)
```

to simulate a production incident.

---

## Monitoring Stack

Prometheus

- Metrics Collection

Grafana

- Dashboards
- Explore

Tempo

- Distributed Tracing

OpenTelemetry

- Trace Exporter
- Flask Instrumentation
- Requests Instrumentation

---

## Flow

```
Client

↓

Checkout Service

↓

Inventory Service

↓

Payment Service

↓

Tempo

↓

Grafana
```

---

## Incident Simulation

Artificial latency introduced inside payment-service.

```python
time.sleep(4.2)
```

Result:

```
Checkout API

↓

Inventory

↓

Payment (4.2 seconds)
```

---

## Investigation

### Metrics

Observed:

- High P95 Latency
- Request Count Normal

---

### Logs

Verified request flow across all services.

---

### Traces

Tempo clearly identifies payment-service as the slowest span.

---

## Root Cause

payment-service contained an artificial delay.

```python
time.sleep(4.2)
```

This delay propagated through the complete request chain.

---

## Resolution

Remove the delay.

Redeploy payment-service.

Latency returns to normal.

---

## Prevention

- Distributed Tracing
- Latency Alerts
- SLO Monitoring
- Prometheus Alert Rules
- Grafana Dashboards

---

## Commands Used

Build

```
docker build
```

Push

```
docker push
```

Deploy

```
kubectl apply
```

Logs

```
kubectl logs
```

Port Forward

```
kubectl port-forward
```

Tracing

```
Grafana
↓

Explore

↓

Tempo
```

---

## Result

Successfully simulated a production incident and identified the bottleneck using:

- Metrics
- Logs
- Distributed Traces

Exercise Status

Completed
