# Lab 5 - Verify the workload, capture evidence, and practice rollback

**Goal:** prove the approved feature is running, not just that a pipeline passed.
**Time:** 25 minutes.

## 1. Check desired and actual state

```powershell
argocd app get workshop-app
kubectl rollout status deployment/workshop-app -n workshop-dev --timeout=180s
kubectl get pods -n workshop-dev -l app=workshop-app
kubectl get deployment workshop-app -n workshop-dev -o jsonpath='{.spec.template.spec.containers[0].image}'
kubectl get pods -n workshop-dev -l app=workshop-app -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.status.containerStatuses[0].imageID}{"\n"}{end}'
```

The Deployment image should match the release PR's ACR digest. Container
`imageID` formatting can vary by runtime and image platform, so also verify the
Deployment reference and the application version. Two replicas should be Ready.

## 2. Exercise the acceptance criteria

In a dedicated terminal:

```powershell
kubectl port-forward -n workshop-dev svc/workshop-app 8080:80
```

Keep it open. In a second terminal:

```powershell
Invoke-RestMethod http://localhost:8080/healthz
Invoke-RestMethod http://localhost:8080/version
Invoke-RestMethod http://localhost:8080/api/greeting
Invoke-RestMethod "http://localhost:8080/api/greeting?name=QCell"
Invoke-RestMethod "http://localhost:8080/api/greeting?name=%20Ada%20"
$Bad = Invoke-WebRequest "http://localhost:8080/api/greeting?name=" -SkipHttpErrorCheck
$Bad.StatusCode
$Bad.Content
```

Expect `ok`, the **source build SHA**, `Hello, workshop!`, `Hello, QCell!`,
`Hello, Ada!`, and then HTTP 400 with `{"error":"invalid name"}`. The source SHA
is not the later release PR merge SHA that Argo CD reports as its Git revision.
Use PowerShell 7 for `-SkipHttpErrorCheck`.

The agent's tests must also verify duplicate names and the 40/41-character
boundary. Read those tests and repeat any acceptance check that remains unclear.
Do not mark the workshop complete based on Synced alone; Synced does not prove
business behavior, and Healthy does not prove every endpoint.

## 3. Add evidence to the original issue

Add a comment with this structure, using actual links and values:

```text
Implementation PR:
Agent session (or IDE fallback used):
CI run:
Source build SHA:
Publish run:
ACR image digest:
Release PR:
Argo CD Git revision and Synced/Healthy result:
Observed /version and greeting responses:
Reviewer:
```

Do not include credentials, local kubeconfig, or sensitive Azure identifiers.
Close/reconcile the issue if it did not auto-close. This links intent, proposed
code, approvals, artifact, desired state, and runtime behavior.

## 4. Observe reconciliation safely

Read `selfHeal: true` in the Application and explain what would happen if a
person changed the managed Deployment out of band. Argo CD would restore Git's
desired state; the next sync is not an independent code review.

An optional facilitator-led drift demo can scale the **lab** Deployment to one
replica, then observe it returning to two. Only do this after confirming the
context/namespace and getting approval for the temporary workload change:

```powershell
kubectl scale deployment/workshop-app -n workshop-dev --replicas=1
argocd app get workshop-app --hard-refresh
kubectl get deployment workshop-app -n workshop-dev --watch
```

Stop the watch with Ctrl+C. Do not edit production workloads for this exercise.

## 5. Create a second valid release before rollback

The first release replaced an **invalid placeholder**. Reverting it would cause
ImagePullBackOff, not a useful rollback. Instead:

1. Create another issue asking Copilot to change the `/` message to
   `Agentic SDLC workshop - release 2` and update its tests, preserving all APIs.
2. Repeat app PR review/merge, publication approval, release PR review/merge, and
   runtime verification. Stop/restart port-forward if its pod is replaced.
3. Record the original and second **valid** image digests.

## 6. Roll back through a reviewed Git change

Use GitHub's **Revert** action on the **second release PR**, then review and merge
the resulting PR. If GitHub cannot construct the revert (for example, merge
strategy/conflicts), create a branch from current `main` and restore only the
overlay's previous known-good `newName`/`digest`, then open a normal PR.

Do **not** revert the app implementation PR for this exercise and do not run
`kubectl rollout undo`: both miss the intended GitOps image-promotion rollback.

After the revert merges:

```powershell
argocd app get workshop-app --hard-refresh
argocd app wait workshop-app --sync --health --timeout 300
kubectl rollout status deployment/workshop-app -n workshop-dev --timeout=180s
```

Restart port-forward and check `/`, `/version`, and `/api/greeting`. The version
should return to the first valid release's build SHA, and the greeting feature
should still work. ACR must retain that image; do not delete old images before
the rollback window ends.

This is a rollback of runtime desired state. The second application's source
change remains in `main`; a future build of that source will include it unless
you also correct/revert the source through an application PR. Do not manually
dispatch publish immediately after rollback unless you intend to promote it again.

**Checkpoint:** actual HTTP acceptance criteria verified; issue evidence complete;
second valid release reverted to the first through Git and reconciled by Argo CD.

**References:** [Automated sync](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/),
[Reverting a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/reverting-a-pull-request).

**Next:** [Lab 6](06-cleanup.md).
