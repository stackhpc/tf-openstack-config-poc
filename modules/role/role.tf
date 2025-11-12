
variable "role_name" {}
variable "group_id" {}
variable "project_id" {
  
}

data  "openstack_identity_role_v3" "role" {
# TODO: is data right here?
  name = var.role_name
}

resource "openstack_identity_role_assignment_v3" "A" {
  group_id    = var.group_id
  project_id = var.project_id
  role_id    = data.openstack_identity_role_v3.role.id
}
