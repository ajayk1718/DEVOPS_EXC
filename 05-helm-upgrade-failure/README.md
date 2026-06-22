# Exercise 5: Helm Upgrade Failure

## Objective

Investigate and resolve a Helm upgrade failure caused by modification of an immutable Kubernetes Deployment field.

---

## Incident

Production deployment failed during a Helm upgrade.

Error:

```text
UPGRADE FAILED:

cannot patch Deployment:

spec.selector:
Invalid value:
field is immutable
```

---

## Environment

* AWS EKS
* Kubernetes
* Helm
* Nginx Application

---

## Project Structure

```text
05-helm-upgrade-failure/
├── docs
├── payment-service
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates
│   └── charts
└── screenshots
```

---

## Create Helm Chart

Generate chart:

```bash
helm create payment-service
```

Verify structure:

```bash
tree -L 2
```

---

## Install Version 1

Install Helm release:

```bash
helm install payment-service ./payment-service
```

Verify:

```bash
helm list

kubectl get deploy
```

Output:

```text
payment-service
```

---

## Deployment Selector

Deployment created with selector:

```yaml
selector:
  matchLabels:
    app.kubernetes.io/instance: payment-service
    app.kubernetes.io/name: payment-service
```

Verify:

```bash
kubectl get deploy payment-service -o yaml | grep -A5 selector
```

---

## Incident Creation

Modify Helm chart.

File:

```text
payment-service/templates/_helpers.tpl
```

Original:

```yaml
{{- define "payment-service.selectorLabels" -}}
app.kubernetes.io/name: payment-service
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Changed Version 2:

```yaml
{{- define "payment-service.selectorLabels" -}}
app.kubernetes.io/name: payment-service-v2
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

---

## Trigger Failure

Run upgrade:

```bash
helm upgrade payment-service ./payment-service
```

Observed:

```text
Error: UPGRADE FAILED:

cannot patch "payment-service" with kind Deployment:

Deployment.apps "payment-service" is invalid:

spec.selector:
Invalid value:

field is immutable
```

---

## Investigation

### What Changed?

Version 1:

```yaml
app.kubernetes.io/name: payment-service
```

Version 2:

```yaml
app.kubernetes.io/name: payment-service-v2
```

The Deployment selector was modified.

---

### Why Immutable Field Errors Occur

The Deployment selector defines which Pods belong to a Deployment.

Example:

```yaml
spec:
  selector:
    matchLabels:
      app: payment
```

Kubernetes uses this selector to manage:

* Pods
* ReplicaSets
* Deployment ownership

Changing the selector after creation can cause:

* Pod ownership conflicts
* ReplicaSet inconsistencies
* Service routing problems
* Orphaned resources

Therefore Kubernetes marks Deployment selectors as immutable.

---

## Root Cause

The Helm chart upgrade modified:

```yaml
spec.selector.matchLabels
```

from:

```yaml
app.kubernetes.io/name: payment-service
```

to:

```yaml
app.kubernetes.io/name: payment-service-v2
```

Since Deployment selectors are immutable, Kubernetes rejected the patch request and the Helm upgrade failed.

---

## Resolution

Restore the original selector.

Updated file:

```yaml
{{- define "payment-service.selectorLabels" -}}
app.kubernetes.io/name: payment-service
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

Run upgrade again:

```bash
helm upgrade payment-service ./payment-service
```

Output:

```text
Release "payment-service" has been upgraded.
Happy Helming!
```

---

## Safe Upgrade Approaches

### Option 1 (Recommended)

Keep the selector unchanged.

Modify only:

* Container image
* Replicas
* Resources
* Environment variables

---

### Option 2

Delete and recreate Deployment.

```bash
helm uninstall payment-service

helm install payment-service ./payment-service
```

Note:

```text
Causes downtime.
```

---

### Option 3

Create a new Deployment.

Example:

```text
payment-service-v2
```

Deploy alongside the old version and gradually shift traffic.

---

## Prevention

* Never modify Deployment selectors after creation.
* Review Helm chart changes before upgrades.
* Use Helm diff before deployment.
* Validate upgrades in non-production environments.
* Use blue-green or canary deployment strategies for major changes.

---

## Outcome

Successfully reproduced and resolved a Helm upgrade failure caused by an immutable Deployment selector.

### Skills Demonstrated

* Helm Chart Management
* Kubernetes Deployments
* Immutable Fields
* Helm Upgrade Troubleshooting
* Incident Investigation
* Root Cause Analysis
* Production Deployment Debugging

Exercise 5 Completed Successfully.
