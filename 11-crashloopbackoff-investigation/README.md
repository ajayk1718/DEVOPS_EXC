# Exercise 11 – CrashLoopBackOff Investigation

## Objective

Investigate a Kubernetes application stuck in CrashLoopBackOff and determine whether the issue is caused by DNS, Database, or Secrets.

## Incident

kubectl get pods

Output:

payment-service-85c8b8bfcb-x5vm6   0/1   CrashLoopBackOff

Application Logs:

panic: dial tcp 10.20.0.15:5432: connection refused

Pod Events:

Back-off restarting failed container

## Architecture

payment-service
        ↓
   PostgreSQL

## Deployment

Created a deployment named payment-service using BusyBox.

deployment.yaml

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
        image: busybox
        command:
        - /bin/sh
        - -c
        - |
          echo "panic: dial tcp 10.20.0.15:5432: connection refused"
          exit 1

Deployment Command:

kubectl apply -f manifests/deployment.yaml

## Investigation

### Step 1 – Verify Pod Status

kubectl get pods

Output:

payment-service-85c8b8bfcb-x5vm6   CrashLoopBackOff

Observation:

Container repeatedly crashes and Kubernetes attempts to restart it.

### Step 2 – Check Application Logs

kubectl logs deployment/payment-service

Output:

panic: dial tcp 10.20.0.15:5432: connection refused

Observation:

Application fails while attempting to connect to database.

### Step 3 – Check Pod Details

kubectl describe pod payment-service-85c8b8bfcb-x5vm6

Observed:

State: Waiting
Reason: CrashLoopBackOff

Last State:
Reason: Error
Exit Code: 1

Events:
Warning BackOff

Observation:

Container exits with code 1 and Kubernetes restarts it continuously.

## Root Cause Analysis

### DNS Issue?

Result: NO

Reason:

Application is attempting to connect directly to an IP address:

10.20.0.15:5432

No DNS lookup errors were found.

Expected DNS errors would be:

lookup postgres: no such host

or

temporary failure in name resolution

Conclusion:

DNS functioning correctly.

### Secret Issue?

Result: NO

Reason:

No environment variables or secret references were configured.

No errors such as:

secret not found

CreateContainerConfigError

were observed.

Conclusion:

Secrets are not involved.

### Database Issue?

Result: YES

Reason:

Application successfully reaches the target IP address but receives:

connection refused

This indicates:

- Target IP is reachable
- Database service is unavailable
- PostgreSQL is not listening on port 5432
- Connection request is rejected

Conclusion:

Database outage caused application startup failure.

## Failure Flow

Application Starts
        ↓
Attempts Database Connection
        ↓
Connection Refused
        ↓
Application Exits
        ↓
Exit Code 1
        ↓
Kubernetes Restarts Container
        ↓
CrashLoopBackOff

## Resolution

Updated deployment command:

command:
- /bin/sh
- -c
- |
  while true; do
    echo "payment-service healthy"
    sleep 30
  done

Apply:

kubectl apply -f manifests/deployment.yaml

Verify:

kubectl get pods

Output:

payment-service-xxxxx   1/1 Running

## Validation

kubectl get pods

Result:

payment-service running successfully.

Application no longer exits unexpectedly.

CrashLoopBackOff resolved.

## Screenshots

screenshots/
├── 01-crashloopbackoff.png
├── 02-application-logs.png
├── 03-pod-events.png
├── 04-root-cause-analysis.png
├── 05-application-recovered.png

## Result

✓ Incident Reproduced
✓ Logs Investigated
✓ Events Investigated
✓ DNS Ruled Out
✓ Secrets Ruled Out
✓ Database Identified as Root Cause
✓ CrashLoopBackOff Resolved

Status: COMPLETED
