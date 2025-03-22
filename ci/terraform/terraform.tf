terraform {
  backend "s3" {
    bucket = "linqqq"
    key    = "ci/terraform.tfstate"
    region = "us-east-1"
  }
}
