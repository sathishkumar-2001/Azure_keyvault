# Create Azure Resource Group
az group create --name keyvault-demo --location westus
# create AKS 
az aks create --name keyvault-demo-cluster -g keyvault-demo --node-count 1 --enable-addons azure-keyvault-secrets-provider --enable-oidc-issuer --enable-workload-identity
# Get csi pods are running
kubectl get pods -n kube-system -l 'app in (secrets-store-csi-driver,secrets-store-provider-azure)' -o wide
# Create keyvault
az keyvault create --name <YourKeyVaultName> --resource-group <YourResourceGroupName> --location <YourLocation>
az keyvault secret set --vault-name <YourKeyVaultName> --name <YourSecretName> --value <YourSecretValue>

# create identity for keyvault
az identity create --name <YourManagedIdentityName> --resource-group <YourResourceGroupName> --location <YourLocation>

# set policy for keyvault
az keyvault set-policy --name <YourKeyVaultName> --resource-group <YourResourceGroupName> --object-id <YourManagedIdentityObjectId> --secret-permissions get


# Add the Azure Key Vault Provider for Secrets Store CSI Driver Helm repository
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts

# Install the Secrets Store CSI Driver
helm install csi-secrets-store secrets-store-csi-driver/secrets-store-csi-driver --namespace kube-system

# Install the Azure Key Vault provider
helm repo add csi-secrets-store-provider-azure https://azure.github.io/secrets-store-csi-driver-provider-azure/charts
helm install csi-secrets-store-provider-azure csi-secrets-store-provider-azure/csi-secrets-store-provider-azure --namespace kube-system



