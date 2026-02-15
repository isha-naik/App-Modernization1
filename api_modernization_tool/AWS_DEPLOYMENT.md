# 🌐 AWS FREE TIER DEPLOYMENT GUIDE

Deploy your API Modernization Tool to AWS for free!

---

## 📋 Quick Comparison of Deployment Options

| Option | Cost | Effort | Performance | Best For |
|--------|------|--------|-------------|----------|
| **Streamlit Cloud** | FREE | 2 mins | Good | Quick demo |
| **EC2 (t2.micro)** | FREE 750hrs/mo | 15 mins | Good | Production |
| **Lambda** | FREE 1M calls/mo | 30 mins | Excellent | APIs |
| **Local Dev** | FREE | 1 min | Good | Development |

**Recommended for Hackathon**: **EC2** (most control and reliability)

---

## Option 1: Streamlit Cloud Deployment (EASIEST - 2 MINUTES)

### Prerequisites
- GitHub account (free)
- Streamlit Cloud account (free)

### Steps

#### 1.1 Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/api-modernization.git

# Push
git branch -M main
git push -u origin main
```

#### 1.2 Deploy on Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign in with GitHub"
3. Authenticate GitHub
4. Click "Deploy an app"
5. Select repo: `api-modernization`
6. Branch: `main`
7. File path: `app.py`
8. Click "Deploy"

**Done!** Your app is live at: `https://[your-username]-api-modernization.streamlit.app`

#### 1.3 Add Secrets (For Bedrock)

1. In Streamlit Cloud dashboard, click settings ⚙️
2. Go to "Secrets"
3. Copy contents of your `.env` file:
   ```
   AWS_REGION="us-east-1"
   USE_BEDROCK="true"
   ```
4. Save
5. App auto-updates!

---

## Option 2: EC2 Deployment (RECOMMENDED - 15 MINUTES)

### 2.1 Create EC2 Instance

