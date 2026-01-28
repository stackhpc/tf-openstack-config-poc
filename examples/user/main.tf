
module "openstack" {
  source = "../../modules/openstack_config"

  # TODO: domain
  # TODO: add ci/cd - PR tofu fmt, plan/approval (on merge) (don't run external PRs)
  projects = {
    example-1 = {
      description = "Project One"
      # project_domain/user_domain? TF only has domain_id and is_domain
    },
    sb-test-2 = {
      description = "Project Two"
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
      project = "example-1"
    },
    {
      role    = "reader"
      group   = "GroupB"
      project = "example-2"
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
}
