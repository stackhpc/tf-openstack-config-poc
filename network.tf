resource "openstack_networking_network_v2" "network" {
    for_each = var.networks

    name                  = each.key
    region                = lookup(each.value, "region", null)
    shared                = lookup(each.value, "shared", false)
    external              = lookup(each.value, "external", false)
    tenant_id             = lookup(each.value, "tenant_id", null)
    mtu                   = lookup(each.value, "mtu", null)
    port_security_enabled = lookup(each.value, "port_security_enabled", true)

    dynamic "segments" {
        for_each = lookup(each.value, "segments", [])
        content {
            physical_network = lookup(segments.value, "physical_network", null)
            network_type     = lookup(segments.value, "network_type", null)
            segmentation_id  = lookup(segments.value, "segmentation_id", null)
        }
    }
}

resource "openstack_networking_subnet_v2" "subnet" {
    for_each = var.subnets

    name            = each.key
    network_id      = each.value.network_id
    region          = lookup(each.value, "region", null)
    cidr            = lookup(each.value, "cidr", null)
    ip_version      = lookup(each.value, "ip_version", 4) #default can be 4 or 6
    tenant_id       = lookup(each.value, "tenant_id", null)
    gateway_ip      = lookup(each.value, "gateway_ip", null)
    enable_dhcp     = lookup(each.value, "enable_dhcp", true)

    dynamic "allocation_pool" {
        for_each = lookup(each.value, "allocation_pool", [])
        content {
            start = allocation_pool.value.start
            end   = allocation_pool.validation.end
        }
    }
}

resource "openstack_networking_router_v2" "router" {
    for_each = var.routers

    name                = each.key
    region              = lookup(each.value, "region", null)
    external_network_id = lookup(each.value, "external_network_id", null)
    tenant_id           = lookup(each.value, "tenant_id", null)

    dynamic "external_fixed_ip" {
        for_each = lookup(each.value, "external_fixed_ip")
        content {
            subnet_id = lookup(external_fixed_ip.value, "subnet_id", null)
            ip_address = lookup(external_fixed_ip.value, "ip_address", null)
        }
    }
}

resource "openstack_networking_router_interface_v2" "router_interface" {
    for_each = var.router_interfaces

    router_id     = each.value.router_id
    region        = lookup(each.value, "region", null)
    subnet_id     = lookup(each.value, "subnet_id", null)
    port_id       = lookup(each.value, "port_id", null)
    force_destroy = lookup(each.value, "force_destroy", false)
}