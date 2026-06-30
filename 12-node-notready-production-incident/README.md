# Exercise 12 – Node NotReady Production Incident

## Objective

Investigate and recover a Kubernetes worker node that became unavailable due to disk pressure.

## Incident

Node Status:

NotReady

Node Conditions:

DiskPressure=True

Journal:

no space left on device

Additional Evidence:

du -sh /var/log/containers/*

95GB consumed

## Architecture

Application Pods
        ↓
Worker Node
        ↓
Kubelet
        ↓
Container Runtime
        ↓
Disk Storage

## Deployment

Created a sample application.

deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  replicas: 3
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

Deployment Command:

kubectl apply -f manifests/deployment.yaml

## Investigation

### Step 1 – Verify Node Health

Command:

kubectl get nodes

Result:

Both worker nodes were in Ready state.

### Step 2 – Inspect Node

Command:

kubectl describe node <node-name>

Observed:

MemoryPressure=False

DiskPressure=False

PIDPressure=False

Ready=True

Node conditions were healthy before simulation.

### Step 3 – Prepare Node for Maintenance

Command:

kubectl cordon <node-name>

Result:

Ready,SchedulingDisabled

Observation:

The node stopped accepting new pods while existing workloads continued running.

### Step 4 – Drain the Node

Command:

kubectl drain <node-name> \
--ignore-daemonsets \
--delete-emptydir-data

Observed:

Application pods were safely evicted.

DaemonSet pods (aws-node, kube-proxy) remained on the node.

Kubernetes automatically recreated application pods on the healthy worker node.

### Step 5 – Verify Workload Migration

Command:

kubectl get pods -o wide

Result:

All application pods were successfully running on the remaining healthy node.

Application availability was maintained during node maintenance.

### Step 6 – Recovery

In a real production environment the engineer would:

- Login to the affected node
- Check disk usage

df -h

- Identify large log files

du -sh /var/log/containers/*

- Remove or rotate unnecessary logs

- Verify DiskPressure becomes False

- Restart kubelet if required

Since the managed EKS worker node did not provide SSH or SSM access by default, only the Kubernetes operational recovery process was demonstrated.

### Step 7 – Return Node to Service

Command:

kubectl uncordon <node-name>

Result:

Node status returned to:

Ready

The node was again available for scheduling workloads.

## Root Cause Analysis

### DNS Issue?

Result:

Not Applicable

### Application Issue?

Result:

Not Applicable

### Kubernetes Issue?

Result:

No

The Kubernetes cluster functioned correctly by rescheduling workloads.

### Root Cause

The simulated production incident represents a worker node experiencing disk exhaustion.

Excessive container logs consume node storage.

When available disk space becomes critically low:

- DiskPressure=True
- Kubelet cannot manage workloads correctly
- Node eventually becomes NotReady

## Production Recovery Procedure

Investigate Node

↓

Check Disk Usage

↓

Identify Large Log Files

↓

Clean or Rotate Logs

↓

Verify Free Disk Space

↓

DiskPressure=False

↓

Uncordon Node

↓

Node Ready

## Commands Used

kubectl get nodes

kubectl describe node

kubectl cordon <node>

kubectl drain <node> \
--ignore-daemonsets \
--delete-emptydir-data

kubectl get pods -o wide

kubectl uncordon <node>

## Key Learnings

- Understanding Kubernetes node conditions
- DiskPressure detection
- Safe node maintenance
- Difference between cordon and drain
- Automatic workload rescheduling
- Returning a repaired node back to production

## Screenshots

screenshots/

01-cluster-ready.png

02-node-description.png

03-node-cordoned.png

04-node-drained.png

05-pods-migrated.png

06-node-recovered.png

## Result

✓ Investigated node health

✓ Understood DiskPressure

✓ Performed safe node maintenance

✓ Migrated workloads successfully

✓ Restored node to service

Status: COMPLETED
