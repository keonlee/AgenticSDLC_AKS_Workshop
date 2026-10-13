# Lab 0 - Prepare tools, repository, and enterprise permissions

**Goal:** establish the permissions and review boundaries before an agent runs.
**Time:** 30 minutes; enterprise administrators may need advance notice.

## 1. Confirm access

A Copilot account and Azure subscription are the starting assumptions, not a
guarantee of administrator privileges. Ask the facilitator to confirm:

| Capability | Who enables it | Why it matters |
| --- | --- | --- |
| GHEC organization repository creation and write access | Organization owner | Issues, branches, and PRs |
| Copilot cloud/coding agent access under your license and enterprise policy | Copilot administrator | Assign issues to an agent |
| GitHub Actions and approved actions/runners | Actions administrator | Run CI and release workflow |
| GitHub App creation, installation, and deploy keys | Organization owner | Release PRs and private Git access |
| GitHub environments and rulesets | Repository administrator | Approvals and protected `main` |
| Azure resource creation | Subscription/resource administrator | AKS, ACR, and managed identity |
| Azure role assignment rights at the required scopes | Owner or User Access Administrator plus resource rights | Registry and AKS RBAC |
| Regional VM quota and ACR Tasks availability | Azure administrator | Two nodes and remote image builds |

If cloud-agent access is unavailable, the IDE agent fallback in Lab 3 still
teaches the delivery loop. Copilot code review is another separately governed
capability; its review is not a human approval. If Azure permissions are missing,
an administrator must perform Lab 1; do not ask an agent to bypass the controls.

## 2. Install tools through approved channels

Use PowerShell 7 (`pwsh`), Git, GitHub CLI (`gh`), Python 3.13, Azure CLI (`az`),
`kubectl`, and Azure `kubelogin`. Install the Argo CD CLI matching your chosen
server release for the core-mode commands in Lab 2. Docker is optional locally;
GitHub's Linux runner performs container checks and ACR performs release builds.
For the fallback, also install VS Code and GitHub Copilot.

```powershell
$PSVersionTable.PSVersion
git --version
gh --version
python --version
az version
kubectl version --client
kubelogin --version
argocd version --client
```

`kubectl` should be within the supported version skew of your cluster. The CI
render step's kubectl version is pinned independently and never connects to AKS.
Use the official [Azure CLI installation](https://learn.microsoft.com/cli/azure/install-azure-cli),
[AKS tools](https://learn.microsoft.com/azure/aks/learn/quick-kubernetes-deploy-cli),
and [Argo CD CLI installation](https://argo-cd.readthedocs.io/en/stable/cli_installation/)
instructions rather than unreviewed install scripts.

## 3. Create your own organization repository

Create an empty **private** repository in your GHEC organization. Copy this
workshop's starter into it through an approved template/import process. Do not
work in the shared source repository. Enterprise Managed Users may not be able
to fork an external repository; an administrator can import the content instead.

For organizations that permit GitHub's importer, choose **+ > Import repository**,
set the source to `https://github.com/keonlee/QCellSDLCWorkshop`, choose your
organization and a unique destination name, and select **Private**. Import the
published workshop revision containing these labs, not an earlier README-only
revision. If the importer is unavailable or the source requires access, have
the administrator copy the reviewed starter into the empty repository using
the organization's approved process.

Use `main` as the default branch and retain the complete directory structure.
For an ordinary clone of your new repository:

```powershell
gh auth login --hostname github.com
$Owner = "YOUR_ORG"
$Repo = "YOUR_REPO"
$GitHubRepo = "$Owner/$Repo"
gh repo clone $GitHubRepo
Set-Location $Repo
git remote -v
python -m unittest discover -s app -p "test_*.py" -v
python -m unittest discover -s scripts -p "test_*.py" -v
```

Record these non-secret values and keep this PowerShell session open. In a new
terminal, set them again. Do not copy credentials into your terminal transcript.

Image publication is opt-in: the publish job is skipped unless the repository
variable `WORKSHOP_PUBLISH_ENABLED` is exactly `true`. Leave it unset until Lab 4.
As an additional setup guard, disable **Publish image and propose release**:

```powershell
gh workflow disable publish.yml --repo $GitHubRepo
```

CI should pass on the imported starter. A feature branch without an existing
repository should not be used as the import destination.

## 4. Create the release GitHub App

With administrator help, create an organization-owned GitHub App:

1. Give it a unique name, such as `workshop-release-<team>`, and a homepage URL
   pointing at the workshop repository.
2. Disable webhook delivery; this lab does not use incoming webhooks.
3. Grant repository **Contents: Read and write** and
   **Pull requests: Read and write**. Metadata read is implicit. Do not grant
   administration, workflows, organization, or deployment access.
4. Install the App on **only your workshop repository**.
5. Record its numeric App ID. Generate a private key and store the downloaded
   PEM through the repository/environment secret UI, never in Git or an issue.
   Keep the downloaded key outside the repository in an approved secure location.
6. Set the repository variable `RELEASE_APP_ID` and the repository secret
   `RELEASE_APP_PRIVATE_KEY`. An environment-scoped secret in `dev` is also valid.

The workflow exchanges this key for a short-lived, repository-scoped installation
token. Unlike PRs opened with the default `GITHUB_TOKEN`, App-authored PRs can
trigger subsequent PR workflows. This avoids a release PR that waits forever for
required CI. Do not replace the App token with a broad personal access token.

See [App installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)
and [workflow trigger limitations](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow).

## 5. Configure the review gates

Create a repository ruleset targeting `main`:

1. Require a pull request and at least one human approval.
2. Require the CI `test` status check once an initial CI run has registered it.
   Select the actual check shown by GitHub, rather than guessing its name.
3. Require resolution of review conversations and an up-to-date branch.
4. Block force pushes and branch deletion. Do not give the release App a bypass.
5. Arrange a second learner or facilitator as reviewer. A solo learner cannot
   approve their own PR; use a reviewer rather than pretending self-review meets
   the gate.

Create the **`dev`** GitHub environment. Restrict deployment branches to `main`,
and configure a required reviewer if your enterprise policy permits it. The
environment gate approves **image publication**, not AKS deployment. The separate
release PR approval authorizes the desired state Argo CD will apply.

The examples use major-version action tags for readability. If enterprise policy
requires immutable action pins, have an administrator resolve approved full
commit SHAs for every `uses:` reference before importing/running the workflows.

**Checkpoint:** starter CI passes; `main` is protected; the release App is scoped
to one repository; `dev` exists; publication remains opted out and disabled until
Azure setup is ready.

**Next:** [Lab 1](01-azure-foundation.md).
