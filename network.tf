resource "openstack_networking_network_v2" "networks" {
    for_each = var.networks

    name                  = each.key
    region                = lookup(each.value, "region", null)
    shared                = lookup(each.value, "shared", false)
    external              = lookup(each.value, "external", false)
    admin_state_up        = lookup(each.value, "admin_state_up", false)
    tenant_id             = lookup(each.value, "tenant_id", null)
    mtu                   = lookup(each.value, "mtu", null)
    port_security_enabled = lookup(each.value, "port_security_enabled", true)
    tags                  = lookup(each.value, "tags", [])

    dynamic "segments" {
        for_each = lookup(each.value, "segments", [])
        content {
            physical_network = lookup(segments.value, "physical_network", null)
            network_type     = lookup(segments.value, "network_type", null)
            segmentation_id  = lookup(segments.value, "segmentation_id", null)
        }
    }
}

resource "openstack_networking_subnet_v2" "subnets" {
    for_each = var.subnets

    name                 = each.key
    network_id           = each.value.network_id
    region               = lookup(each.value, "region", null)
    cidr                 = lookup(each.value, "cidr", null)
    ip_version           = lookup(each.value, "ip_version", 4) #default can be 4 or 6
    tenant_id            = lookup(each.value, "tenant_id", null)
    gateway_ip           = lookup(each.value, "gateway_ip", null)
    enable_dhcp          = lookup(each.value, "enable_dhcp", true)
    dns_nameservers      = lookup(each.value, "dns_nameservers", [])
    dns_publish_fixed_ip = lookup(each.value, "dns_publish_fixed_ip", false)
    service_types        = lookup(each.value, "service_types", [])
    subnetpool_id        = lookup(each.value, "subnetpool_id", null)
    no_gateway           = lookup(each.value, "no_gateway", null)
    tags                 = lookup(each.value, "tags", [])

    dynamic "allocation_pool" {
        for_each = lookup(each.value, "allocation_pool", [])
        content {
            start = allocation_pool.value.start
            end   = allocation_pool.value.end
        }
    }
}

resource "openstack_networking_router_v2" "routers" {
    for_each = var.routers

    name                = each.key
    region              = lookup(each.value, "region", null)
    external_network_id = lookup(each.value, "external_network_id", null)
    admin_state_up      = lookup(each.value, "admin_state_up", false)
    tenant_id           = lookup(each.value, "tenant_id", null)
    tags                = lookup(each.value, "tags", [])

    dynamic "external_fixed_ip" {
        for_each = lookup(each.value, "external_fixed_ip", [])
        content {
            subnet_id = lookup(external_fixed_ip.value, "subnet_id", null)
            ip_address = lookup(external_fixed_ip.value, "ip_address", null)
        }
    }
}

resource "openstack_networking_router_interface_v2" "router_interfaces" {
    for_each = var.router_interfaces

    router_id     = each.value.router_id
    region        = lookup(each.value, "region", null)
    subnet_id     = lookup(each.value, "subnet_id", null)
    port_id       = lookup(each.value, "port_id", null)
    force_destroy = lookup(each.value, "force_destroy", false)
}

resource "openstack_networking_network_v2" "portal_internals" {
    for_each = var.portal_internals

    tenant_id             = each.key
    name                  = each.value.name
    region                = lookup(each.value, "region", null)
    shared                = lookup(each.value, "shared", false)
    external              = lookup(each.value, "external", false)
    admin_state_up        = lookup(each.value, "admin_state_up", false)
    mtu                   = lookup(each.value, "mtu", null)
    port_security_enabled = lookup(each.value, "port_security_enabled", true)
    tags                  = lookup(each.value, "tags", [])

    dynamic "segments" {
        for_each = lookup(each.value, "segments", [])
        content {
            physical_network = lookup(segments.value, "physical_network", null)
            network_type     = lookup(segments.value, "network_type", null)
            segmentation_id  = lookup(segments.value, "segmentation_id", null)
        }
    }
}