**Video**: [AWS EC2 Getting Started](https://youtu.be/tDFJKPjhvt4)

Step-by-step:

1. Go to https://console.aws.amazon.com/ec2/
2. Click **"Launch instance"**
3. **Name**: `api-modernization-app`
4. **AMI**: Select "Ubuntu 22.04 LTS" 
   - (marked as "Free tier eligible")
5. **Instance type**: `t2.micro` 
   - (FREE tier eligible!)
6. **Key pair**: 
   - Click "Create new key pair"
   - Name: `api-modernization-key`
   - Type: RSA
   - Click "Create key pair"
   - **Save the .pem file to your computer**
7. **Network settings**:
   - Click "Edit"
   - Check "Allow SSH from": "Anywhere 0.0.0.0/0"
   - Check "Allow HTTP from": "Anywhere 0.0.0.0/0"
   - Check "Allow HTTPS from": "Anywhere 0.0.0.0/0"
   - **Add rule**: Custom TCP, Port 8501 (Streamlit)
8. **Storage**: 
   - 20 GB (Free tier eligible!)
9. **Summary**:
   - Should show "Free tier eligible" options only
10. Click **"Launch instance"**
11. Wait for instance to start (green status)

### 2.2 Connect to Instance

#### On Windows

1. Download PuTTY: https://www.chiark.greenend.org.uk/~sgtatham/putty/
2. Install PuTTY
3. Open PuTTYgen
4. Click "Load" → select your `.pem` file
5. Click "Save private key"
6. Open PuTTY
7. In "Host Name": `ubuntu@[instance-public-ip]`
8. In "Connection" → "SSH" → "Auth" → Browse → select `.ppk` file
9. Click "Open"

#### On Linux/Mac

```bash
# Navigate to where you saved the .pem file
cd ~/Downloads

# Set permissions
chmod 400 api-modernization-key.pem

# Connect
ssh -i "api-modernization-key.pem" ubuntu@YOUR_INSTANCE_IP
```

Get instance IP from AWS console (Public IPv4)

### 2.3 Setup Application

Once connected to the instance:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git

# Clone your repo (or upload files)
git clone https://github.com/YOUR_USERNAME/api-modernization.git
cd api-modernization

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Configure AWS (if using Bedrock)
aws configure
# Enter your AWS credentials

# Test locally
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

**Access at**: http://YOUR_INSTANCE_IP:8501

### 2.4 Run as Background Service

To keep app running even after disconnect:

```bash
# Install screen
sudo apt install -y screen

# Create new screen session
screen -S api-app

# Run app in screen
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Detach (Ctrl+A then D)
# Ctrl+A, then D

# Later, to reattach:
screen -r api-app
```

Or use **systemd** (more permanent):

```bash
# Create service file
sudo nano /etc/systemd/system/api-modernization.service
```

Paste:
```ini
[Unit]
Description=API Modernization Tool
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/api-modernization
Environment="PATH=/home/ubuntu/api-modernization/venv/bin"
ExecStart=/home/ubuntu/api-modernization/venv/bin/python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
# Save (Ctrl+X, Y, Enter)

# Enable service
sudo systemctl enable api-modernization

# Start service
sudo systemctl start api-modernization

# Check status
sudo systemctl status api-modernization
```

### 2.5 Setup Domain (Optional)

If you have a domain:

1. Go to Route 53 in AWS
2. Create hosted zone
3. Point domain to Elastic IP

or

1. Use Cloudflare (free)
2. Point to EC2 instance IP

---

## Option 3: Lambda Deployment (ADVANCED)

### Setup Lambda

```bash
# Install serverless framework
npm install -g serverless

# Install Python plugin
npm install --save-dev serverless-python-requirements serverless-wsgi

# Initialize project
serverless create --template aws-python3
```

Edit `serverless.yml`:
```yaml
service: api-modernization

provider:
  name: aws
  region: us-east-1
  runtime: python3.10

functions:
  app:
    handler: wsgi.handler
    events:
      - http: ANY {proxy+}
      - http: ANY

plugins:
  - serverless-python-requirements
  - serverless-wsgi

custom:
  wsgi:
    app: app.app
```

Deploy:
```bash
serverless deploy
```

---

### Estimated Costs

| Free Tier | Limit | Monthly Usage |
|-----------|-------|---------------|
| **EC2** | 750 hours | ~30 days × 24 hrs = 720 hours ✅ |
| **Data Transfer** | 1 GB/month | ~100MB typical usage ✅ |
| **Storage** | 20 GB EBS | 20 GB ✅ |
| **Lambda** | 1M invocations | 10K invocations max ✅ |

**You will NOT be charged if you stay within free tier!**

### Monitor Costs

1. Go to https://console.aws.amazon.com/cost-management/
2. Set up billing alerts
3. Keep free tier instances running
4. Delete if not using

---

## Troubleshooting Deployment

### Issue: SSH Connection Timeout

**Solution**:
- Check security group allows SSH (port 22)
- Check instance is running
- Check instance has public IP
- Wait 1-2 minutes after launch

### Issue: Streamlit Port Blocked

**Solution**:
- Add port 8501 to security group
- Or use different port: `--server.port 8080`
- Or put behind nginx reverse proxy

### Issue: App Crashes

**Solution**:
```bash
# SSH into instance
ssh -i "key.pem" ubuntu@IP

# Check logs
cd /home/ubuntu/api-modernization
source venv/bin/activate

# Run manually to see errors
streamlit run app.py --server.port 8501

# Check service status
sudo systemctl status api-modernization
sudo journalctl -u api-modernization -n 50
```

### Issue: Out of Memory

**Solution**:
- Upgrade to `t2.small` or `t3.micro`
- Free tier still covers 750 hours!
- Or optimize code (cache results)

---

## Best Practices

### 1. Backups

```bash
# Backup your code
git push origin main  # Always push to GitHub

# Backup EC2 instance
# Go to AWS Console → EC2 → Instances
# Right-click → Image and templates → Create image
```

### 2. Monitoring

```bash
# Monitor CPU
watch -n 1 'ec2-metadata --instance-id && vmstat'

# Monitor storage
df -h

# Monitor Streamlit logs
tail -f ~/.streamlit/logs/
```

### 3. Security

```bash
# Change SSH key permissions
chmod 400 api-modernization-key.pem

# Update system regularly
sudo apt update && sudo apt upgrade

# Use security groups (AWS firewall)
# Only allow SSH from your IP (not 0.0.0.0)
```

### 4. Cost Optimization

- Use t2.micro (free tier)
- Stop instance when not using (not terminate)
- Monitor with AWS Cost Explorer
- Set billing alerts at $1

---

## Quick Reference Commands

### Streamlit Cloud
```bash
git push origin main  # Auto-deploys
```

### EC2 (SSH)
```bash
ssh -i "key.pem" ubuntu@IP
screen -S api-app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### EC2 (SystemD Service)
```bash
sudo systemctl start api-modernization
sudo systemctl status api-modernization
sudo systemctl logs api-modernization
```

---

## Next Steps After Deployment

1. **Configure Custom Domain**
   - Buy domain ($12/year minimum)
   - Point to Elastic IP
   - Get SSL certificate (AWS Certificate Manager is free)

2. **Add Authentication**
   - Protect app with password
   - Use AWS Cognito

3. **Scale Up**
   - If hits traffic limits
   - Add ALB (Application Load Balancer)
   - Higher instance type

4. **Production Ready**
   - Add logging (CloudWatch)
   - Add monitoring (CloudWatch alarms)
   - Add backup (EBS snapshots)

---

**Deployment Complete! 🎉**

Your API Modernization tool is now live on AWS free tier!

