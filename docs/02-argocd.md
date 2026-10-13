# Lab 2 - Bootstrap Argo CD with read-only Git access

**Goal:** install the GitOps controller without exposing its API publicly.
**Time:** 25 minutes.

## 1. Install a reviewed release

Confirm `kubectl config current-context` points to the disposable workshop AKS
cluster. Resolve a release tag, have the facilitator review/approve it, and
record that exact tag for the class. Do not apply a moving `stable` URL.

```powershell
$ArgoVersion = gh api repos/argoproj/argo-cd/releases/latest --jq .tag_name
$ArgoVersion
# Stop here until the facilitator approves this release.
kubectl create namespace argocd
kubectl apply --server-side -n argocd -f "https://raw.githubusercontent.com/argoproj/argo-cd/$ArgoVersion/manifests/install.yaml"
kubectl rollout status deployment/argocd-server -n argocd --timeout=300s
kubectl rollout status deployment/argocd-repo-server -n argocd --timeout=300s
kubectl rollout status statefulset/argocd-application-controller -n argocd --timeout=300s
kubectl get pods -n argocd
```

This upstream installation creates cluster-wide controller RBAC. The project
below limits what this Application can deploy, but does not make the controller
itself a namespace-scoped least-privilege installation. Isolate it in the lab
cluster. For an existing installation, follow its approved upgrade process;
do not resolve server-side conflicts by blindly taking field ownership.

## 2. Create the application namespace

```powershell
kubectl create namespace workshop-dev
kubectl label namespace workshop-dev pod-security.kubernetes.io/enforce=restricted
```

The namespace is managed by the administrator. The Application does not create
it, and the AppProject does not allow cluster-scoped workload resources.

## 3. Configure private repository access

Create a **read-only deploy key**, separate from the release GitHub App:

```powershell
New-Item -ItemType Directory -Force .local | Out-Null
ssh-keygen -t ed25519 -C "argocd-workshop-readonly" -f .local\argocd_repo
```

For this disposable, non-interactive repo-server key, leave the passphrase empty.
Protect the local file and use an enterprise-approved secret manager for
persistent environments. In your workshop repository, open **Settings > Deploy
keys > Add deploy key**, paste the `.local\argocd_repo.pub` public key, and leave
**Allow write access unchecked**. Do not upload the private key to GitHub.

```powershell
$RepoSsh = "git@github.com:${Owner}/${Repo}.git"
kubectl create secret generic workshop-repo -n argocd --from-literal=type=git --from-literal=url=$RepoSsh --from-file=sshPrivateKey=.local\argocd_repo
kubectl label secret workshop-repo -n argocd argocd.argoproj.io/secret-type=repository
```

Argo CD's installation includes a known-hosts configuration for common Git
providers. Verify the `github.com` host keys against GitHub's published
fingerprints under your enterprise policy. Do not disable SSH host verification.
If deploy keys are prohibited, ask the administrator to configure an approved
read-only GitHub App repository credential using Argo CD's private-repository
documentation. Do not reuse the workflow's write-enabled App as a shortcut.

## 4. Customize and review the Argo templates

Create an ordinary branch:

```powershell
git switch -c setup/argocd-repository
```

In `argocd\project.yaml` and `argocd\application.yaml`, replace
`git@github.com:YOUR_ORG/YOUR_REPO.git` with `$RepoSsh`. The two URLs must match
each other and the repository secret. Keep `targetRevision: main`, the
`deploy/overlays/dev` path, and the namespace destination unchanged.

```powershell
git add argocd
git commit -m "configure: point Argo CD at workshop repository"
git push -u origin setup/argocd-repository
gh pr create --base main --title "Configure workshop Argo CD repository" --body "Configure the read-only Git source and namespace-scoped Application."
```

Have the reviewer approve and merge the setup PR. Then update your clone:

```powershell
git switch main
git pull --ff-only
kubectl apply -f argocd\project.yaml
```

**Do not apply `argocd\application.yaml` yet.** The dev overlay still contains
`registry.invalid` and a placeholder digest. Creating the Application now would
try to deploy an image that cannot be pulled. Lab 4 applies it after a real image
promotion is merged.

## 5. Use Argo CD core mode

Match the installed Argo CD CLI version to the approved server release:

```powershell
kubectl config set-context --current --namespace=argocd
argocd login --core
argocd repo list
```

Core mode uses your authenticated Kubernetes context, avoids an Argo admin
password and self-signed browser certificate, and needs no public service.
`repo list` should show a successful connection. If it does not, resolve the
credential/host-key/network issue before continuing. Application health will be
checked after bootstrap in Lab 4.

**Checkpoint:** controller pods Ready; read-only repository connection successful;
customized project applied; no Application attempting to run the placeholder.

**References:** [Argo CD getting started](https://argo-cd.readthedocs.io/en/stable/getting_started/),
[private repository authentication](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/),
[GitHub SSH fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints),
[AppProject restrictions](https://argo-cd.readthedocs.io/en/stable/user-guide/projects/).

**Next:** [Lab 3](03-issue-to-pr.md).
