#!/bin/bash

# Script to generate Kubernetes secrets for Photo Studio CRM
# This script generates a secrets file with random secure values

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to generate random passwords
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-20
}

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    print_error "openssl is not installed. Please install openssl first."
    exit 1
fi

# Generate secure random values
print_status "Generating secure random values..."

POSTGRES_PASSWORD=$(generate_password)
REDIS_PASSWORD=$(generate_password)
SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
JWT_SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
GRAFANA_PASSWORD=$(generate_password)

# Create secrets file
print_status "Creating secrets file..."

cat > kubernetes/phstudio-secrets.yml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: phstudio-secrets
  namespace: phstudio
type: Opaque
data:
  # Base64 encoded values
  postgres_password: $(echo -n "$POSTGRES_PASSWORD" | base64)
  redis_password: $(echo -n "$REDIS_PASSWORD" | base64)
  secret_key: $(echo -n "$SECRET_KEY" | base64)
  jwt_secret_key: $(echo -n "$JWT_SECRET_KEY" | base64)
  grafana_password: $(echo -n "$GRAFANA_PASSWORD" | base64)
EOF

print_status "Secrets file created: kubernetes/phstudio-secrets.yml"

# Show generated values (for reference only - DO NOT COMMIT)
print_warning "Generated values (DO NOT COMMIT THESE TO VERSION CONTROL):"
echo "  POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "  REDIS_PASSWORD: $REDIS_PASSWORD"
echo "  SECRET_KEY: $SECRET_KEY"
echo "  JWT_SECRET_KEY: $JWT_SECRET_KEY"
echo "  GRAFANA_PASSWORD: $GRAFANA_PASSWORD"

print_status "Secrets generation completed!"
print_warning "IMPORTANT: Store these values securely and never commit them to version control!"