# Exercise 8: Egress Restriction Incident

## Objective

Investigate and resolve an application connectivity issue where a Kubernetes application running in Amazon EKS cannot access Amazon DynamoDB.

---

## Incident

Application logs reported:

```text
Connection timeout
```

Connectivity test:

```bash
curl dynamodb.us-east-1.amazonaws.com
```

Result:

```text
Connection timed out
```

---

## Environment

* Amazon EKS
* Kubernetes
* AWS Security Groups
* Route Tables
* Network Policies
* DynamoDB
* AWS VPC

---

## Project Structure

```text
08-egress-restriction-incident/

├── docs
├── manifests
│   ├── test-pod.yaml
│   └── deny-egress.yaml
└── screenshots
```

---

## Cluster Creation

```bash
eksctl create cluster \
--name egress-lab \
--region us-east-1 \
--nodegroup-name workers \
--node-type t3.small \
--nodes 2
```

---

## Test Pod Deployment

Created a test pod to validate external connectivity.

### test-pod.yaml

```yaml
apiVersion: v1
kind: Pod

metadata:
  name: network-test

spec:
  containers:
  - name: network-test
    image: amazonlinux:latest
    command:
      - sleep
      - "3600"
```

Deploy:

```bash
kubectl apply -f manifests/test-pod.yaml
```

Verify:

```bash
kubectl get pods
```

---

## Initial Connectivity Test

Access pod:

```bash
kubectl exec -it network-test -- bash
```

Test DynamoDB:

```bash
curl https://dynamodb.us-east-1.amazonaws.com
```

Output:

```text
healthy: dynamodb.us-east-1.amazonaws.com
```

### Observation

Connectivity to DynamoDB was successful.

This confirmed:

* DNS resolution working
* Internet access available
* Route tables functioning
* Security groups allowing outbound traffic

---

## Network Policy Investigation

Created deny-all egress policy.

### deny-egress.yaml

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy

metadata:
  name: deny-all-egress

spec:
  podSelector: {}

  policyTypes:
  - Egress

  egress: []
```

Deploy:

```bash
kubectl apply -f manifests/deny-egress.yaml
```

Verify:

```bash
kubectl get networkpolicy -A
```

Output:

```text
default deny-all-egress
```

### Result

Connectivity to DynamoDB still worked.

### Conclusion

NetworkPolicy was not being enforced by the current EKS networking configuration.

Network Policy was not the root cause.

---

## VPC Endpoint Investigation

Check VPC endpoints:

```bash
aws ec2 describe-vpc-endpoints \
--filters Name=vpc-id,Values=<VPC-ID>
```

Output:

```json
{
  "VpcEndpoints": []
}
```

### Conclusion

No DynamoDB VPC Endpoint existed.

Traffic relied on internet egress.

---

## Security Group Investigation

Retrieve cluster security group:

```bash
aws eks describe-cluster \
--name egress-lab \
--query "cluster.resourcesVpcConfig.clusterSecurityGroupId" \
--output text
```

Output:

```text
sg-084078462e3f23380
```

---

## Reproducing The Incident

Removed outbound internet access from the cluster security group.

After removing egress access, connectivity test failed:

```bash
kubectl exec -it network-test -- \
curl --connect-timeout 10 https://dynamodb.us-east-1.amazonaws.com
```

Output:

```text
connection reset by peer
error reading from error stream
```

### Incident Successfully Reproduced

Application could no longer access DynamoDB.

---

## Security Group Validation

Check outbound rules:

```bash
aws ec2 describe-security-groups \
--group-ids sg-084078462e3f23380 \
--query "SecurityGroups[0].IpPermissionsEgress"
```

Output:

```json
[
  {
    "IpProtocol": "-1",
    "UserIdGroupPairs": [
      {
        "GroupId": "sg-084078462e3f23380"
      }
    ],
    "IpRanges": [],
    "Ipv6Ranges": [],
    "PrefixListIds": []
  }
]
```

### Observation

The security group only allowed traffic within itself.

Internet egress was blocked.

---

## Route Table Investigation

Verified route tables:

```bash
aws ec2 describe-route-tables \
--filters Name=vpc-id,Values=<VPC-ID>
```

### Result

Default routes were present.

Route tables were functioning correctly.

---

## Investigation Results

### Security Groups

Result:

Yes

Issue Found:

Outbound internet access removed.

---

### Network Policies

Result:

No

Policy existed but was not enforced.

---

### Route Tables

Result:

No

Routing configuration was healthy.

---

### VPC Endpoints

Result:

No

No DynamoDB VPC Endpoint configured.

Traffic depended on internet access.

---

## Root Cause

The cluster security group outbound rules were removed.

Because no DynamoDB VPC Endpoint existed, the application depended on internet egress to reach DynamoDB.

Removing outbound access prevented communication with DynamoDB and caused connection failures.

---

## Resolution

Restore outbound access:

```bash
aws ec2 authorize-security-group-egress \
--group-id sg-084078462e3f23380 \
--ip-permissions IpProtocol=-1,IpRanges='[{CidrIp=0.0.0.0/0}]'
```

Wait for rule propagation.

Retest:

```bash
kubectl exec -it network-test -- \
curl https://dynamodb.us-east-1.amazonaws.com
```

Output:

```text
healthy: dynamodb.us-east-1.amazonaws.com
```

Connectivity restored successfully.

---

## Prevention

* Avoid accidental removal of outbound security group rules.
* Use DynamoDB VPC Endpoints for private AWS service access.
* Monitor connectivity failures using CloudWatch and application logs.
* Validate security group changes before production deployment.
* Implement change management procedures for networking updates.

---

## Skills Demonstrated

* Amazon EKS
* AWS Networking
* Security Groups
* Route Tables
* Network Policies
* VPC Endpoints
* DynamoDB Connectivity
* Kubernetes Troubleshooting
* Root Cause Analysis
* Production Incident Investigation

---

## Outcome

Successfully reproduced, investigated, fixed, and verified an Egress Restriction Incident affecting DynamoDB connectivity from Amazon EKS.
