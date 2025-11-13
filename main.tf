module "openstack" {
    source = "./modules/openstack"


  # TODO: domain
    projects = {
      sb-test-1 = {
      description = "Project One"
      # project_domain/user_domain? TF only has domain_id and is_domain
      quotas = {
          volumes   = 2
          snapshots = 4
          gigabytes = 10
          per_volume_gigabytes = 2
          backups = 4
          backup_gigabytes = 10
          groups = 5
          volume_type_quota = {
              volumes_arcus-staging-ceph01-rbd = 5
          }
          key_pairs            = 10
          ram                  = 40960
          cores                = 32
          instances            = 5
          server_groups        = 2
          server_group_members = 6
      }
      # users = {}
      },
      sb-test-2 = {
      description = "Project Two"
      quotas = {
          # TODO: need to have at least one blockstorage and one compute quota set!
          # so maybe split them out?
          volumes = 2
          cores = 64
      }
    }
  }
  groups = {
    GroupA = "Group A"
    GroupB = "Group B"
  }

  role_assignments = [
    {
      role = "member"
      group = "GroupA"
      project = "sb-test-1"
    },
    {
      role = "reader"
      group = "GroupB"
      project = "sb-test-2"
    }
  ]
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

# output "debug" {
#   value = module.openstack.groups
# }