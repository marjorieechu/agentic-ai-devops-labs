# Terraform IaC Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### YAML-Based Configuration Pattern

| Skill | Why It Matters |
|-------|---------------|
| `yamldecode()` for variables | Human-readable config, no .tfvars needed |
| Environment separation | dev/staging/prod configs in separate YAML files |
| Config vs code separation | Non-Terraform users can modify configs |

```hcl
locals {
  env = yamldecode(file("${path.module}/../../environments/dev.yaml"))
}

module "vpc" {
  source = "../../modules/vpc"
  config = local.env.vpc
  tags   = local.env.tags
}
```

### Modular Terraform

| Module | Purpose | Why Modular |
|--------|---------|-------------|
| VPC | Network infrastructure | Reuse across environments |
| EKS | Kubernetes cluster | Consistent cluster config |
| RDS | PostgreSQL database | Standardized DB setup |

**Module Pattern:**
```
terraform/
├── environments/     # YAML configs
├── modules/          # Reusable modules
│   ├── vpc/
│   ├── eks/
│   └── rds/
└── resources/        # Environment deployments
    ├── dev/
    ├── staging/
    └── prod/
```

### AWS Resources Created

| Resource | Configuration |
|----------|--------------|
| VPC | Public/private subnets, NAT Gateway |
| EKS | Managed node groups, addons (CoreDNS, VPC-CNI) |
| RDS | PostgreSQL, encrypted, password in Secrets Manager |

### Security Best Practices

| Practice | Implementation |
|----------|---------------|
| No hardcoded passwords | `random_password` + Secrets Manager |
| Encrypted storage | `storage_encrypted = true` on RDS |
| Private subnets | EKS/RDS in private subnets only |
| Least privilege | Security groups restrict by VPC CIDR |

### Remote State

```hcl
backend "s3" {
  bucket         = "dev-titanic-api-tf-state"
  key            = "dev/terraform.tfstate"
  region         = "us-east-1"
  encrypt        = true
  dynamodb_table = "dev-titanic-api-tf-lock"
}
```

**Why Remote State?**
- Team collaboration
- State locking prevents concurrent modifications
- Encrypted at rest in S3

### Environment Scaling

| Resource | Dev | Prod |
|----------|-----|------|
| EKS Nodes | 1-3 t3.medium | 3-10 t3.large |
| RDS | db.t3.micro | db.t3.medium, Multi-AZ |
| NAT Gateway | Single | Per-AZ |
| Deletion Protection | No | Yes |

### Separate Pipelines: Infrastructure vs Application

| Pipeline | Trigger | Purpose |
|----------|---------|---------|
| **App CI/CD** | Push to main/develop | Build, test, deploy app to K8s |
| **Infra CI/CD** | Push to `terraform/**` | Provision/update AWS resources |

**Why Separate?**
- Infrastructure changes less frequently than app code
- Different permissions needed (AWS vs K8s)
- Stricter approval gates for infra (destroying resources is dangerous)
- Different blast radius - infra failure affects everything

**Terraform Pipeline Flow:**
```
PR (terraform/** changes)
    │
    ▼
Format + Validate → Checkov Scan → Plan (comments on PR)
    │
    ▼ (merge to main)
Apply Dev (auto) → Apply Staging (approval) → Apply Prod (approval)
```

**Key Patterns:**
- Plan on PR, Apply on merge
- Auto-apply dev, require approval for staging/prod
- Use OIDC for AWS auth (no static credentials)
- Save plan artifact, apply exact plan

## Commands Learned

```bash
# Initialize and plan
terraform init
terraform plan

# Apply with auto-approve (CI/CD only)
terraform apply -auto-approve

# Destroy (careful!)
terraform destroy

# Format check
terraform fmt -check -recursive

# Validate
terraform validate
```
