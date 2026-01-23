# Security & Compliance Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### Defense in Depth

| Layer | Controls |
|-------|----------|
| CI/CD | Gitleaks, Checkov, SonarCloud, Trivy |
| Container | Non-root, read-only FS, minimal image |
| Kubernetes | Network Policy, Security Context, RBAC |
| Infrastructure | Private subnets, encrypted storage, Secrets Manager |

### Container Security

```yaml
# Dockerfile
USER appuser  # Non-root

# Kubernetes
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

**Why Each Setting:**
| Setting | Protection Against |
|---------|-------------------|
| `runAsNonRoot` | Container escape with root |
| `readOnlyRootFilesystem` | Malware writing to disk |
| `allowPrivilegeEscalation: false` | Privilege escalation attacks |
| `capabilities.drop: ALL` | Kernel exploits |

### Secret Management

| Secret | Where to Store | Never Store In |
|--------|---------------|----------------|
| DB Password | AWS Secrets Manager | Code, Git, ConfigMap |
| API Keys | K8s Secrets (encrypted) | Environment files in Git |
| AWS Creds | OIDC Federation | Static access keys |

**AWS OIDC Pattern (no static keys):**
```yaml
- name: Configure AWS Credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
```

### Shift-Left Security

| Stage | Tool | Blocks Pipeline If |
|-------|------|-------------------|
| 1 | Gitleaks | Secrets in code |
| 2 | Checkov | IaC misconfigs |
| 3 | SonarCloud | Quality gate fails |
| 4 | Trivy | CRITICAL/HIGH CVEs |

**Why Shift-Left?**
- Find issues early (cheaper to fix)
- Prevent vulnerabilities reaching production
- Automated enforcement (no human bypass)

### Network Security

```yaml
# Network Policy - restrict traffic
spec:
  podSelector:
    matchLabels:
      app: my-app
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
  egress:
    - to:
        - ipBlock:
            cidr: 10.0.0.0/8  # Only VPC
      ports:
        - port: 5432  # Only database
```

### Compliance Checklist Pattern

```markdown
### Container Security
- [x] Non-root user
- [x] Read-only filesystem
- [x] Image scanning

### Kubernetes
- [x] Network policies
- [x] Resource limits
- [x] Security context

### Infrastructure
- [x] Private subnets
- [x] Encrypted storage
- [x] No public S3
```

### Vulnerability Response

| Severity | Response Time | Action |
|----------|---------------|--------|
| CRITICAL | 24 hours | Hotfix deploy |
| HIGH | 7 days | Next release |
| MEDIUM | 30 days | Scheduled |
| LOW | 90 days | Backlog |

## Key Learnings

1. **Never hardcode secrets** - Use Secrets Manager, K8s Secrets, or env vars from CI/CD
2. **OIDC > Static keys** - No credentials to rotate or leak
3. **Scan early, scan often** - Every PR, every build
4. **Least privilege** - Minimal permissions everywhere
5. **Defense in depth** - Multiple layers, assume each can fail
