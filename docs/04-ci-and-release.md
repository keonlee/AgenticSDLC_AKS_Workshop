# Lab 4 - Build an image and promote it through GitOps

**Goal:** make the release traceable without giving CI cluster access.
**Time:** 30 minutes.

## 1. Read the workflow boundaries

| Workflow | Trigger | Credentials | Result |
| --- | --- | --- | --- |
| `ci.yml` | Every PR; pushes to `main` | Read-only GitHub token, no Azure login | App/tool tests, Kustomize render, container build/smoke |
| `publish.yml` | App/build changes merged to `main`; manual dispatch on `main` | Azure OIDC plus short-lived release App token | ACR image and a digest promotion PR |
| Argo CD controller | Polls desired state in `main` | Read-only Git credential and in-cluster controller identity | Reconciles the `workshop-dev` workload |

CI runs on **all** PRs, including deployment-only changes, so protected release
PRs get a status check. CI renders YAML but does not perform a live Kubernetes
API/admission check. The release repeats tests before building; it does not
depend on a race between separate CI and publish workflow runs.

## 2. Enable and run the first publication

Confirm `dev` has the branch restriction and reviewer, all five repository
variables are present (`AZURE_*`, `ACR_NAME`, `RELEASE_APP_ID`), and the App key
secret exists. Opt in to publication only after these checks, then:

```powershell
gh variable set WORKSHOP_PUBLISH_ENABLED --body true --repo $GitHubRepo
gh workflow enable publish.yml --repo $GitHubRepo
gh workflow run publish.yml --ref main --repo $GitHubRepo
gh run list --workflow publish.yml --limit 5 --repo $GitHubRepo
```

Open the newest run in GitHub Actions. If it is waiting on `dev`, have the
authorized reviewer approve it. Open Azure Login, ACR build, and release PR
steps. Do not paste tokens or key material into screenshots.

If the publish job is skipped, verify the explicit opt-in variable is `true`.
It is intentionally unset in the shared workshop source repository so publishing
the teaching content itself does not attempt an Azure release.

The first run may need time for Azure RBAC propagation. Fix a failed step rather
than granting subscription Owner or adding a client secret.

## 3. Inspect the immutable artifact

`az acr build` uploads the build context and builds in ACR; it does not require a
Docker daemon on the release runner. The source commit SHA is the image tag and
the `/version` build argument. The workflow queries the resulting digest and
records the image reference in the run summary.

```powershell
az acr repository show-tags --name $AcrName --repository workshop-app -o table
# Set this to the source SHA shown in the publish run/release PR, not a later GitOps commit.
$SourceSha = "SOURCE_COMMIT_SHA"
az acr repository show --name $AcrName --image "workshop-app:$SourceSha" --query "{digest:digest,name:name}" -o table
```

A tag alone is not immutable. The deployment uses
`<registry>.azurecr.io/workshop-app@sha256:<digest>`.
The workshop's floating Python base image is another production-hardening
discussion: pin a reviewed base digest and update it through a controlled process.

## 4. Review and merge the release PR

Open the PR linked in the publish summary. It should change only
`deploy\overlays\dev\kustomization.yaml`, setting `newName` and `digest`.

Have the reviewer confirm the image digest, source SHA, successful build, app
PR/issue linkage, and CI result. Use the normal reviewed merge. The release App
has no ruleset bypass and does not auto-merge.

Only the latest intended release should remain eligible to merge. Close obsolete
unmerged release PRs. Branch freshness alone cannot prove that an old image is
the intended release. The workflow refuses to propose a build if `main` advanced
during that build; rerun from the latest `main` if this guard fires.

The digest-only merge does **not** match the publish workflow's path filter, so
it does not create an endless image/PR loop. Every later app merge does publish
again. A manual rerun can create another proposal if the desired digest differs;
review and close redundant proposals.

## 5. Bootstrap the Application once

Now that the real digest has merged, update your local `main` and inspect the
rendered manifests:

```powershell
git switch main
git pull --ff-only
kubectl kustomize deploy\overlays\dev
kubectl apply --dry-run=server -k deploy\overlays\dev
kubectl apply -f argocd\application.yaml
argocd app get workshop-app --hard-refresh
argocd app wait workshop-app --sync --health --timeout 300
```

The dry run invokes admission without persisting app resources. Only the Argo
Application is applied by the administrator; the controller deploys the workload.
Subsequent app releases require **no manual workload apply**. Argo CD polls Git
(normally on the order of minutes); `--hard-refresh` requests an immediate
refresh for the lab, not a separate deployment authority.

In `argocd\application.yaml`, automated sync deploys approved Git,
`selfHeal` repairs drift, and `prune` deletes managed resources removed from Git.
Review those deletion consequences before using the pattern in a real system.
The bootstrap Application/Project are administrator-managed in this baseline;
editing their YAML in Git alone does not automatically reapply those two CRs.

**Checkpoint:** image exists by digest; release PR approved and merged;
Application is Synced/Healthy; no Azure/AKS credentials were supplied to PR code.

**Next:** [Lab 5](05-verify-and-rollback.md).
