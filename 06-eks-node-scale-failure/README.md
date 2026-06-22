# Exercise 6: EKS Node Scale Failure

## Objective

Investigate an application scaling failure in Amazon EKS where the Horizontal Pod Autoscaler (HPA) requests additional replicas, but pods remain pending due to insufficient node resources and autoscaler issues.

---

## Incident

Application failed to scale.

Observed:

HPA Status:

Desired Replicas: 15

Current Replicas: 5

Pending Pods:

0/3 nodes available:
Insufficient CPU

Cluster Autoscaler Logs:

No node group config found

---

## Environment

* AWS EKS
* Kubernetes
* Horizontal Pod Autoscaler (HPA)
* Metrics Server
* Cluster Autoscaler
* Nginx Test Application

---

## Project Structure

06-eks-node-scale-failure/
├── docs
├── manifests
│   └── stress-app.yaml
└── screenshots

---

## Architecture

User Traffic
↓
Application Deployment
↓
Horizontal Pod Autoscaler
↓
Kubernetes Scheduler
↓
Worker Nodes
↓
Cluster Autoscaler

---

## Create Test Application

Create deployment with high CPU requests.

stress-app.yaml

apiVersion: apps/v1
kind: Deployment

metadata:
name: stress-app

spec:
replicas: 5

selector:
matchLabels:
app: stress-app

template:
metadata:
labels:
app: stress-app

```
spec:
  containers:
  - name: stress-app
    image: nginx

    resources:
      requests:
        cpu: "1000m"
      limits:
        cpu: "1000m"
```

Apply:

kubectl apply -f manifests/stress-app.yaml

---

## Observe Pod Scheduling Failure

Check Pods:

kubectl get pods

Observed:

Running
Running
Pending
Pending
Pending

Several pods remained in Pending state.

---

## Investigate Pending Pods

Describe pod:

kubectl describe pod <pending-pod>

Observed:

Events:

FailedScheduling

0/2 nodes are available:

Insufficient cpu

No preemption victims found

This confirms that the scheduler could not place the pod because worker nodes lacked available CPU resources.

---

## Check Node Utilization

View node metrics:

kubectl top nodes

Example Output:

CPU Usage: 1%
Memory Usage: 33%

Although CPU utilization was low, scheduling still failed.

---

## Check Resource Allocation

kubectl describe nodes | grep -A5 "Allocated resources"

Observed:

Node 1:
CPU Requests = 64%

Node 2:
CPU Requests = 75%

Pods requested large CPU reservations:

cpu: 1000m

Kubernetes schedules based on requested resources, not actual usage.

---

## Create Horizontal Pod Autoscaler

Create HPA:

kubectl autoscale deployment stress-app 
--cpu-percent=50 
--min=5 
--max=15

Verify:

kubectl get hpa

Output:

NAME         REFERENCE               TARGETS
stress-app   Deployment/stress-app

MINPODS = 5
MAXPODS = 15

---

## Investigation

### HPA Issue

Result:

No

Evidence:

* HPA was created successfully.
* Minimum replicas configured.
* Maximum replicas configured.
* Scaling configuration valid.

Conclusion:

HPA configuration was not the cause of the incident.

---

### Node Issue

Result:

Yes

Evidence:

FailedScheduling

0/2 nodes available:

Insufficient cpu

Pods could not be scheduled due to insufficient worker node capacity.

Conclusion:

Node capacity was exhausted.

---

### Autoscaler Issue

Result:

Yes

Evidence:

No additional worker nodes were created despite pending pods.

Production Incident Example:

Cluster Autoscaler Logs:

No node group config found

Possible Causes:

* Cluster Autoscaler not installed.
* Node group auto-discovery not configured.
* Incorrect IAM permissions.
* Invalid autoscaler configuration.

Conclusion:

Autoscaler could not provision new nodes.

---

## Root Cause

The Horizontal Pod Autoscaler requested additional replicas.

The Kubernetes scheduler attempted to place the new pods.

Worker nodes did not have sufficient CPU resources to satisfy pod requests.

Cluster Autoscaler failed to add new worker nodes because node group configuration was missing or invalid.

Result:

Desired Replicas: 15

Current Replicas: 5

Pending Pods

Insufficient CPU

Application could not scale.

---

## Resolution

1. Increase node group size.

2. Configure Cluster Autoscaler correctly.

3. Enable node group auto-discovery.

4. Validate IAM permissions.

5. Reduce excessive CPU requests if appropriate.

6. Monitor cluster capacity proactively.

---

## Prevention

* Configure Cluster Autoscaler for all node groups.
* Enable autoscaler monitoring and alerting.
* Review CPU requests before deployment.
* Implement capacity planning.
* Monitor pending pods continuously.
* Validate HPA and autoscaler integration during testing.

---

## Outcome

Successfully reproduced and investigated an EKS scaling failure.

Skills Demonstrated:

* Amazon EKS
* Kubernetes Scheduling
* Horizontal Pod Autoscaler
* Cluster Capacity Analysis
* Resource Requests and Limits
* Pending Pod Troubleshooting
* Cluster Autoscaler Investigation
* Root Cause Analysis
* Production Incident Response

Exercise 6 Completed Successfully.
