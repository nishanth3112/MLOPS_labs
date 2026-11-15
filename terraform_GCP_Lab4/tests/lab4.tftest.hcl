# Runs offline: the mock provider fakes Google's responses, so no credentials
# or real resources are used. Run with: terraform test

mock_provider "google" {}

# Set every variable so results don't depend on a local terraform.tfvars.
variables {
  project_id         = "test-project"
  region             = "us-central1"
  zone               = "us-central1-a"
  environment        = "dev"
  owner              = "nishanth"
  machine_type       = "e2-micro"
  object_expiry_days = 30
}

run "defaults" {
  command = plan

  assert {
    condition     = google_compute_instance.vm.machine_type == "e2-micro"
    error_message = "VM should default to e2-micro."
  }

  assert {
    condition = google_compute_instance.vm.labels == tomap({
      course      = "ie7374"
      lab         = "terraform-lab4"
      environment = "dev"
      owner       = "nishanth"
      managed_by  = "terraform"
    })
    error_message = "VM labels are wrong."
  }

  assert {
    condition     = google_storage_bucket.bucket.labels == google_compute_instance.vm.labels
    error_message = "Bucket and VM should share the same labels."
  }

  assert {
    condition     = length(google_compute_instance.vm.network_interface[0].access_config) == 0
    error_message = "VM must not have an external IP."
  }

  assert {
    condition     = length(google_compute_instance.vm.service_account) == 0
    error_message = "VM must not have a service account attached."
  }

  assert {
    condition     = google_storage_bucket.bucket.name == "test-project-tf-lab4"
    error_message = "Bucket name should be <project_id>-tf-lab4."
  }

  assert {
    condition     = google_storage_bucket.bucket.public_access_prevention == "enforced"
    error_message = "Bucket must block public access."
  }

  assert {
    condition     = google_storage_bucket.bucket.force_destroy == false
    error_message = "Bucket must not be deletable while it still has objects."
  }

  assert {
    condition     = google_storage_bucket.bucket.uniform_bucket_level_access
    error_message = "Bucket must use uniform bucket-level access."
  }

  assert {
    condition     = one(google_storage_bucket.bucket.versioning).enabled
    error_message = "Bucket versioning must be on."
  }

  assert {
    condition     = one(one(google_storage_bucket.bucket.lifecycle_rule).condition).age == 30
    error_message = "Objects should expire after 30 days by default."
  }
}

run "variable_overrides" {
  command = plan

  variables {
    environment        = "test"
    object_expiry_days = 7
  }

  assert {
    condition     = google_compute_instance.vm.labels["environment"] == "test"
    error_message = "environment variable should set the VM label."
  }

  assert {
    condition     = google_storage_bucket.bucket.labels["environment"] == "test"
    error_message = "environment variable should set the bucket label."
  }

  assert {
    condition     = one(one(google_storage_bucket.bucket.lifecycle_rule).condition).age == 7
    error_message = "object_expiry_days should set the lifecycle age."
  }
}

run "rejects_large_machine_type" {
  command = plan

  variables {
    machine_type = "n2-standard-4"
  }

  expect_failures = [var.machine_type]
}

run "rejects_bad_environment" {
  command = plan

  variables {
    environment = "prod"
  }

  expect_failures = [var.environment]
}

run "rejects_bad_owner" {
  command = plan

  variables {
    owner = "Nishanth M"
  }

  expect_failures = [var.owner]
}
