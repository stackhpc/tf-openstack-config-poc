variable "projects" {
    type = any # TODO: tighten up?
    default = {}
}

variable "groups" {
    type = map(string)
    default = {}
}

variable "users" {
    type = any
    default = {}
}

variable "role_assignments" {
    type = any # TODO: tighten up?
    default = []
    description = "Note an error will occur if these are not unique"
}

variable "network_rbac" {
    type = any
    default = []
}

variable "flavors" {
    type = any
    description = <<-EOT
        Mapping of flavor definitions. Key is flavor name, and must be quoted
        if it contains ".". Possible values:
            ram: Required integer
            vcpus: Required integer
            disk: Required integer
            ephemeral: Optional integer
            swap: Optional integer
            rx_tx_factor: Optional
            is_public: Optional bool. Default true. If "projects" is non-empty this is ignored and set false
            flavor_id: Optional string
            extra_specs: Optional mapping
    EOT
    default = {}
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
