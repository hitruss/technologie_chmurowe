terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

provider "docker" {}

resource "docker_image" "ubuntu" {
  name = "ubuntu:22.04"
}

resource "docker_container" "ubuntu_vm" {
  name  = "ubuntu-container"
  image = docker_image.ubuntu.image_id

  tty   = true
  stdin_open = true
}