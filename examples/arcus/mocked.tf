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