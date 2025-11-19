variable "small_quota" {
  type = any
  default = {
    instances    = 20
    cores        = 200
    ram          = 512000 # 500GB
    floating_ips = 3
    routers      = 3
    ports        = 500
    volumes = 10
  }
}

module "openstack" {
  source = "./modules/openstack_config"

  # TODO: domain
  # TODO: add ci/cd - PR tofu fmt, plan/approval (on merge) (don't run external PRs)
  projects = {
    sb-test-1 = {
      description = "Project One"
      # project_domain/user_domain? TF only has domain_id and is_domain
      quotas = var.small_quota
    },
    sb-test-2 = {
      description = "Project Two"
      quotas      = var.small_quota
    }
  }
  groups = {
    GroupA = "Group A"
    GroupB = "Group B"
  }

  role_assignments = [
    {
      role    = "member"
      group   = "GroupA"
      project = "sb-test-1"
    },
    {
      role    = "reader"
      group   = "GroupB"
      project = "sb-test-2"
    }
  ]

  # TODO: users

  network_rbac = [
    {
      network = "storage-net"
      projects = ["sb-test-2"]
      access = "access_as_external"
    },
  ]

  # TODO: flavor_rbac
  # agreed to keep separate from network, as for ansible

}

# -- faked stuff, will be done by federation --
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
