variable "projects" {
  description = <<-EOT
    Map of projects. Keys are project name. Values are mappings with keys/values:
      description: string
      compute_quota: mapping
      network_quota: mapping
      blockstorage_quota: mapping
    For keys/values for quotas see type declarations
  EOT
  type = map(
    object({
      description = string
      compute_quota = optional(
        object({
          key_pairs            = optional(number)
          ram                  = optional(number)
          cores                = optional(number)
          instances            = optional(number)
          server_groups        = optional(number)
          server_group_members = optional(number)
        })
      )
      blockstorage_quota = optional(
        object({
          volumes              = optional(number)
          snapshots            = optional(number)
          gigabytes            = optional(number)
          per_volume_gigabytes = optional(number)
          backups              = optional(number)
          backup_gigabytes     = optional(number)
          groups               = optional(number)
          volume_type_quota    = optional(map(any)) # TODO: improve!
        })
      )
      network_quota = optional(
        object({
          floatingip          = optional(number)
          network             = optional(number)
          port                = optional(number)
          rbac_policy         = optional(number)
          router              = optional(number)
          security_group      = optional(number)
          security_group_rule = optional(number)
          subnet              = optional(number)
          subnetpool          = optional(number)
        })
      )
    })
  )
  default = {}
}

variable "groups" {
  description = "Map of groups. Keys are group names, values are group descriptions"
  type        = map(string)
  default     = {}
}

variable "users" {
  description = <<-EOT
    Map of users. Keys are user names. Values are mappings with keys/values:
      description: string
      email: string
      groups: list of group name strings, must be keys from var.groups
      password: optional string **WARNING** this will be saved in state
    If password is provided, this must be changed on first use.
  EOT
  type    = map(
    object({
      description = string
      email = string
      groups = list(string)
      password = optional(string)
    })
  )
  default = {}
}

variable "role_assignments" {
  description = <<-EOT
    List of role assignments. Elements are maps with keys/values:
      role: string name of pre-existing role
      group: string group name, a key from var.groups
      project: string project name, a key from var.projects
    Note an error will occur if elements are not unique.
  EOT
  type = list(
    object({
      role    = string
      group   = string
      project = string
    })
  )
  default = []
}

variable "network_rbac" {
  description = <<-EOT
    List of network RBAC configurations. Elements are maps with keys/values:
      network: string name of pre-existing network
      projects: list of project name strings, must be keys from var.projects
      access: string access type, "access_as_external" or "access_as_shared"
  EOT
  type = list(
    object({
      network  = string
      projects = list(string)
      access   = string
    })
  )
  validation {
    condition     = alltrue([for v in var.network_rbac : contains(["access_as_external", "access_as_shared"], v.access)])
    error_message = "Value for access must be access_as_external or access_as_shared"
  }
  default = []
}

variable "flavors" {
  description = <<-EOT
        Mapping of flavor definitions. Key is flavor name, and must be quoted
        if it contains ".". Values are mappings with with keys/values:
            ram: Required integer
            vcpus: Required integer
            disk: Required integer
            ephemeral: Optional integer
            swap: Optional integer
            rx_tx_factor: Optional
            is_public: Optional bool, default true. If "projects" is non-empty
            this is ignored and set false
            flavor_id: Optional string
            extra_specs: Optional mapping
            projects: Optional list of project names to which flavor should be
            mapped (i.e. flavor only visible/usable from these projects). Project
            names must be keys from var.projects.
    EOT
  type = map(
    object({
      ram          = number
      vcpus        = number
      disk         = number
      ephemeral    = optional(number)
      swap         = optional(number)
      rx_tx_factor = optional(number)
      is_public    = optional(bool, true)
      flavor_id    = optional(string)
      extra_specs  = optional(map(string))
      projects     = optional(list(string), [])
    })
  )
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
