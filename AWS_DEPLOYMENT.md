# AWS Elastic Beanstalk Deployment Guide

## Prerequisites
1. AWS Account with Free Tier eligible
2. AWS CLI installed
3. EB CLI installed

## Installation

### 1. Install AWS CLI
```bash
# Windows (using MSI installer)
Download from: https://awscli.amazonaws.com/AWSCLIV2.msi

# Or via pip
pip install awscli
```

### 2. Install EB CLI
```bash
pip install awsebcli
```

### 3. Configure AWS Credentials
```bash
aws configure
# Enter:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1 (or your preferred region)
# - Default output format: json
```

## Backend Deployment (Elastic Beanstalk)

### 1. Initialize Elastic Beanstalk
```bash
cd c:/Users/jesse/cgmd
eb init

# Choose:
# - Region: us-east-1 (or your preferred)
# - Application name: cgmd-backend
# - Platform: Python 3.12
# - CodeCommit: No
# - SSH: Yes (for debugging)
```

### 2. Create Environment
```bash
eb create cgmd-production

# This will:
# - Create an EC2 instance (t3.micro - FREE tier)
# - Install Python 3.12
# - Install dependencies from requirements.txt
# - Run migrations
# - Collect static files
```

### 3. Set Environment Variables
```bash
eb setenv \
  SECRET_KEY="your-secret-key-here-generate-a-new-one" \
  DEBUG=False \
  ALLOWED_HOSTS=".elasticbeanstalk.com" \
  DATABASE_URL="postgresql://postgres.yosugfmarodnempvvbru:YOUR-PASSWORD@aws-0-us-west-2.pooler.supabase.com:5432/postgres" \
  CORS_ALLOWED_ORIGINS="https://your-cloudfront-url.cloudfront.net"
```

### 4. Deploy
```bash
eb deploy
```

### 5. Get Backend URL
```bash
eb status
# Look for "CNAME" - this is your backend URL
# Example: cgmd-production.us-east-1.elasticbeanstalk.com
```

## Frontend Deployment (S3 + CloudFront)

### 1. Build Frontend
```bash
cd frontend
npm install
npm run build
```

### 2. Create S3 Bucket
```bash
# Replace 'your-unique-bucket-name' with something unique
aws s3 mb s3://cgmd-frontend-bucket --region us-east-1

# Enable static website hosting
aws s3 website s3://cgmd-frontend-bucket --index-document index.html --error-document index.html
```

### 3. Configure Bucket Policy (Public Access)
Create a file `s3-policy.json`:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::cgmd-frontend-bucket/*"
    }
  ]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy --bucket cgmd-frontend-bucket --policy file://s3-policy.json
```

### 4. Upload Frontend Files
```bash
aws s3 sync frontend/dist/ s3://cgmd-frontend-bucket --delete
```

### 5. Create CloudFront Distribution (CDN)
```bash
aws cloudfront create-distribution \
  --origin-domain-name cgmd-frontend-bucket.s3.amazonaws.com \
  --default-root-object index.html
```

Or create via AWS Console:
1. Go to CloudFront console
2. Create Distribution
3. Origin: Your S3 bucket
4. Default root object: `index.html`
5. Error pages: Add custom error response for 404 → /index.html (for React routing)

### 6. Update Frontend Environment Variable
Update `frontend/.env.production`:
```
VITE_API_URL=https://cgmd-production.us-east-1.elasticbeanstalk.com/api
```

Rebuild and redeploy:
```bash
npm run build
aws s3 sync frontend/dist/ s3://cgmd-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR-DIST-ID --paths "/*"
```

## Useful Commands

### Backend (EB)
```bash
eb status                  # Check environment status
eb logs                    # View logs
eb ssh                     # SSH into instance
eb deploy                  # Deploy new version
eb setenv KEY=value        # Set environment variable
eb open                    # Open app in browser
eb terminate              # Delete environment (careful!)
```

### Frontend (S3)
```bash
# Sync new files
aws s3 sync frontend/dist/ s3://cgmd-frontend-bucket --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id DIST-ID --paths "/*"
```

## Cost Estimate
- **EB t3.micro**: FREE (first year) → $8-10/month
- **S3**: ~$0.50/month (for storage)
- **CloudFront**: ~$1/month (first 1TB free)
- **Data Transfer**: Included in free tier
- **Total**: FREE first year, then ~$10/month

## Monitoring
- EB Health: `eb health`
- CloudWatch Logs: AWS Console → CloudWatch
- S3 Usage: AWS Console → S3 → Metrics

## Troubleshooting
```bash
# View recent logs
eb logs --stream

# SSH into instance
eb ssh

# Check Django logs
sudo cat /var/log/eb-engine.log
sudo cat /var/log/web.stdout.log
```

## Production Checklist
- [ ] SECRET_KEY set (new, random value)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS configured
- [ ] DATABASE_URL points to Supabase
- [ ] CORS_ALLOWED_ORIGINS includes CloudFront URL
- [ ] Frontend VITE_API_URL points to EB backend
- [ ] SSL/HTTPS enabled (EB provides this automatically)
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] CloudFront error pages configured for SPA routing
