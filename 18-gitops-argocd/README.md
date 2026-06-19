# Exercise 18: GitOps Platform Using ArgoCD

## Objective

Build a GitOps deployment platform using ArgoCD and Amazon EKS.

The application should be deployed through:

Git Commit → ArgoCD → EKS

The platform must support:

* Auto Sync
* Self Heal
* Pruning

---

# Architecture

```text
Developer
    │
    ▼
GitHub Repository
    │
    ▼
ArgoCD
    │
    ▼
Amazon EKS
    │
    ▼
Deployment / Pods / Services
```

ArgoCD continuously monitors the Git repository and ensures the Kubernetes cluster state matches the desired state stored in Git.

---

# Prerequisites

* AWS Account
* AWS CLI
* kubectl
* eksctl
* GitHub Repository
* ArgoCD
* Amazon EKS Cluster

---

# Project Structure

```text
18-gitops-argocd
├── README.md
├── commands.md
├── theory.md
├── gitops
│   ├── dev
│   │   ├── nginx-deployment.yaml
│   │   └── nginx-service.yaml
│   ├── qa
│   └── prod
└── screenshots
```

---

# Step 1: Create EKS Cluster

Created EKS cluster using eksctl.

```bash
eksctl create cluster \
--name gitops-lab \
--region us-east-1 \
--nodegroup-name workers \
--node-type t3.small \
--nodes 2
```

Verify:

```bash
kubectl get nodes
```

Output:

```text
2 Worker Nodes in Ready State
```

---

# Step 2: Install ArgoCD

Create namespace:

```bash
kubectl create namespace argocd
```

Install ArgoCD:

```bash
kubectl apply -n argocd \
-f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verify:

```bash
kubectl get pods -n argocd
```

Components installed:

* argocd-server
* argocd-repo-server
* argocd-application-controller
* argocd-applicationset-controller
* argocd-notifications-controller
* argocd-dex-server
* argocd-redis

All pods reached Running state.

---

# Step 3: Access ArgoCD UI

Retrieve admin password:

```bash
kubectl get secret argocd-initial-admin-secret \
-n argocd \
-o jsonpath="{.data.password}" | base64 -d
```

Port Forward:

```bash
kubectl port-forward svc/argocd-server \
-n argocd 9090:443
```

Access:

```text
https://localhost:9090
```

Login:

```text
Username: admin
Password: Retrieved Secret
```

---

# Step 4: Create GitOps Manifests

Created deployment manifest:

```text
gitops/dev/nginx-deployment.yaml
```

Created service manifest:

```text
gitops/dev/nginx-service.yaml
```

Deployment specification:

```yaml
replicas: 2
image: nginx:latest
```

---

# Step 5: Push Manifests to GitHub

```bash
git add .
git commit -m "Exercise 18 GitOps Setup"
git push origin main
```

GitHub becomes the Single Source of Truth.

---

# Step 6: Create ArgoCD Application

Created application:

```text
dev-nginx
```

Source:

```text
Repository:
https://github.com/ajayk1718/DEVOPS_EXC.git

Path:
18-gitops-argocd/gitops/dev

Branch:
main
```

Destination:

```text
Cluster:
https://kubernetes.default.svc

Namespace:
default
```

Enabled:

* Automatic Sync
* Self Heal
* Pruning
* Auto Create Namespace

---

# Step 7: Initial Deployment

ArgoCD automatically deployed:

```text
Deployment
ReplicaSet
Pods
```

Verification:

```bash
kubectl get deploy
kubectl get pods
```

Result:

```text
nginx-dev
2 Running Pods
```

---

# Step 8: Auto Sync Demonstration

Modified:

```yaml
replicas: 2
```

Changed to:

```yaml
replicas: 4
```

Committed and pushed changes:

```bash
git add .
git commit -m "Scale nginx to 4 replicas"
git push origin main
```

ArgoCD automatically detected the Git change.

Verification:

```bash
kubectl get deploy
kubectl get pods
```

Result:

```text
4 Running Pods
```

Auto Sync successfully demonstrated.

---

# Step 9: Self Heal Demonstration

Manually modified cluster state:

```bash
kubectl scale deployment nginx-dev --replicas=1
```

Expected State in Git:

```yaml
replicas: 4
```

ArgoCD detected configuration drift.

Automatically restored deployment to:

```text
4 Replicas
```

Verification:

```bash
kubectl get deploy
```

Result:

```text
4/4 Available
```

Self Heal successfully demonstrated.

---

# Step 10: Pruning Demonstration

Deleted manifest:

```text
nginx-service.yaml
```

Committed and pushed changes:

```bash
git add .
git commit -m "Pruning Test"
git push origin main
```

ArgoCD detected resource removal from Git.

Automatically removed corresponding Kubernetes resource from cluster.

Verification:

```bash
kubectl get svc
```

Result:

```text
Service removed automatically
```

Pruning successfully demonstrated.

---

# Features Demonstrated

## Auto Sync

Automatically synchronizes cluster state with Git repository changes.

## Self Heal

Automatically corrects manual changes made directly to the cluster.

## Pruning

Automatically removes resources that no longer exist in Git.

---

# Outcome

Successfully implemented a complete GitOps deployment platform using ArgoCD and Amazon EKS.

The platform provides:

* Continuous Deployment
* Drift Detection
* Automated Recovery
* Declarative Infrastructure Management
* Git as Single Source of Truth

---

# Conclusion

This exercise demonstrated how ArgoCD continuously monitors Git repositories and ensures Kubernetes clusters always match the desired state defined in Git.

GitOps improves deployment reliability, traceability, consistency, and operational efficiency while reducing manual intervention.
