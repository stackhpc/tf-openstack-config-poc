terraform {
  required_providers {
    vastdata = {
      source = "vast-data/vastdata"
      version = "2.1.1"
    }
  }
}

provider "vastdata" {
  username        = try(var.vast_info.username, null)
  port            = try(var.vast_info.port, 443)
  password        = try(var.vast_info.password)
  host            = try(var.vast_info.host, null)
  skip_ssl_verify = true
}
