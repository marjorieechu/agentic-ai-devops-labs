# Documentation & Architecture Skills

## Project Reference
- Repository: [titanic-devops-assessment](https://github.com/marjorieechu/titanic-devops-assessment)

## Skills Demonstrated

### README Structure

| Section | Purpose |
|---------|---------|
| Summary | Quick overview of what was built |
| Architecture | Visual diagram of components |
| Cost Estimation | Monthly costs per environment |
| Disaster Recovery | RTO/RPO for each component |
| Quick Start | Commands to get running |

### Cost Estimation

| Resource | What to estimate |
|----------|-----------------|
| EKS Cluster | $73/month (control plane) |
| EC2 Nodes | Instance type × count × hours |
| RDS | Instance type + storage + IOPS |
| ALB | Fixed + LCU hours |
| NAT Gateway | Fixed + data processed |
| Data Transfer | Egress to internet |

**Cost Optimization:**
- Spot instances for non-prod (60-70% savings)
- Reserved instances for prod (30-40% savings)
- Fargate for variable workloads

### Disaster Recovery

| Term | Meaning |
|------|---------|
| **RTO** | Recovery Time Objective - how long to recover |
| **RPO** | Recovery Point Objective - max data loss acceptable |

**DR Strategies:**
| Strategy | RTO | Cost |
|----------|-----|------|
| Backup & Restore | Hours | $ |
| Pilot Light | Minutes | $$ |
| Warm Standby | Minutes | $$$ |
| Active-Active | Seconds | $$$$ |

### Rolling Update vs DR

| Concern | Rolling Update | Disaster Recovery |
|---------|---------------|-------------------|
| Purpose | Zero-downtime deploys | Survive failures |
| Scope | Pod replacement | Data backup, multi-region |
| Handles | Bad code deployments | Infrastructure outages |

## Key Learnings

1. **Document as you build** - Easier than documenting after
2. **ASCII diagrams** - Work in any markdown renderer
3. **Cost estimation** - Essential for budget planning
4. **RTO/RPO** - Define before disaster happens
5. **Quick start** - Help others get running fast
