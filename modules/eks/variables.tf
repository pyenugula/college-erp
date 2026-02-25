variable "cluster_name" {
  type        = string
  description = "The name of the EKS cluster"
  
}

variable "cluster_version"{

    type = string
    description = "Cluster version"
}


variable "vpc_id" {
  type        = string
  description = "The ID of the VPC to use for the EKS cluster"
}

variable "subnet_ids" {
  type        = list(string)
  description = "A list of subnet IDs to use for the EKS cluster"
}

variable "node_groups" {
  type        = map(object({

    instance_types=list(string)
    capacity_type=string
    scaling_config=object({
      desired_size = number
      max_size=number
      min_size=number
    })

  }))
}


