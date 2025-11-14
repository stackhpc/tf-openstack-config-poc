resource "openstack_identity_project_v3" "project" {
  for_each = var.projects

  name        = each.key
  description = each.value.description
}

locals {
  blockstorage_params = [
    "volumes",
    "snapshots",
    "gigabytes",
    "per_volume_gigabytes",
    "backups",
    "backup_gigabytes",
    "groups",
    "volume_type_quota"
  ]
  
}

resource "openstack_blockstorage_quotaset_v3" "project" {
  # Skip projects where quotas has no blockstorage keys, else fails with
  # {"code": 400, "message": "Invalid input for field/attribute quota_set. Value: {}. {} does not have enough properties"}
  for_each = {for name, proj in var.projects: name => proj if length(setintersection(keys(proj.quotas) , local.blockstorage_params)) > 0}
  
  project_id = openstack_identity_project_v3.project[each.key].id
  # so need to set these to null if not required
  volumes              = lookup(each.value.quotas, "volumes", null)
  snapshots            = lookup(each.value.quotas, "snapshots", null)
  gigabytes            = lookup(each.value.quotas, "gigabytes", null)
  per_volume_gigabytes = lookup(each.value.quotas, "per_volume_gigabytes", null)
  backups              = lookup(each.value.quotas, "backups", null)
  backup_gigabytes     = lookup(each.value.quotas, "backup_gigabytes", null)
  groups               = lookup(each.value.quotas, "groups", null)
  volume_type_quota    = lookup(each.value.quotas, "volume_type_quota", null)
  # in above $TYPE is presumably result of `openstack volume type list -c Name`:
  #   volumes_$TYPE = 30
  #   gigabytes_$TYPE = 500
  #   snapshots_$TYPE = 10
  # }
}

resource "openstack_compute_quotaset_v2" "project" {
  for_each = var.projects

  project_id           = openstack_identity_project_v3.project[each.key].id
  key_pairs            = lookup(each.value.quotas, "key_pairs", null)
  ram                  = lookup(each.value.quotas, "ram", null)
  cores                = lookup(each.value.quotas, "cores", null)
  instances            = lookup(each.value.quotas, "instances", null)
  server_groups        = lookup(each.value.quotas, "server_groups", null)
  server_group_members = lookup(each.value.quotas, "server_group_members", null)
}

resource "openstack_networking_quota_v2" "project" {
  for_each = var.projects

  project_id          = openstack_identity_project_v3.project[each.key].id
  floatingip          = lookup(each.value.quotas, "floatingip", null)
  network             = lookup(each.value.quotas, "network", null)
  port                = lookup(each.value.quotas, "port", null)
  rbac_policy         = lookup(each.value.quotas, "rbac_policy", null)
  router              = lookup(each.value.quotas, "router", null)
  security_group      = lookup(each.value.quotas, "security_group", null)
  security_group_rule = lookup(each.value.quotas, "security_group_rule", null)
  subnet              = lookup(each.value.quotas, "subnet", null)
  subnetpool          = lookup(each.value.quotas, "subnetpool", null)
}

# TODO: add network
# TODO: What about manila? doens't appear to be a quota for that
