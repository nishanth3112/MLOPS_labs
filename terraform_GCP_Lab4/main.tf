# No credentials setting: the provider uses Application Default Credentials
# (gcloud auth application-default login), so no service account key is needed.
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

locals {
  labels = {
    course      = "ie7374"
    lab         = "terraform-lab4"
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
  }
}

resource "google_compute_instance" "vm" {
  name         = "tf-lab4-vm"
  machine_type = var.machine_type
  zone         = var.zone
  labels       = local.labels

  # Lets Terraform stop the VM to change machine_type instead of failing.
  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 10
      type  = "pd-standard"
    }
  }

  # No access_config block, so the VM gets no external IP.
  network_interface {
    network = "default"
  }

  # No service_account block, so the VM runs without the default Editor-level account.
}

resource "google_storage_bucket" "bucket" {
  name     = "${var.project_id}-tf-lab4"
  location = var.region
  labels   = local.labels

  # Lets terraform destroy remove the bucket even if it still has objects.
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = var.object_expiry_days
    }
    action {
      type = "Delete"
    }
  }
}
