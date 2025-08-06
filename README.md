A full‑stack web application for podcast content, running in Docker containers and deployed on AWS EC2.  
Frontend is served via an Nginx reverse proxy with HTTPS enabled via Certbot.

**Live Site:** [https://www.podifynews.com](https://www.podifynews.com)


## Tech Stack
- **Frontend**: React
- **Backend**: FASTAPI (AWS Polly, DynamoDB, S3)
- **Authentication**: Auth0 JWT
- **Deployment**: Docker Compose on AWS EC2
- **Reverse Proxy**: Nginx
- **SSL/TLS**: Certbot (Let's Encrypt)
- **Cloud Deployment**: AWS (EC2, VPC, Subnets, Security Groups, Internet Gateway, Route Tables, ACM Certificates,          Application Load Balancer, Target Groups, Listener Rules)
-**Infrastructure as Code**: Terraform
-**Load Balancing**: AWS Application Load Balancer (ALB) with HTTPS and path-based routing
-**Domain and DNS**: Custom domain via Route53 