# Lab 4: Terraform Infrastructure on Google Cloud

This lab uses Terraform to create, modify and destroy a Compute Engine VM and a Cloud Storage bucket on Google Cloud. It is my version of the Professor's [Terraform GCP Beginner Lab](https://github.com/raminmohammadi/MLOps/tree/main/Labs/Terraform_Labs/GCP/Lab1_Beginner).

> **Status:** Deployed, modified, and destroyed on GCP project `mlops-cloud-run-lab-2`. No resources are left running. See [Results](#11-results).

## 1. Objective

Same learning goals as the reference lab:

- Understand what Terraform does and how it tracks resources in state.
- Write a Terraform configuration for GCP.
- Use `init`, `plan`, `apply` and `destroy` to manage infrastructure.
- Modify existing resources and read the plan before applying.
- Understand the state file and the `.terraform` directory.

## 2. Differences from the reference lab

| Reference lab | This lab |
|---|---|
| Service account JSON key with the Editor role, set through `GOOGLE_APPLICATION_CREDENTIALS` | Application Default Credentials (`gcloud auth application-default login`). No key is created or stored. |
| One `main.tf` with the project ID hard-coded | Split into `versions.tf`, `variables.tf`, `main.tf` and `outputs.tf`. The project ID comes from a gitignored `terraform.tfvars`. |
| No variables or outputs | 7 variables (4 with validation rules) and 6 outputs |
| Labels only on the VM, hard-coded | One shared label set applied to both resources, built from variables |
| `f1-micro` VM on `debian-11` | `e2-micro` on `debian-12` (Debian 11 is end of life). No external IP and no service account attached. |
| Bucket with only `force_destroy` | Uniform access, public access prevention enforced, versioning, and a lifecycle rule that deletes objects after N days |
| Modification by editing the code | Modification by changing variable values only (`environment`, `object_expiry_days`) |
| Nothing to keep state or keys out of Git | `.gitignore` for state, tfvars, plans, `.terraform/` and `*.json` keys |
| No tests | 5 `terraform test` runs with a mock provider, which need no credentials |
| `terraform apply -auto-approve` mentioned | Every change applied from a saved plan file that was reviewed first |

## 3. Tools

| Tool | Version / purpose |
|---|---|
| Terraform | v1.17.1 |
| Google provider (`hashicorp/google`) | 8.11.0, pinned in `.terraform.lock.hcl` |
| Google Cloud CLI (`gcloud`) | Authentication, enabling APIs, checking resources |
| Google Cloud | Compute Engine and Cloud Storage in project `mlops-cloud-run-lab-2` |

## 4. Project structure

```text
terraform_GCP_Lab4/
├── .gitignore                # Keeps state, tfvars, plans, plugins and keys out of Git
├── .terraform.lock.hcl       # Pins the provider version (committed)
├── versions.tf               # Terraform and provider version requirements
├── variables.tf              # Input variables with validation
├── main.tf                   # Provider, labels, VM and bucket
├── outputs.tf                # Values printed after apply
├── terraform.tfvars.example  # Template for terraform.tfvars (committed)
├── tests/
│   └── lab4.tftest.hcl       # Offline tests using a mock provider
└── README.md
```

These files are created locally but **never committed** (see `.gitignore`):

| File | Why it stays out of Git |
|---|---|
| `terraform.tfstate`, `terraform.tfstate.backup` | State holds resource details and is the source of truth for Terraform. It should not be shared through Git. |
| `terraform.tfvars` | Local values for your project |
| `.terraform/` | Provider plugins downloaded by `terraform init` (large, platform-specific) |
| `*.tfplan` | Saved plans, used once |
| `*.json` | Protects against accidentally committing a service account key |

## 5. Configuration

### Variables

| Variable | Default | Validation |
|---|---|---|
| `project_id` | none (required) | |
| `region` | `us-central1` | |
| `zone` | `us-central1-a` | |
| `environment` | `dev` | `dev` or `test` |
| `owner` | `nishanth` | lowercase letters, numbers, `-` or `_` (GCP label rules) |
| `machine_type` | `e2-micro` | `e2-micro` or `e2-small`, to keep cost low |
| `object_expiry_days` | `30` | at least 1 |

### Resources

| Resource | Name | Settings |
|---|---|---|
| `google_compute_instance.vm` | `tf-lab4-vm` | `e2-micro`, `debian-12`, 10 GB `pd-standard` disk, `default` network, no external IP, no service account, `allow_stopping_for_update = true` |
| `google_storage_bucket.bucket` | `<project_id>-tf-lab4` | `us-central1`, uniform bucket-level access, public access prevention `enforced`, versioning on, delete objects after `object_expiry_days`, `force_destroy = true` |

Both resources get the same labels: `course=ie7374`, `lab=terraform-lab4`, `environment`, `owner`, `managed_by=terraform`. The provider also adds `goog-terraform-provisioned=true` on its own.

### Outputs

`vm_name`, `vm_zone`, `vm_machine_type`, `vm_internal_ip`, `bucket_name`, `bucket_url`.

## 6. Authentication (no service account keys)

The provider block has no `credentials` setting. Terraform uses Application Default Credentials, the same login `gcloud` uses for client libraries:

```bash
gcloud config set project mlops-cloud-run-lab-2
gcloud auth application-default login
```

This avoids creating a long-lived JSON key that could leak or be committed by mistake. The `*.json` rule in `.gitignore` is a second safety net.

## 7. Step-by-step commands

All Terraform commands are run **from `terraform_GCP_Lab4/`**. Terraform only reads the `.tf` files and state in the current folder.

### Step 1: Initialize and validate (no cloud changes)

```bash
cd terraform_GCP_Lab4
terraform version            # Terraform v1.17.1
terraform fmt -check         # passed, no formatting changes needed
terraform init               # installed hashicorp/google v8.11.0
terraform validate           # Success! The configuration is valid.
```

### Step 2: Enable the Compute Engine API

The project only had the Storage APIs enabled, and creating a VM needs the Compute API:

```bash
gcloud services enable compute.googleapis.com --project mlops-cloud-run-lab-2
gcloud compute networks list --project mlops-cloud-run-lab-2   # default (AUTO)
```

### Step 3: Plan and create the resources

```bash
cp terraform.tfvars.example terraform.tfvars   # sets project_id
terraform plan -out=lab4.tfplan                # Plan: 2 to add, 0 to change, 0 to destroy.
terraform apply lab4.tfplan                    # Apply complete! Resources: 2 added, 0 changed, 0 destroyed.
```

Saving the plan to a file and applying that file makes sure Terraform does exactly what was reviewed. Outputs after apply:

```text
bucket_name     = "mlops-cloud-run-lab-2-tf-lab4"
bucket_url      = "gs://mlops-cloud-run-lab-2-tf-lab4"
vm_internal_ip  = "10.128.0.2"
vm_machine_type = "e2-micro"
vm_name         = "tf-lab4-vm"
vm_zone         = "us-central1-a"
```

Check the resources outside Terraform:

```bash
gcloud compute instances describe tf-lab4-vm --zone us-central1-a \
  --format="yaml(name,status,machineType.basename(),labels,networkInterfaces[0].accessConfigs,serviceAccounts)"
gcloud storage buckets describe gs://mlops-cloud-run-lab-2-tf-lab4 \
  --format="yaml(name,location,labels,versioning_enabled,public_access_prevention,uniform_bucket_level_access,lifecycle_config)"
terraform plan    # No changes. Your infrastructure matches the configuration.
```

### Step 4: Modify the resources with variables

Only `terraform.tfvars` was changed. No `.tf` file was edited:

```hcl
project_id = "mlops-cloud-run-lab-2"

environment        = "test"   # was "dev"
object_expiry_days = 7        # was 30
```

```bash
terraform plan -out=lab4-phase4.tfplan   # Plan: 0 to add, 2 to change, 0 to destroy.
terraform apply lab4-phase4.tfplan       # Apply complete! Resources: 0 added, 2 changed, 0 destroyed.
```

Both resources were updated **in place** (`~` in the plan). The VM stayed `RUNNING`, its `environment` label became `test`, and the bucket's lifecycle rule changed to 7 days. The plan shows the lifecycle `condition` block as removed and added again; that is how the provider displays a change inside a nested block, and the only real change is `age = 30 → 7`.

### Step 5: Run the tests

```bash
terraform test    # Success! 5 passed, 0 failed.
```

### Step 6: Destroy everything

```bash
terraform plan -destroy -out=lab4-destroy.tfplan   # Plan: 0 to add, 0 to change, 2 to destroy.
terraform apply lab4-destroy.tfplan                # Apply complete! Resources: 0 added, 0 changed, 2 destroyed.
```

Check that nothing is left:

```bash
terraform state list                                                  # (empty)
gcloud compute instances list --project mlops-cloud-run-lab-2         # Listed 0 items.
gcloud compute disks list --project mlops-cloud-run-lab-2             # Listed 0 items.
gcloud storage buckets describe gs://mlops-cloud-run-lab-2-tf-lab4    # not found: 404
```

The Compute Engine API was left enabled. It costs nothing by itself.

## 8. Tests

[`tests/lab4.tftest.hcl`](tests/lab4.tftest.hcl) uses `mock_provider "google" {}`, so `terraform test` never contacts Google Cloud. Every run uses `command = plan`, and every variable is set inside the test file, so the results don't depend on a local `terraform.tfvars`. I confirmed they need no credentials by running them with the gcloud config pointed at an empty folder: all 5 passed, and `terraform.tfstate` was unchanged.

| Run | What it checks |
|---|---|
| `defaults` | `e2-micro`, all 5 labels on both resources, no external IP, no service account, bucket name, public access blocked, uniform access, versioning, 30-day expiry |
| `variable_overrides` | `environment = "test"` and `object_expiry_days = 7` reach the labels and the lifecycle rule (the Step 4 change) |
| `rejects_large_machine_type` | `n2-standard-4` is rejected by the variable check |
| `rejects_bad_environment` | `prod` is rejected |
| `rejects_bad_owner` | `Nishanth M` is rejected (not a valid GCP label value) |

## 9. Cost and safety notes

- The VM was `e2-micro` in `us-central1` with a 10 GB standard disk and no external IP. That fits Google Cloud's always-free tier, as long as no other `e2-micro` runs on the same billing account.
- `machine_type` only allows `e2-micro` or `e2-small`, so a typo can't create an expensive VM.
- The bucket's lifecycle rule deletes old objects, and public access is blocked.
- Everything was destroyed at the end and checked with `gcloud`.

## 10. Lessons and gotchas

- **Run Terraform from the lab folder.** Running `terraform plan -destroy` from the repo root printed "No objects need to be destroyed" even though the VM was still running. The root has no `.tf` files or state, so Terraform saw nothing.
- **A saved plan can only be applied once.** After applying, create a new plan.
- **Some changes are in place and some force a replacement.** Labels, lifecycle rules and (with `allow_stopping_for_update`) the machine type are updated in place. Changing the boot disk image or size recreates the VM. Always read the plan for `~` (update) versus `-/+` (replace).
- **State is the source of truth.** Terraform compares the config with the state file, then with the real resources. Never edit `terraform.tfstate` by hand and never commit it.

## 11. Results

| Step | Verified outcome |
|---|---|
| Validate | `fmt` passed, provider 8.11.0 installed, configuration valid |
| Create | 2 added: bucket in 1 s, VM in 19 s. All settings and labels confirmed with `gcloud`. A new plan showed no changes. |
| Modify | 2 changed in place. VM stayed `RUNNING`. `environment=test` on both resources, lifecycle age 7. A new plan showed no changes. |
| Test | 5 passed, 0 failed, with no credentials available |
| Destroy | 2 destroyed: bucket in 1 s, VM in 31 s. State empty, 0 instances, 0 disks, bucket returns 404. |
