## Networking config

Note that:

- Networks (and their subnets) and routers do not necessarily have to be associated with a project. If they are this association can be made with the project's name (if the project is controllled by this config) or by a project/tenant id from OpenStack (if it is not).
- The names in OpenStack for networks, subnets and routers are not necessarily unique across projects. Therefore these resources have a tofu resource name which must be unique across projects, which can be used to refer to them for other resources. It is suggested that a convention of using $NAME:$PROJECT_NAME is used.


## Networks

To create a network,

Example usage:

```console
network = {
    "client_net_data:client" = {
      name = "client-net-data"
      project = "client"
      admin_state_up = true
      external = false
      mtu = 9000
      port_security_enabled = false

      segments = [{
        network_type = "vlan"
        physical_network = "physnet1"
      }]

      subnets = {
        "client_subnet_data:client" = {
            name = "client-subnet-data"
            ip_version = 4
            no_gateway = true

            #project-nets
            subnetpool_id = "..."
            prefix_length = 24
        }
      }
    }
}
```

Argument reference:
- `name` (Required) string.
- `region` (Optional) string. Changing this creates a new network.
- `shared` (Optional) bool, default false.
- `external` (Optional) bool, default false.
- `admin_state_up` (Optional) bool, default false.
- `project` (Optional) string. Project name, overrides `tenant_id`. Changing this creates a new network.
- `tenant_id` (Optional) string. Openstack project id, overriden by `project`. Changing this creates a new network.
- `mtu` (Optional) number.
- `port_sercuirty_enabled` (Optional) bool, default false.
- `tags` (Optional) list.
- `segments` (Optional) list of objects, block supports:
    - `physical_network` (Optional) string.
    - `network_type` (Optonal) string.
    - `segmentation_id` (Optional) string.
- `subnets` (Optional) list of maps, block supports:
    - `key` (Required) string.
    - `name` (Required) string.
    - `region` (Optional) string. Changing this creates a new subnet.
    - `cidr` (Optional) string. Can omit option if creating subnet from a subnet pool (using `subnetpool_id` ).
    - `ip_version` (Optional) number, default 4. Changing this creates a new subnet.
    - `gateway_ip` (Optional) string.
    - `enable_dhcp` (Optional) bool, default true.
    - `dns_nameserver` (Optional) list.
    - `dns_publish_fixed_ips` (Optional) bool, default false.
    - `service_type` (Optional) list
    - `subnetpool_id` (Optional) string
    - `prefix_length` (Optional) number
    - `no_gateway` (Optional) bool
    - `tags` (Optional) list
    - `allocation_pool` (Optional) list, block supports:
        - `start` (Required) string.
        - `end` (Required) string.


## Routers

To create a router,

Example usage:

```console
routers = {
    "internal:admin" = {
        name                = "internal"
        external_network    = "internal-net:admin" # tofu resource name of network
        project             = "admin"

        external_fixed_ips  = [
            { subnet = "internal-net:admin" }
        ]

        interfaces = [
            { subnet = "internal-net:admin" }
        ]
    }
}
```

Arguments referenece:
- `name` (Required) string. Openstack router name.
- `region` (Optional) string. Changing this creates a new router.
- `external_network` (Optional) string. Tofu resource name of network.
- `external_network_id` (Optional) string. Openstack network id.
- `admin_state_up` (Optional) bool.
- `project` (Optional) string. Project name, overrides `tenant_id`. Changing this creates a new router.
- `tenant_id` (Optional) string. Openstack project id, overriden by `project`. Changing this creates a new router.
- `tags` (Optional) list.
- `external_fixed_ip` (Optional) list of maps, block supports:
    - `subnet` (Optional) string. Tofu resource name of subnet.
    - `subnet_id` (Optional) string. Openstack subnet id.
    - `ip_address` (Optional) string.
- `interfaces` (Optional) list of maps, block supports:
    - `region` (Optional) string. Changing this creates a new router interface.
    - `subnet` (Optional) string. Tofu resource name of subnet, overrides `subnet_id`. Changing this creates a new router interface.
    - `subnet_id` (Optional) string. Openstack subnet id, overriden by `subnet`. Changing this creates a new router interface.
    - `port_id` (Optional) string. Openstack port id. Changing this creates a new router interface.
    - `force_destroy` (Optional) bool, default false.

## Network RBAC
To create a network RBAC (role based access control),

Example usage:

```console
network_rbac = {

}
```

Argument reference:
- `network` (Required) string. Changing this creates a new routing entry.
- `projects` (Required) list of strings. Project names.
- `access` (Required) string. Valid values are either `access_as_external` or `access_as_shared`.

