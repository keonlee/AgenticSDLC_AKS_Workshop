# Lab 1 - Provision AKS, ACR, and federated CI identity

**Goal:** create an isolated development cluster and a secretless Azure login for
GitHub Actions. **Time:** 35 minutes.

These commands create billable resources and role assignments. Run them only
after your administrator approves the subscription, region, and resource scope.
No Azure resources are provisioned by reading this guide.

## 1. Choose the lab configuration

| Decision | Workshop choice | Rationale and tradeoff |
| --- | --- | --- |
| Cluster type | AKS Standard, Free control-plane tier | Fixed two-node exercise; no production API SLA |
| Nodes | Two `Standard_D4s_v5`, Azure Linux | Capacity for Argo CD and two small app replicas; billable even when idle |
| Pod networking | Azure CNI Overlay with Cilium | Explicit non-VNet-routable pod model and network-policy-capable dataplane |
| API access | Public endpoint restricted to administrator egress CIDR | Learner access without a private network; GitHub runners never access it |
| Application access | ClusterIP plus localhost port-forward | No public ingress, DNS, or TLS setup in the baseline |
| Identity | Entra AKS authentication, Azure RBAC, local accounts disabled | No shared cluster-admin certificate |
| Registry | ACR Basic, classic RBAC mode | Supports the lab's `AcrPull` integration |
| Upgrades | Patch auto-upgrade | Suitable for a disposable lab, not a production maintenance plan |

For production, assess AKS Automatic first. This lab deliberately uses Standard
to teach a repeatable fixed node pool and explicit Day-0 decisions. Private API
access, VNet/pod address ranges, and egress design must be planned before cluster
creation. Check the region/SKU and quota; do not change an enterprise network
design merely to make the lab run.

## 2. Set variables and confirm the Azure context

Run from the repository root in the PowerShell session from Lab 0:

```powershell
az login
az account list --query "[].{Name:name,IsDefault:isDefault}" -o table
az account set --subscription "YOUR_APPROVED_SUBSCRIPTION_NAME"
az account show --query "{Name:name,State:state}" -o table

$Location = "eastus"
$Suffix = Get-Random -Minimum 100000 -Maximum 999999
$ResourceGroup = "rg-agentic-sdlc-$Suffix"
$AksName = "aks-agentic-sdlc-$Suffix"
$AcrName = "acrsdlc$Suffix"
$IdentityName = "id-github-build-$Suffix"
$AdminCidr = "YOUR_APPROVED_PUBLIC_EGRESS_IP/32"
$SubscriptionId = az account show --query id -o tsv
$TenantId = az account show --query tenantId -o tsv
$AdminObjectId = az ad signed-in-user show --query id -o tsv
```

Replace the subscription name and CIDR before continuing. Use your current
corporate/VPN public egress address, not your workstation's private LAN IP. If
directory reads are restricted, an administrator must resolve the Entra object
ID. Record resource names privately; do not publish subscription identifiers.

## 3. Create and connect the resources

```powershell
az group create --name $ResourceGroup --location $Location
az acr create --resource-group $ResourceGroup --name $AcrName --sku Basic --role-assignment-mode rbac --admin-enabled false
$AcrId = az acr show --name $AcrName --query id -o tsv

az aks create --resource-group $ResourceGroup --name $AksName --location $Location --tier free --node-count 2 --node-vm-size Standard_D4s_v5 --os-sku AzureLinux --network-plugin azure --network-plugin-mode overlay --network-dataplane cilium --enable-managed-identity --enable-aad --enable-azure-rbac --disable-local-accounts --api-server-authorized-ip-ranges $AdminCidr --auto-upgrade-channel patch --attach-acr $AcrId --generate-ssh-keys

$AksId = az aks show --resource-group $ResourceGroup --name $AksName --query id -o tsv
az role assignment create --assignee-object-id $AdminObjectId --assignee-principal-type User --role "Azure Kubernetes Service RBAC Cluster Admin" --scope $AksId
az aks get-credentials --resource-group $ResourceGroup --name $AksName
kubelogin convert-kubeconfig -l azurecli
kubectl config current-context
kubectl get nodes
```

Azure CLI native command failures are not automatically terminating errors in
all PowerShell versions. Stop at any failed command, fix it, and rerun only the
failed step. Role propagation can take several minutes. Do not use
`get-credentials --admin` as an authentication workaround.

The cluster admin role is intentionally powerful for **one lab administrator**
who installs Argo CD. It is not assigned to GitHub Actions. `--attach-acr` assigns
registry pull rights to the kubelet identity, not the workload or CI identity.
An existing ABAC-enabled registry needs repository-specific roles instead; do
not use `--attach-acr` with it.

## 4. Create the GitHub Actions managed identity

```powershell
az identity create --resource-group $ResourceGroup --name $IdentityName
$ClientId = az identity show --resource-group $ResourceGroup --name $IdentityName --query clientId -o tsv
$PrincipalId = az identity show --resource-group $ResourceGroup --name $IdentityName --query principalId -o tsv

az role assignment create --assignee-object-id $PrincipalId --assignee-principal-type ServicePrincipal --role Contributor --scope $AcrId

az identity federated-credential create --resource-group $ResourceGroup --identity-name $IdentityName --name github-dev --issuer "https://token.actions.githubusercontent.com" --subject "repo:${Owner}/${Repo}:environment:dev" --audiences "api://AzureADTokenExchange"
```

**Why Contributor here?** The release uses `az acr build`, which creates an ACR
quick task as well as publishing an image. `AcrPush` alone is not the complete
permission for managing these builds. Registry-scoped Contributor is a workshop
simplification, **not** subscription-wide access or a production least-privilege
claim. It permits registry management/deletion. Before production, replace it
with verified task/build and repository permissions for your registry mode.

There is no client secret. The federated subject must exactly match the
repository's owner/name and environment. Because the job uses `environment:
dev`, its OIDC subject is environment-based, not `ref:refs/heads/main`. The
environment's branch restriction supplies that second boundary.

## 5. Configure GitHub variables

```powershell
gh variable set AZURE_CLIENT_ID --body $ClientId --repo $GitHubRepo
gh variable set AZURE_TENANT_ID --body $TenantId --repo $GitHubRepo
gh variable set AZURE_SUBSCRIPTION_ID --body $SubscriptionId --repo $GitHubRepo
gh variable set ACR_NAME --body $AcrName --repo $GitHubRepo
```

These identifiers are configuration, not passwords. The App private key remains
an encrypted secret from Lab 0. No Azure credentials belong in the Copilot agent
environment or a PR workflow. Keep ACR publicly reachable for this baseline;
private endpoints require appropriately networked build runners and tasks.

**Checkpoint:** two Ready nodes; ACR admin account disabled; kubelet pull access
exists; CI identity has only registry-scoped Azure access; GitHub variables are set.

**References:** [AKS CLI quickstart](https://learn.microsoft.com/azure/aks/learn/quick-kubernetes-deploy-cli),
[AKS Azure RBAC](https://learn.microsoft.com/azure/aks/manage-azure-rbac),
[AKS/ACR integration](https://learn.microsoft.com/azure/aks/cluster-container-registry-integration),
[GitHub-to-Azure OIDC](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect).

**Next:** [Lab 2](02-argocd.md).
