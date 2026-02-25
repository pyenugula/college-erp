
output "cluster_endpoint" {

    description = "EKS cluster endpoint"
    value = aws_eks_cluster.eks_cluster.endpoint
  
}

output "cluster_name" {

    description = "EKS Cluster Name"
    value = aws_eks_cluster.eks_cluster.name
  
}