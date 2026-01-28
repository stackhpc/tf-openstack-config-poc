variable "small_quota" {
  type = any
  default = {
    instances    = 20
    cores        = 200
    ram          = 512000 # 500GB
    floating_ips = 3
    routers      = 3
    ports        = 500
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

