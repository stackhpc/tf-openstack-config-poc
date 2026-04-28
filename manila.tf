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