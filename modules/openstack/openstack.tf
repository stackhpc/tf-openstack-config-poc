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
# TODO: should we return the entire structure, not just ids?
output "projects" {
    value = {for k, v in openstack_identity_project_v3.project: k => v.id}
}

output "groups" {
    value = {for k, v in openstack_identity_group_v3.group: k => v.id}
}

output "debug" {
    value = {for v in flatten([for rbac in var.network_rbac: [for project in rbac.projects: {rbac=rbac, project=project}]]): "${v.rbac.network}:${v.project}" => v}
}
