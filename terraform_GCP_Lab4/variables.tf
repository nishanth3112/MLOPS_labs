variable "project_id" {
  description = "GCP project to deploy into."
  type        = string
}

variable "region" {
  description = "Region for the bucket and provider default."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zone for the VM."
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment label."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "test"], var.environment)
    error_message = "environment must be \"dev\" or \"test\"."
  }
}

variable "owner" {
  description = "Owner label (lowercase letters, numbers, - or _)."
  type        = string
  default     = "nishanth"

  validation {
    condition     = can(regex("^[a-z0-9_-]{1,63}$", var.owner))
    error_message = "owner must be 1-63 lowercase letters, numbers, - or _ (GCP label rules)."
  }
}

variable "machine_type" {
  description = "VM machine type. Limited to small types to keep costs low."
  type        = string
  default     = "e2-micro"

  validation {
    condition     = contains(["e2-micro", "e2-small"], var.machine_type)
    error_message = "machine_type must be \"e2-micro\" or \"e2-small\"."
  }
}

variable "object_expiry_days" {
  description = "Delete bucket objects after this many days."
  type        = number
  default     = 30

  validation {
    condition     = var.object_expiry_days >= 1
    error_message = "object_expiry_days must be at least 1."
  }
}
