# Allow services to read their specific secrets
path "secret/data/devsecops-tp/user-service/*" {
  capabilities = ["read"]
}

path "secret/data/devsecops-tp/product-service/*" {
  capabilities = ["read"]
}

# Deny all other paths
path "secret/*" {
  capabilities = ["deny"]
}
