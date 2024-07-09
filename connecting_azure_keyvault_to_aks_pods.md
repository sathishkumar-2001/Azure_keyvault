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

# Deploy a Pod That Uses the Secrets from the Key Vault

apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-keyvault
spec:
  provider: azure
  secretObjects:
  - secretName: kv-secrets
    type: Opaque
    data:
    - objectName: <YourSecretName>
      key: secret-key
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: <YourManagedIdentityClientId>
    keyvaultName: <YourKeyVaultName>
    objects: |
      array:
        - |
          objectName: <YourSecretName>
          objectType: secret
    tenantId: <YourTenantId>


kubectl apply -f secret-provider-class.yaml


# Create a pod that mounts the secrets:

apiVersion: v1
kind: Pod
metadata:
  name: keyvault-secrets-pod
spec:
  containers:
  - name: busybox
    image: busybox
    command: [ "/bin/sh", "-c", "sleep 3600" ]
    volumeMounts:
    - name: secrets-store-inline
      mountPath: "/mnt/secrets-store"
      readOnly: true
  volumes:
  - name: secrets-store-inline
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "azure-keyvault"


kubectl apply -f pod-with-secrets.yaml

# print the secret in the pod
kubectl exec -it keyvault-secrets-pod -- cat /mnt/secrets-store/<YourSecretName>



