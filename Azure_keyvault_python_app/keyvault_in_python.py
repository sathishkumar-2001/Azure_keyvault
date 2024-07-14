from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Define your Key Vault and secret names
key_vault_name = "<YourKeyVaultName>"
secret_name = "<YourSecretName>"

# Create the Key Vault URL
key_vault_url = f"https://{key_vault_name}.vault.azure.net/"

# Authenticate to Azure and create a SecretClient
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve the secret
retrieved_secret = client.get_secret(secret_name)

# Print the secret value
print(f"The value of the secret '{secret_name}' is: {retrieved_secret.value}")
