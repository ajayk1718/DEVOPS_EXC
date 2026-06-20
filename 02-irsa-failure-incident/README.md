# Exercise 2: IAM / IRSA Failure Investigation

## Objective

Investigate and resolve an application failure where a Kubernetes application running on Amazon EKS suddenly lost access to DynamoDB.

The goal was to identify:

- Why the Node IAM Role was being used.
- Why IRSA (IAM Roles for Service Accounts) was not working.
- How to restore secure access to DynamoDB.

---

# Incident Description

Application Logs:

2026-05-10T08:12:13Z ERROR

botocore.exceptions.ClientError:

An error occurred (AccessDeniedException)
when calling the GetItem operation:

User:
arn:aws:sts::123456789012:assumed-role/eks-nodegroup-role

is not authorized to perform:
dynamodb:GetItem

on resource:
arn:aws:dynamodb:ap-south-1:123456789012:table/customer-data

---

# Expected Architecture

Pod
↓
ServiceAccount
↓
IAM Role (IRSA)
↓
DynamoDB

The application should access DynamoDB through an IAM Role attached to a Kubernetes ServiceAccount using IRSA.

---

# Lab Environment Created

Components:

- Amazon EKS Cluster
- DynamoDB Table
- OIDC Provider
- IAM Policy
- IAM Role for ServiceAccount
- Kubernetes ServiceAccount
- Test Pod
- DynamoDB

---

# Step 1: Create EKS Cluster

Created EKS Cluster:

Name:
irsa-failure-lab

Verified Cluster:

kubectl get nodes

Result:

2 Worker Nodes in Ready State

---

# Step 2: Create DynamoDB Table

Created DynamoDB Table:

customer-data

Primary Key:

CustomerID

Verified:

aws dynamodb list-tables

Result:

customer-data

---

# Step 3: Enable OIDC Provider

Enabled OIDC Provider:

eksctl utils associate-iam-oidc-provider \
--cluster irsa-failure-lab \
--region us-east-1 \
--approve

Purpose:

Allows Kubernetes ServiceAccounts to assume IAM Roles.

---

# Step 4: Create IAM Policy

Created Policy:

DynamoDBIRSAFailurePolicy

Permissions:

- dynamodb:GetItem
- dynamodb:PutItem
- dynamodb:UpdateItem

Resource:

customer-data table

---

# Step 5: Create IRSA ServiceAccount

Created ServiceAccount:

dynamodb-sa

Attached:

DynamoDBIRSAFailurePolicy

Verified:

kubectl describe sa dynamodb-sa

Result:

Annotation Present:

eks.amazonaws.com/role-arn

This confirmed IRSA configuration.

---

# Step 6: Create Test Pod

Created Pod:

dynamodb-test

Configuration:

serviceAccountName: dynamodb-sa

Purpose:

Simulate application access to DynamoDB.

---

# Step 7: Verify Working State

Entered Pod:

kubectl exec -it dynamodb-test -- sh

Checked Identity:

aws sts get-caller-identity

Output:

arn:aws:sts::181640953339:assumed-role/eksctl-irsa-failure-lab-addon-iamserviceaccount-role

Observation:

Pod successfully assumed the IRSA Role.

---

# Step 8: Verify DynamoDB Access

Executed:

aws dynamodb put-item

Result:

Success

Executed:

aws dynamodb get-item

Result:

Successfully retrieved record.

Observation:

IRSA was functioning correctly and DynamoDB access worked.

---

# Step 9: Create Failure Scenario

Modified Pod Configuration:

Changed:

serviceAccountName: dynamodb-sa

To:

serviceAccountName: default

Redeployed Pod.

Purpose:

Simulate production failure.

---

# Step 10: Investigate Incident

Checked Identity:

aws sts get-caller-identity

Output:

arn:aws:sts::181640953339:assumed-role/eksctl-irsa-failure-lab-nodegroup-NodeInstanceRole

Observation:

Pod was using the Node IAM Role.

Expected:

IRSA Role

Actual:

Node Role

---

# Step 11: Reproduce Error

Executed:

aws dynamodb get-item

Result:

AccessDeniedException

Error:

User:
assumed-role/NodeInstanceRole

is not authorized to perform:

dynamodb:GetItem

Observation:

Exact incident successfully reproduced.

---

# Root Cause Analysis

Root Cause:

The pod was deployed using the default ServiceAccount instead of the IRSA-enabled ServiceAccount.

Because of this:

Pod
↓
Default ServiceAccount
↓
No IRSA Credentials
↓
AWS SDK Fallback
↓
Node IAM Role
↓
AccessDeniedException

The Node IAM Role did not have permission to access DynamoDB.

---

# Resolution

Updated Pod Configuration:

Changed:

serviceAccountName: default

Back To:

serviceAccountName: dynamodb-sa

Deleted old pod.

Redeployed application.

---

# Step 12: Verify Fix

Checked Identity:

aws sts get-caller-identity

Output:

arn:aws:sts::181640953339:assumed-role/eksctl-irsa-failure-lab-addon-iamserviceaccount-role

Observation:

IRSA Role restored successfully.

---

# Step 13: Verify DynamoDB Access

Executed:

aws dynamodb get-item

Result:

Success

Retrieved Customer Record:

CustomerID = 101
Name = Ajay

Observation:

Application regained DynamoDB access.

Incident resolved successfully.

---

# Answers to Exercise Questions

## Why node role is being used?

The pod was using the default ServiceAccount instead of the IRSA-enabled ServiceAccount. Since IRSA credentials were unavailable, AWS SDK automatically fell back to the EKS Node IAM Role.

---

## Why IRSA is not working?

IRSA was not working because the pod was not associated with the ServiceAccount that contained the IAM Role annotation.

The pod was using:

default

instead of:

dynamodb-sa

---

## How to fix?

Update the pod or deployment to use the IRSA-enabled ServiceAccount.

Example:

serviceAccountName: dynamodb-sa

Redeploy the workload and verify:

aws sts get-caller-identity

The output should show the IRSA Role instead of the Node Role.

---

# Outcome

Successfully:

✓ Created EKS Cluster

✓ Configured IRSA

✓ Connected DynamoDB

✓ Verified Working State

✓ Created Failure Scenario

✓ Reproduced Production Incident

✓ Investigated Root Cause

✓ Restored IRSA Configuration

✓ Verified DynamoDB Access

✓ Resolved Incident

---

# Conclusion

This exercise demonstrated a real-world IAM and IRSA troubleshooting scenario in Amazon EKS. By intentionally breaking the ServiceAccount configuration, the application lost access to DynamoDB and fell back to the Node IAM Role. Through systematic investigation using AWS STS and Kubernetes ServiceAccount validation, the root cause was identified and corrected. The application successfully resumed DynamoDB access after restoring the IRSA-enabled ServiceAccount.
