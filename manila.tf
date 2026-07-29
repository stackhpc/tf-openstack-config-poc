resource "openstack_sharedfilesystem_sharetype_v2" "sharetypes" {
    for_each = var.sharetypes

    name = each.key

    description = lookup(each.value, "description", null)
    is_public  = lookup(each.value, "is_public", true)

    extra_specs = {
        driver_handles_share_servers = each.value.extra_specs.driver_handles_share_servers
        snapshot_support             = lookup(each.value.extra_specs, "snapshot_support", null)
        share_backend_name           = each.value.extra_specs.share_backend_name
        "vast:vippoolname"           = vastdata_vip_pool.vippools[each.value.extra_specs.vast_vip_pool_name].name
    }
}

resource "openstack_sharedfilesystem_sharetype_access_v2" "sharetypes_access" {
    for_each = var.sharetypes_access

    share_type_id = each.value.sharetype_name != null ? openstack_sharedfilesystem_sharetype_v2.sharetypes[each.value.sharetype_name].id : each.value.share_type_id
    project_id    = each.value.project != null ? openstack_identity_project_v3.project[each.value.project].id : each.value.project_id
}
