terraform {
  cloud {
    organization = "exaf-epfl"
    workspaces {
      name = "unite-compress-base"
    }
  }
}
