# Exercise 7: ALB Ingress Failure

## Objective

Investigate and resolve an Application Load Balancer (ALB) Ingress failure in Amazon EKS.

---

## Incident

Users reported that the application was inaccessible.

Observed Symptoms:

* 504 Gateway Timeout
* Ingress Address not assigned
* Target registration failed
* AWS Load Balancer Controller reported subnet discovery errors

---

## Environment

* Amazon EKS
* AWS Load Balancer Controller
* Kubernetes Ingress
* Application Load Balancer (ALB)
* Nginx Application

---

## Project Structure

07-alb-ingress-failure/

├── docs

├── manifests

│   ├── app.yaml

│   ├── service.yaml

│   └── ingress.yaml

└── screenshots

---

## Application Deployment

Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment

metadata:
  name: web-app

spec:
  replicas: 2

  selector:
    matchLabels:
      app: web-app

  template:
    metadata:
      labels:
        app: web-app

    spec:
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
```

Apply:

```bash
kubectl apply -f manifests/app.yaml
```

---

## Service Creation

```yaml
apiVersion: v1
kind: Service

metadata:
  name: web-app

spec:
  selector:
    app: web-app

  ports:
  - port: 80
    targetPort: 80
```

Apply:

```bash
kubectl apply -f manifests/service.yaml
```

---

## Ingress Creation

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress

metadata:
  name: web-app-ingress

  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip

spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app
            port:
              number: 80
```

Apply:

```bash
kubectl apply -f manifests/ingress.yaml
```

---

## Initial Investigation

Check ingress:

```bash
kubectl get ingress
```

Observed:

```text
ADDRESS:
<empty>
```

Application was not reachable.

---

## AWS Load Balancer Controller Logs

Investigated controller logs:

```bash
kubectl logs -n kube-system deployment/aws-load-balancer-controller
```

Observed:

```text
couldn't auto-discover subnets

unable to resolve at least one subnet

Evaluated 0 subnets
```

---

## Root Cause 1

### Missing Subnet Tags

The AWS Load Balancer Controller could not identify suitable subnets for ALB creation.

Required tags were missing.

Missing Tags:

Public Subnets:

```text
kubernetes.io/role/elb=1
```

Private Subnets:

```text
kubernetes.io/role/internal-elb=1
```

Cluster Discovery:

```text
kubernetes.io/cluster/devops-lab=shared
```

---

## Resolution 1

Tagged Public Subnets:

```bash
aws ec2 create-tags \
--resources subnet-08da06bbc17cc3205 subnet-0a92bbc74051b6ae1 \
--tags Key=kubernetes.io/role/elb,Value=1
```

Tagged Private Subnets:

```bash
aws ec2 create-tags \
--resources subnet-09a8db64da0ecd961 subnet-0b2eb104c2a47b084 \
--tags Key=kubernetes.io/role/internal-elb,Value=1
```

Tagged Cluster Discovery:

```bash
aws ec2 create-tags \
--resources \
subnet-08da06bbc17cc3205 \
subnet-09a8db64da0ecd961 \
subnet-0b2eb104c2a47b084 \
subnet-0a92bbc74051b6ae1 \
--tags Key=kubernetes.io/cluster/devops-lab,Value=shared
```

---

## Secondary Failure

After subnet tagging, a new error appeared.

Controller Logs:

```text
InvalidParameterValue: vpc-id
```

---

## Root Cause 2

### Invalid VPC ID Configuration

Controller Helm values:

Incorrect:

```text
vpcId: 01919abaf9d2a2311
```

Correct:

```text
vpcId: vpc-01919abaf9d2a2311
```

The VPC prefix was missing.

---

## Resolution 2

Updated controller configuration:

```bash
helm upgrade aws-load-balancer-controller eks/aws-load-balancer-controller \
-n kube-system \
--set clusterName=devops-lab \
--set serviceAccount.create=false \
--set serviceAccount.name=aws-load-balancer-controller \
--set region=us-east-1 \
--set vpcId=vpc-01919abaf9d2a2311
```

Verify:

```bash
helm get values aws-load-balancer-controller -n kube-system
```

Output:

```text
vpcId: vpc-01919abaf9d2a2311
```

---

## Successful Deployment

Controller Logs:

```text
created targetGroup

created loadBalancer

created listener

created listener rule

created targetGroupBinding

successfully deployed model

registered targets

Successful reconcile
```

The ALB was successfully provisioned and targets were registered.

---

## Investigation Results

### Application Issue

Result:

No

Evidence:

* Pods running
* Service available
* Backend endpoints healthy

---

### Ingress Issue

Result:

Yes

Evidence:

* Ingress address missing
* Failed ALB provisioning
* FailedBuildModel events

---

### AWS Issue

Result:

Yes

Evidence:

* Missing subnet tags
* Invalid VPC ID configuration

---

## Final Root Cause

The AWS Load Balancer Controller could not discover suitable subnets because required subnet tags were missing.

After subnet tagging, the controller encountered an invalid VPC ID configuration.

Both issues prevented ALB creation and caused application inaccessibility.

---

## Prevention

* Tag EKS subnets correctly during cluster creation.
* Validate AWS Load Balancer Controller configuration.
* Verify VPC ID format before deployment.
* Monitor controller logs continuously.
* Use infrastructure validation before production releases.

---

## Outcome

Successfully reproduced, investigated, fixed, and verified an ALB Ingress failure.

Skills Demonstrated:

* Amazon EKS
* AWS Load Balancer Controller
* Kubernetes Ingress
* ALB Troubleshooting
* AWS Networking
* VPC Configuration
* Subnet Tagging
* IAM Roles for Service Accounts (IRSA)
* Production Incident Response
* Root Cause Analysis

Exercise 7 Completed Successfully.
