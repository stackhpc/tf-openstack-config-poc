locals {
  groups_list = flatten([
    for user_name, user in var.users : [
      for group_name in user.groups : {
        user = user_name
        group = group_name
      }
    ]
  ])
}

resource "openstack_identity_user_v3" "user" {
    for_each = var.users

    name = each.key
    description = each.value.description
    password = lookup(each.value, "password", null) ## TOOD: check if we can not specify a password
    ignore_change_password_upon_first_use = false
    #default_project_id = openstack_identity_project_v3.project[each.value.default_project].id
    extra = {
      email = each.value.email
    }
}

resource "openstack_identity_user_membership_v3" "user_membership" {
    for_each = {for m in local.groups_list: "${m.user}:${m.group}" => m}

    user_id  = openstack_identity_user_v3.user[each.value.user].id
    group_id = openstack_identity_group_v3.group[each.value.group].id
}

