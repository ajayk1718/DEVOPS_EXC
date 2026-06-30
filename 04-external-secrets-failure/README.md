# Exercise 4: External Secrets Failure

## Objective

Implement External Secrets Operator with AWS Secrets Manager and investigate a production incident caused by IAM permission failure.

--------------------------------------------------

INCIDENT

Application startup failed:

FATAL:
Database password not found

Environment Variable DB_PASSWORD missing

External Secret Status:

READY=False

Error:

SecretSyncedError

AccessDeniedException:
User is not authorized to perform:
secretsmanager:GetSecretValue

--------------------------------------------------

ARCHITECTURE

AWS Secrets Manager
        ↓
External Secrets Operator
        ↓
Kubernetes Secret
        ↓
Application Pod

--------------------------------------------------

ENVIRONMENT

- AWS EKS
- AWS Secrets Manager
- External Secrets Operator (ESO)
- IAM Roles for Service Accounts (IRSA)
- Kubernetes
- Helm

--------------------------------------------------

PROJECT STRUCTURE

04-external-secrets-failure/
├── docs
├── manifests
│   ├── clustersecretstore.yaml
│   ├── externalsecret.yaml
│   ├── app.yaml
│   └── secret-policy.json
└── screenshots

--------------------------------------------------

STEP 1: CREATE EKS CLUSTER

eksctl create cluster \
--name external-secrets-lab \
--region us-east-1 \
--nodegroup-name workers \
--nodes 2 \
--node-type t3.small

Verify:

kubectl get nodes

--------------------------------------------------

STEP 2: INSTALL EXTERNAL SECRETS OPERATOR

helm repo add external-secrets https://charts.external-secrets.io

helm repo update

helm install external-secrets \
external-secrets/external-secrets \
-n external-secrets-system \
--create-namespace

Verify:

kubectl get pods -n external-secrets-system

--------------------------------------------------

STEP 3: CREATE SECRET IN AWS SECRETS MANAGER

aws secretsmanager create-secret \
--name db-password \
--secret-string '{"password":"SuperSecret123"}' \
--region us-east-1

Verify:

aws secretsmanager get-secret-value \
--secret-id db-password \
--region us-east-1

--------------------------------------------------

STEP 4: CREATE IAM POLICY

secret-policy.json

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    }
  ]
}

Create Policy:

aws iam create-policy \
--policy-name ExternalSecretsPolicy \
--policy-document file://manifests/secret-policy.json

--------------------------------------------------

STEP 5: CONFIGURE OIDC

eksctl utils associate-iam-oidc-provider \
--cluster external-secrets-lab \
--region us-east-1 \
--approve

--------------------------------------------------

STEP 6: CREATE IRSA

eksctl create iamserviceaccount \
--name external-secrets-sa \
--namespace external-secrets-system \
--cluster external-secrets-lab \
--attach-policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/ExternalSecretsPolicy \
--approve \
--override-existing-serviceaccounts

Restart:

kubectl rollout restart deployment external-secrets \
-n external-secrets-system

--------------------------------------------------

STEP 7: CREATE CLUSTERSECRETSTORE

apiVersion: external-secrets.io/v1
kind: ClusterSecretStore
metadata:
  name: aws-secretsmanager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets-system

Apply:

kubectl apply -f manifests/clustersecretstore.yaml

--------------------------------------------------

STEP 8: CREATE EXTERNALSECRET

apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: db-password

spec:
  refreshInterval: 1m

  secretStoreRef:
    name: aws-secretsmanager
    kind: ClusterSecretStore

  target:
    name: db-secret

  data:
  - secretKey: DB_PASSWORD
    remoteRef:
      key: db-password
      property: password

Apply:

kubectl apply -f manifests/externalsecret.yaml

Verify:

kubectl get externalsecret

Expected:

READY=True

--------------------------------------------------

STEP 9: VERIFY SECRET

kubectl get secret db-secret

Decode:

kubectl get secret db-secret \
-o jsonpath='{.data.DB_PASSWORD}' | base64 -d

Expected:

SuperSecret123

--------------------------------------------------

STEP 10: DEPLOY TEST APPLICATION

apiVersion: apps/v1
kind: Deployment
metadata:
  name: secret-app

spec:
  replicas: 1

  selector:
    matchLabels:
      app: secret-app

  template:
    metadata:
      labels:
        app: secret-app

    spec:
      containers:
      - name: app
        image: busybox

        command:
        - sh
        - -c
        - |
          echo "DB_PASSWORD=$DB_PASSWORD";
          sleep 3600

        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: DB_PASSWORD

Apply:

kubectl apply -f manifests/app.yaml

Verify:

kubectl logs deployment/secret-app

Output:

DB_PASSWORD=SuperSecret123

--------------------------------------------------

STEP 11: CREATE INCIDENT

Detach Policy:

aws iam detach-role-policy \
--role-name <ROLE_NAME> \
--policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/ExternalSecretsPolicy

Restart ESO:

kubectl rollout restart deployment external-secrets \
-n external-secrets-system

--------------------------------------------------

SYMPTOMS

kubectl get externalsecret

Output:

READY=False

Describe:

kubectl describe externalsecret db-password

Output:

SecretSyncedError

AccessDeniedException

User is not authorized to perform:
secretsmanager:GetSecretValue

--------------------------------------------------

INVESTIGATION

AWS ISSUE

IAM role lost permission:

secretsmanager:GetSecretValue

Evidence:

AccessDeniedException

--------------------------------------------------

KUBERNETES ISSUE

No issue found.

Verified:

- ClusterSecretStore valid
- ExternalSecret exists
- ServiceAccount exists
- IRSA configured

--------------------------------------------------

SECRET ISSUE

No issue found.

Verified:

- Secret exists in AWS Secrets Manager
- Secret value is valid

--------------------------------------------------

ROOT CAUSE

IAM policy granting:

secretsmanager:GetSecretValue

was detached from the IRSA role used by
External Secrets Operator.

Result:

ExternalSecret could not sync secret
from AWS Secrets Manager.

Applications depending on DB_PASSWORD
failed to start.

--------------------------------------------------

RESOLUTION

Reattach Policy:

aws iam attach-role-policy \
--role-name <ROLE_NAME> \
--policy-arn arn:aws:iam::<ACCOUNT_ID>:policy/ExternalSecretsPolicy

Restart ESO:

kubectl rollout restart deployment external-secrets \
-n external-secrets-system

Verify:

kubectl get externalsecret

Expected:

READY=True

--------------------------------------------------

PREVENTION

- Use least-privilege IAM policies
- Monitor IAM changes
- Enable CloudTrail alerts
- Use Terraform/IaC
- Implement approval workflows
- Monitor ExternalSecret health

--------------------------------------------------

OUTCOME

Successfully reproduced and resolved a production-grade
External Secrets failure.

Skills Demonstrated:

- AWS Secrets Manager
- External Secrets Operator
- Kubernetes Secret Management
- IAM Policies
- IRSA
- OIDC
- Incident Investigation
- Root Cause Analysis
- Production Troubleshooting

Exercise 4 Completed Successfully
