
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

# -- per-project stuff --

resource "openstack_identity_project_v3" "project_1" {
  name        = "sb-test-1"
  description = "Project One"
}

resource "openstack_blockstorage_quotaset_v3" "project_1" {
  project_id = openstack_identity_project_v3.project_1.id
  # so need to set these to null if not required
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
  # in below $TYPE is presumably result of `openstack volume type list -c Name`
  #   volumes_$TYPE = 30
  #   gigabytes_$TYPE = 500
  #   snapshots_$TYPE = 10
  # }
}

resource "openstack_compute_quotaset_v2" "quotaset_1" {
  project_id           = openstack_identity_project_v3.project_1.id
  key_pairs            = 10
  ram                  = 40960
  cores                = 32
  instances            = 5
  server_groups        = 2
  server_group_members = 6
}

# # What about manila? doens't appear to be a thing for that


resource "openstack_identity_project_v3" "project_2" {
  name        = "sb-test-2"
  description = "Project Two"
}
# TODO: no quotas added here here!

# -- groups  --

resource "openstack_identity_group_v3" "A" {
  name        = "GroupA"
  description = "Group A"
}

resource "openstack_identity_group_v3" "B" {
  name        = "GroupB"
  description = "Group B"
}

# -- roles - NB *not* per-project
# TODO: is using data ones for these correct?
data  "openstack_identity_role_v3" "member" {
  name = "member"
}

data  "openstack_identity_role_v3" "reader" {
  name = "reader"
}

data  "openstack_identity_role_v3" "loadbalancer" {
  name = "load-balancer_member"
}

# role assignments: many-to-many users/projects/roles
# TODO: hard to have meaninful names for these!
resource "openstack_identity_role_assignment_v3" "A" {
  group_id    = openstack_identity_group_v3.A.id
  project_id = openstack_identity_project_v3.project_1.id
  role_id    = data.openstack_identity_role_v3.member.id
}

resource "openstack_identity_role_assignment_v3" "B" {
  group_id    = openstack_identity_group_v3.B.id
  project_id = openstack_identity_project_v3.project_2.id
  role_id    = data.openstack_identity_role_v3.reader.id
}


# # --- quotas


# # --- roles and groups
# ## TODO: or are these a data thing?


# # or are these actually created by federation?
# resource "openstack_identity_group_v3" "group_1" {
#   # NB this is NOT per-project
#   name        = "group_1"
#   description = "group 1"
# }


# resource "openstack_identity_role_assignment_v3" "role_assignment_1" {
#   group_id    = openstack_identity_user_v3.user_1.id
#   project_id = openstack_identity_project_v3.project_1.id
#   role_id    = openstack_identity_role_v3.role_1.id
# }
# # or openstack_identity_inherit_role_assignment_v3?

# # e.g. https://github.com/stackhpc/smslab-config/blob/master/etc/openstack-config/openstack-config.yml

# # smslab_slurmci_project:
# #   name: slurm-ci
# #   description: SMS Lab Slurm CI project
# #   project_domain: stackhpc
# #   user_domain: stackhpc
# #   users: "{{ smslab_stackhpc_local_users }}"
# ### groups:
# #   quotas: "{{ smslab_slurmci_quotas }}"

# # smslab_slurmci_quotas:
# #   ram: 98304
# #   cores: 50
# #   instances: 50
# #   floatingip: 0
# #   network: 1
# #   router: 0
# #   subnet: 1
# #   security_group: 20
# #   gigabytes: 200

