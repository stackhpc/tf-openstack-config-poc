variable "arcus_small_quota" {
  type = any
  default = {
    instances = 20
    cores = 200
    ram = 512000 # 500GB
    floating_ips = 3
    routers = 3
    ports = 500
  }
}

module "openstack" {
  source = "./modules/openstack"

  # TODO: domain
  # TODO: add ci/cd - PR tofu fmt, plan/approval (on merge) (don't run external PRs)
  projects = {
    sb-test-1 = {
      description = "Project One"
      # project_domain/user_domain? TF only has domain_id and is_domain
      quotas = var.arcus_small_quota
    },
    sb-test-2 = {
      description = "Project Two"
      quotas = var.arcus_small_quota
    }
  }
  groups = {
    GroupA = "Group A"
    GroupB = "Group B"
  }

  role_assignments = [
    {
      role  = "member"
      group = "GroupA"
      
      project = "sb-test-1"
    },
    {
      role    = "reader"
      group   = "GroupB"
      project = "sb-test-2"
    }
  ]

  # TODO: user

  # TODO: flavor_rbac (yes as separate thing)
  # TODO: why is this already in there?
  # network_rbac = [
  #   {
  #     network = "CUDN-Internet"
  #     projects = ["sb-test-1", "sb-test-2"]
  #     action = "access_as_external"
  #   },
  # ]
}

# -- faked stuff, will be done by federation --
data "openstack_identity_user_v3" "steveb" {
  name = "steveb_stack"
}

# TODO: fixme!
resource "openstack_identity_user_membership_v3" "steveb_A" {
  user_id  = data.openstack_identity_user_v3.steveb.id
  group_id = module.openstack.groups["GroupA"]
}

resource "openstack_identity_user_membership_v3" "steveb_B" {
  user_id  = data.openstack_identity_user_v3.steveb.id
  group_id = module.openstack.groups["GroupB"]
}
# -- end of faked stuff --

output "debug" {
  value = module.openstack.debug
}
