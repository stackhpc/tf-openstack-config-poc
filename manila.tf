resource "openstack_sharedfilesystem_share_v2" "shares" {
    for_each = var.shares

    name              = each.key
    share_proto       = each.value.share_proto
    size              = each.value.size
    region            = lookup(each.value, "region", null)
    description       = lookup(each.value, "description", null)
    share_type        = lookup(each.value, "share_type", null)
    snapshot_id       = lookup(each.value, "snapshot_id", null)
    is_public         = lookup(each.value, "is_public", false)
    metadata          = lookup(each.value, "metadata", null)
    share_network_id  = lookup(each.value, "share_network_id", null)
    availability_zone = lookup(each.value, "availability_zone", null)
}

resource "openstack_sharedfilesystem_sharetype_v2" "sharetypes" {
    for_each = var.sharetypes

    name = each.key

    description = lookup(each.value, "description", null)
    is_public  = lookup(each.value, "is_public", true)

    extra_specs = {
        driver_handles_share_servers = each.value.extra_specs.driver_handles_share_servers
        snapshot_support             = lookup(each.value.extra_specs, "snapshot_support", null)
        share_backend_name           = each.value.extra_specs.share_backend_name
        "vast:vippoolname"           = vastdata_vip_pool.vippools[each.value.extra_specs.vippoolname].name
    }
}

resource "openstack_sharedfilesystem_sharetype_access_v2" "sharetypes_access" {
    for_each = var.sharetypes_access

    share_type_id = each.value.sharetype_name != null ? openstack_sharedfilesystem_sharetype_v2.sharetypes[each.value.sharetype_name].id : each.value.share_type_id
    project_id    = each.value.project != null ? openstack_identity_project_v3.project[each.value.project].id : each.value.project_id
}
