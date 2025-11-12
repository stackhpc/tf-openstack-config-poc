
variable "name" {}
variable "description" {}
variable "quotas" {}

resource "openstack_identity_project_v3" "project" {
  name        = var.name
  description = var.description
}

resource "openstack_blockstorage_quotaset_v3" "project" {
  project_id = openstack_identity_project_v3.project.id
  # so need to set these to null if not required
  volumes   = lookup(var.quotas, "volumes", null)
  snapshots = lookup(var.quotas, "snapshots", null)
  gigabytes = lookup(var.quotas, "gigabytes", null)
  per_volume_gigabytes = lookup(var.quotas, "per_volume_gigabytes", null)
  backups = lookup(var.quotas, "backups", null)
  backup_gigabytes = lookup(var.quotas, "backup_gigabytes", null)
  groups = lookup(var.quotas, "groups", null)
  volume_type_quota = lookup(var.quotas, "volume_type_quota", null)
  # in below $TYPE is presumably result of `openstack volume type list -c Name`
  #   volumes_$TYPE = 30
  #   gigabytes_$TYPE = 500
  #   snapshots_$TYPE = 10
  # }
}

resource "openstack_compute_quotaset_v2" "project" {
  project_id           = openstack_identity_project_v3.project.id
  key_pairs            = lookup(var.quotas, "key_pairs", null)
  ram                  = lookup(var.quotas, "ram", null)
  cores                = lookup(var.quotas, "cores", null)
  instances            = lookup(var.quotas, "instances", null)
  server_groups        = lookup(var.quotas, "server_groups", null)
  server_group_members = lookup(var.quotas, "server_group_members", null)
}

# # What about manila? doens't appear to be a thing for that

output "id" {
  value = openstack_identity_project_v3.project.id
}
