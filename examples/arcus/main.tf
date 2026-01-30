variable "small_compute_quota" {
  type = any
  default = {
    instances    = 20
    cores        = 200
    ram          = 512000 # 500GB
  }
}

variable "small_network_quota" {
  type = any
  default = {
    floating_ips = 3
    routers      = 3
    ports        = 500
  }
}

variable "small_blockstorage_quota" {
  type = any
  default = {
    volumes = 10
    gigabytes = 10
  }
}

module "openstack" {
  source = "../../modules/openstack_config"

  # TODO: domain
  # TODO: add ci/cd - PR tofu fmt, plan/approval (on merge) (don't run external PRs)
  projects = {
    sb-test-1 = {
      description = "Project One"
      # project_domain/user_domain? TF only has domain_id and is_domain
      compute_quotas = var.small_compute_quota
      network_quotas = var.small_network_quota
      blockstorage_quota = var.small_blockstorage_quota
    },
    sb-test-2 = {
      description = "Project Two"
      compute_quotas = var.small_compute_quota
      network_quotas = var.small_network_quota
      #blockstorage_quota = var.small_blockstorage_quota
    }
  }
  groups = {
    GroupA = "Group A"
    GroupB = "Group B"
    GroupC = "Group C"
  }

  role_assignments = [
    {
      role    = "member"
      group   = "GroupA"
      project = "sb-test-1"
    },
    # uncomment and apply to demonstrate stability:
    # {
    #   role = "member"
    #   group = "GroupC"
    #   project = "sb-test-1"
    # },
    {
      role    = "reader"
      group   = "GroupB"
      project = "sb-test-2"
    }
  ]

  network_rbac = [
    {
      network = "storage-net"
      projects = ["sb-test-2"]
      access = "access_as_external"
    },
  ]

  users = {
    user1 = {
       description = "User 1"
       email = "user1@example.com"
       groups = [ "GroupA" ]
       password = "super-secret-password"
    },
    user2 = {
       description = "User 2"
       email = "user2@example.com"
       groups = [ "GroupA", "GroupB" ]
       password = "super-secret-password"
    }
  }

  # TODO: flavor_rbac
  # agreed to keep separate from network, as for ansible

}

# -- faked stuff, will be done by federation
data "openstack_identity_user_v3" "steveb" {
  name = "steveb_stack"
}

resource "openstack_identity_user_membership_v3" "steveb_A" {
  user_id  = data.openstack_identity_user_v3.steveb.id
  group_id = module.openstack.groups["GroupA"].id
}

resource "openstack_identity_user_membership_v3" "steveb_B" {
  user_id  = data.openstack_identity_user_v3.steveb.id
  group_id = module.openstack.groups["GroupB"].id
}
# -- end of faked stuff --

# output "debug" {
#   value = module.openstack.debug
# }