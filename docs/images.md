## Images

To create an image,

Example usage:

```console
images = {
    "Ubuntu-24.04-20260323-noble-server-cloudimg-amd64" = {
      image_source_url = "https://cloud-images.ubuntu.com/noble/20260323/noble-server-cloudimg-amd64.img"
      container_format = "bare"
      disk_format      = "qcow2"
    }
}
```

Argument reference:
- `container_format` (Required) string. Must be one of "bare", "ovf", "aki", "ari", "ami", "ova", "docker", "compressed".
- `disk_format` (Required) string. Must be one of "raw", "vhd", "vhdx", "vmdk", "vdi", "iso", "ploop", "qcow2", "aki", "ari", "ami".
- `image_cache_path` (Optional) string.
- `image_source_url` (Optional) string.
- `image_id` (Optional) string.
- `min_disk_gb` (Optional) number, default 0.
- `min_ram_mb` (Optional) number, default 0.
- `protected` (Optional) bool, default false.
- `hidden` (Optional) bool, default false.
- `web_download` (Optional) bool, default false.
- `properties` (Optional) list of strings.
- `visibility` (Optional) string.
