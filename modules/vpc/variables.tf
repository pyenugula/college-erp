variable "vpc_cidr" {
  
  default = "10.0.0.0/16"
  type = string
}

variable "availability_zones" {

    description = "Availability Zones"
    type = list(string)

}

variable "public_subnet_cidrs" {

    description = "CIDR blocks for public subnet"
    type = list(string)
  
}

variable "private_subnet_cidrs" {

    description = "CIDR blocks for private subnet"
    type = list(string)
  
}

variable "cluster_name" {

    description = "Name of the eks cluster"
    type = string
  
}
