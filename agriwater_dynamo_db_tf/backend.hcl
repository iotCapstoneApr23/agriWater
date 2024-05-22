# backend.hcl

terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "path/to/my/state/file.tfstate"
    region         = "us-east-1"
    dynamodb_table = "my-terraform-locks"
  }
}