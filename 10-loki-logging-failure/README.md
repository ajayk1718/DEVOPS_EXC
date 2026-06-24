# Exercise 10 – Loki Logging Failure

## Objective
Investigate and resolve a logging pipeline failure where application logs stopped appearing in Grafana.

## Incident

Grafana:
No Logs Available

Promtail Logs:
error sending batch
connect: connection refused

Loki:
Unavailable

## Architecture

Application
    ↓
Promtail
    ↓
Loki
    ↓
Grafana

## Deployment

Install Loki Stack:

helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install loki grafana/loki-stack \
-n monitoring \
--create-namespace

Deploy Log Generator:

kubectl apply -f manifests/app.yaml

Verify Logs:

kubectl logs deployment/log-generator

Output:
Application log generated

## Failure Simulation

Scale Loki Down:

kubectl scale statefulset loki \
-n monitoring \
--replicas=0

Verify:

kubectl get pods -n monitoring

Result:
Loki pod terminated.

## Investigation

Check Promtail Logs:

kubectl logs -n monitoring daemonset/loki-promtail --tail=50

Observed:

error sending batch, will retry

Post "http://loki:3100/loki/api/v1/push":
dial tcp 10.100.237.237:3100:
connect: connection refused

## Analysis

Application:
Healthy

Promtail:
Collecting logs successfully

Loki:
Unavailable

Grafana:
Unable to display logs

## Root Cause

Loki service was unavailable.

Promtail attempted to push logs to:
http://loki:3100/loki/api/v1/push

Since Loki was not running, the connection was refused.

Logs never reached Loki and Grafana displayed no logs.

## Failure Point

Promtail → Loki

## Resolution

Scale Loki Back Up:

kubectl scale statefulset loki \
-n monitoring \
--replicas=1

Verify:

kubectl get pods -n monitoring

Output:

loki-0                1/1 Running
loki-promtail-946s2   1/1 Running
loki-promtail-zcd4p   1/1 Running

## Validation

Check Promtail Logs:

kubectl logs -n monitoring daemonset/loki-promtail --since=2m

Result:
No connection refused errors observed.

Logging pipeline restored successfully.

## Result

✓ Incident Reproduced
✓ Root Cause Identified
✓ Failure Point Located
✓ Loki Restored
✓ Log Collection Recovered
✓ Grafana Logging Restored

## Screenshots

screenshots/
├── 01-loki-installed.png
├── 02-log-generator-running.png
├── 03-promtail-error.png
├── 04-loki-down.png
├── 05-root-cause-analysis.png
├── 06-loki-restored.png
├── 07-promtail-recovered.png

Status: COMPLETED
