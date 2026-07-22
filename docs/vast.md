## Vippools

To create a vippool,

Example usage:

```console
vippools = {
    "client_manila" = {
      subnet_cidr = "24"
      network = "client_net_data:client"

      vast_tenant = "client"

      vip_ranges = [{
        subnet = "client_subnet_data:client"
        start  = 200
        end    = 249
      }]
    }

}
```

Arugment reference:
- `name` (Optional) string.
- `network` (Optional) string. Tofu resource network name.
- `vlan` (Optional) string
- `role` (Optional) string
- `subnet_cidr` (Optional) number
- `tenant_id` (Optional) string. Vast tenant id. Overriden by `vast_tenant`.
- `vast_tenant` (Optional) string. Vast tenant name. Overrides `tenant_id`.
- `vip_ranges` (Optional) list. Overriden by `ip_ranges`. Block supports:
    - `subnet` (Required) number. Tofu resource name of subnet.
    - `start` (Requied) number
    - `end` (Required) number
- `ip_ranges` (Optional) list. Overrides `vip_ranges`.


## Vast Tenants

To create a vast tenant,

Example usage:

```console
vast_tenants = {
    "testclient" = {
      allow_locked_users = true
      allow_disabled_users = true

      client_ranges = [{
        subnet = "testclient_subnet_data:testclient"
        start = 2
        end = 149
      }]
    }
}
```

Argument reference:
- `allow_locked_users` (Optional) bool
- `allow_disabled_users` (Optional) bool
- `client_ranges` (Optional) list. Overriden by `client_ip_ranges`. Block supports:
    - `subnet` (Required) string. Tofu resource name of subnet.
    - `start` (Required) number
    - `end` (Required) number
- `client_ip_ranges` (Optional) list. Overrides `client_ranges`.

## Vast host

To set the vast host set:

```console
vast_host = string
```

By default `vast_host` is set to `10.3.2.10` .

## Vast username

To set the vast username set:

```console
username = string
```

By default `username` is set to `openstack-manila` .