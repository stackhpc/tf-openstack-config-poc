module "project_1" {
    source = "./modules/project"
    name = "sb-test-1"
    description = "Project One"
    # project_domain?
    # user_domain?
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
}


module "project_2" {
    source = "./modules/project"
    name        = "sb-test-2"
    description = "Project Two"
    quotas = {
        # TODO: need to have at least one blockstorage and one compute quota set!
        # so maybe split them out?
        volumes = 2
        cores = 64
    }
}

# -- groups  --
resource "openstack_identity_group_v3" "A" {
  name        = "GroupA"
  description = "Group A"
}

resource "openstack_identity_group_v3" "B" {
  name        = "GroupB"
  description = "Group B"
}

# role assignments: many-to-many users/projects/roles
# TODO: hard to have meaninful names for these!

module "roleA" {
  source = "./modules/role"
  role_name = "member"
  group_id = openstack_identity_group_v3.A.id
  project_id = module.project_1.id
}

module "roleB" {
  source = "./modules/role"
  role_name = "reader"
  group_id    = openstack_identity_group_v3.B.id
  project_id = module.project_2.id
}

# -- faked stuff, will be done by federation --
data "openstack_identity_user_v3" "steveb" {
  name = "steveb_stack"
}

resource "openstack_identity_user_membership_v3" "steveb_A" {
  user_id  = data.openstack_identity_user_v3.steveb.id
  group_id = openstack_identity_group_v3.A.id
}

resource "openstack_identity_user_membership_v3" "steveb_B" {
  user_id  = data.openstack_identity_user_v3.steveb.id
  group_id = openstack_identity_group_v3.B.id
}
# -- end of faked stuff --
