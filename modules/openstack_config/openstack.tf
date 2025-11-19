variable "projects" {
    type = any # TODO: tighten up?
    default = {}
}

variable "groups" {
    type = map(string)
    default = {}
}

variable "users" {
    type = map(string)
    default = {}
}

variable "role_assignments" {
    type = any # TODO: tighten up?
    default = []
}

variable "network_rbac" {
    type = any
    default = []
}

# TODO: more outputs?
output "projects" {
    #value = {for k, v in openstack_identity_project_v3.project: k => v.id}
    value = openstack_identity_project_v3.project
}

output "groups" {
    #value = {for k, v in openstack_identity_group_v3.group: k => v.id}
    value = openstack_identity_group_v3.group
}

output "role_assignments" {
    value = openstack_identity_role_assignment_v3.role_assign
}

# output "debug" {
#     value = {for v in flatten([for rbac in var.network_rbac: [for project in rbac.projects: {rbac=rbac, project=project}]]): "${v.rbac.network}:${v.project}" => v}
# }
