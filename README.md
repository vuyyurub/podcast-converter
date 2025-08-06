A full‑stack web application for converting articles to podcasts for anytime listen, deployed on AWS EC2 with HTTPS enabled via Nginx and Certbot.  

**Live Site:** [https://www.podifynews.com](https://www.podifynews.com)


## Tech Stack  

### Frontend  
- **Framework**: React  
- **Reverse Proxy**: Nginx  
- **SSL/TLS**: Certbot (Let's Encrypt)  

### Backend  
- **Framework**: FastAPI  
- **AWS Services**:  
  - **Text-to-Speech**: AWS Polly  
  - **Database**: DynamoDB  
  - **Storage**: S3  

### Authentication  
- **Auth Provider**: Auth0 (JWT-based authentication)  

### Deployment & Infrastructure  
- **Containerization**: Docker (Docker Compose)  
- **Cloud Platform**: AWS  
  - **Compute**: EC2  
  - **Networking**: VPC, Subnets, Security Groups, Internet Gateway, Route Tables  
  - **Certificate Management**: ACM (AWS Certificate Manager)  
  - **Load Balancing**: Application Load Balancer (ALB) with HTTPS & path-based routing  
  - **DNS & Domain**: Route53 (Custom domain)  
- **Infrastructure as Code (IaC)**: Terraform  