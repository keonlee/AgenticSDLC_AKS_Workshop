# Troubleshooting by checkpoint

Stop at the first failing checkpoint. Keep secrets out of logs and issue comments.

| Symptom | Likely cause | Safe next step |
| --- | --- | --- |
| Copilot cannot be assigned to an issue | License, organization policy, repository eligibility, or UI changes | Ask the Copilot administrator; use the Lab 3 IDE fallback |
| Agent PR checks need approval | GitHub's trusted-run gate for agent/first-time contributions | Inspect diff, then let an authorized human approve the run |
| Required `test` stays Expected | Wrong ruleset check name or App/token workflow trigger behavior | Pick a check from an actual CI run; confirm release PR uses the App token |
| Can't approve a PR | Author cannot approve their own PR | Ask the assigned second learner/facilitator |
| Publish job is skipped | `WORKSHOP_PUBLISH_ENABLED` is unset or not `true` | Keep it unset during setup; opt in only after completing Lab 4 configuration checks |
| Publish waits on `dev` | Environment reviewer approval pending | Authorized reviewer inspects and approves publication |
| Azure Login reports no matching federated identity | Owner/repo/environment mismatch, wrong tenant/client | Match `repo:OWNER/REPO:environment:dev`; check branch restriction and variables |
| Azure Login cannot obtain OIDC token | Missing `id-token: write` or policy | Inspect the trusted publish job; never add OIDC to PR CI as a fix |
| ACR build forbidden | Wrong identity/scope or RBAC propagation | Verify registry-scoped role assignment and wait; do not grant subscription Owner |
| ACR Tasks unavailable | Subscription/region support or policy limitation | Ask Azure administrator for an approved supported region/build method |
| Release App token or PR creation fails | Wrong App ID/key, missing installation, or permission | Verify App installation only on this repo and Contents/PR write grants |
| Publish says `main advanced` | Source/setup/release commit merged during build | Dispatch publish on current `main`; close stale proposals |
| AKS create fails | VM quota/SKU/region limits or unregistered providers | Administrator checks quota/providers; do not expand cloud privileges |
| kubectl times out | Authorized IP changed with VPN/egress, wrong context | Confirm approved egress CIDR and context; administrator updates the allowed range |
| kubectl returns Forbidden | Entra/RBAC role or token propagation | Verify Cluster Admin lab role; refresh login; do not use admin certificates |
| Argo repository connection fails | SSH URL/key/host keys, deploy key disabled, or outbound access | Compare project/app/secret URLs, inspect repo-server logs, verify published host fingerprints |
| Argo Application doesn't exist | Deliberately deferred until real image promotion | Complete Lab 4, then apply the customized Application once |
| ImagePullBackOff at first sync | Placeholder remained, incorrect digest, or missing kubelet pull role | Inspect Deployment image and pod events; verify ACR RBAC mode and pull integration |
| Argo Synced but Degraded | Admission denial, failed probes, image pull, or insufficient node resources | Inspect pod events/logs; fix desired state through a PR |
| Argo remains OutOfSync | Poll interval, source error, or project destination/resource restriction | Request hard refresh, inspect Application conditions, preserve namespace restrictions |
| `/version` differs from Argo revision | Comparing source build SHA with GitOps merge SHA | Compare with publish run's source SHA instead |
| HTTP greeting still 404 | Wrong/old digest or feature not implemented | Verify source PR, artifact digest, deployed reference, and tests |
| Local port-forward stops | Pod replaced during rollout | Restart the port-forward after rollout is healthy |
| Rollback causes image pull failure | Reverted first placeholder or deleted old artifact | Promote a retained known-good digest through a reviewed PR |

Useful read-only diagnostics:

```powershell
kubectl config current-context
kubectl get events -n workshop-dev --sort-by=.lastTimestamp
kubectl describe pods -n workshop-dev -l app=workshop-app
kubectl logs -n workshop-dev -l app=workshop-app --tail=100
kubectl logs -n argocd deployment/argocd-repo-server --tail=100
kubectl get application workshop-app -n argocd -o yaml
argocd app get workshop-app --hard-refresh
```

Review/redact diagnostic output before sharing it. Do not post Kubernetes
Secrets, tokens, PEM files, kubeconfig, or full environment dumps.
