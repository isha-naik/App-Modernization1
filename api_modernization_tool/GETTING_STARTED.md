# 🚀 GETTING STARTED - Complete Setup

## For Complete Beginners

This guide walks you through everything step-by-step.

---

## Step 1: Install Prerequisites (5 minutes)

### Windows

#### 1.1 Install Python

1. Go to https://www.python.org/downloads/
2. Click "Download Python 3.11" (or latest 3.10+)
3. Run installer
4. **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"
6. Wait for completion

#### 1.2 Install Git (for cloning repo)

1. Go to https://git-scm.com/download/win
2. Click "Click here to download"
3. Run installer, accept all defaults
4. Click "Finish"

#### 1.3 Verify Installation

Open Command Prompt (Win+R, type `cmd`, Enter):

```bash
python --version
# Should show Python 3.10 or higher

git --version
# Should show git version
```

### Linux (Ubuntu/Debian)

```bash
# Update package manager
sudo apt update

# Install Python
sudo apt install -y python3 python3-venv python3-pip

# Install Git
sudo apt install -y git

# Verify
python3 --version
git --version
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Install Git
brew install git

# Verify
python3 --version
git --version
```

---

## Step 2: Get the Code (2 minutes)

### Option A: Download ZIP (Easiest for beginners)

1. Go to project repository
2. Click "Code" → "Download ZIP"
3. Extract to a folder (e.g., `C:\Users\YourName\Projects\api-modernization`)

### Option B: Clone with Git

Open Command Prompt/Terminal:

```bash
# Navigate to where you want the project
cd Desktop
# or
cd Documents

# Clone the repository
git clone <repository-url>
cd api_modernization_tool
```

---

## Step 3: Create Virtual Environment (2 minutes)

### Windows

```bash
# Navigate to project folder
cd path/to/api_modernization_tool

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) at start of command prompt
```

### Linux / macOS

```bash
# Navigate to project folder
cd path/to/api_modernization_tool

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) at start of prompt
```

---

## Step 4: Install Dependencies (5 minutes)

Make sure you're in the project folder and virtual environment is activated:

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# This will download and install ~1.5 GB of libraries
# Be patient, it may take several minutes
```

**If you get errors**, try:
```bash
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

---

## Step 5: Configure AWS (Optional but Recommended)

If you want to use AWS Bedrock for AI recommendations:

### 5.1 Create AWS Free Tier Account

1. Go to https://aws.amazon.com/free
2. Click "Create a free account"
3. Enter email, password, account name
4. Add payment method (won't be charged for free tier)
5. Complete identity verification

### 5.2 Get AWS Credentials

1. Log into AWS Console: https://console.aws.amazon.com
2. Go to **IAM** (Identity and Access Management)
3. Click **Users** → Your username
4. Go to **Security Credentials** tab
5. Under "Access keys", click **"Create access key"**
6. Select "Command Line Interface"
7. Click **"Create access key"**
8. **Save the Access Key ID and Secret Access Key** (you won't see them again!)

### 5.3 Configure AWS CLI

```bash
# Run configuration
aws configure

# Enter when prompted:
# AWS Access Key ID: [your-access-key-id]
# AWS Secret Access Key: [your-secret-access-key]
# Default region name: us-east-1
# Default output format: json
```

### 5.4 Enable Bedrock

Edit `.env` file in project folder:

```bash
# Find this line:
USE_BEDROCK=false

# Change to:
USE_BEDROCK=true

# AWS_REGION=us-east-1 (leave as is)
```

---

## Step 6: Run the Application (1 minute)

Make sure:
1. ✅ You're in the project folder
2. ✅ Virtual environment is activated (see `(venv)` in prompt)

Then run:

```bash
streamlit run app.py
```

**Expected output:**

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501

  For better performance, install pyarrow: pip install --upgrade pyarrow
```

The app will open automatically in your browser. If not, open: http://localhost:8501

---

## Step 7: Test the Application (5 minutes)

### 7.1 Create a Test Java Project

Create a simple test file to make sure everything works:

```java
// Save as: test_project/UserController.java

package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public String getAllUsers() {
        return "Users list";
    }
    
    @GetMapping("/{id}")
    public String getUser(@PathVariable Long id) {
        return "User: " + id;
    }
    
    @PostMapping
    public String createUser() {
        return "User created";
    }
}
```

### 7.2 Upload to App

1. Go to **"Upload Code"** tab in Streamlit
2. Choose "Local Directory Path"
3. Enter path: `test_project` (or full path like `C:/Users/YourName/test_project`)
4. Click "🔍 Analyze Directory"
5. Should show: 1 class, 3 methods, 3 endpoints ✅

### 7.3 View Analysis

1. Go to **"Analysis"** tab
2. Should see:
   - API Style: REST ✅
   - REST Maturity Level: 1 (Resources) ✅
   - 1 class found ✅

### 7.4 Generate Migration Plan

1. Go to **"Migration Plan"** tab
2. Select: Spring 3 → Spring Boot 3
3. Click "🤖 Generate Migration Plan"
4. Should see recommendations ✅

---

## Troubleshooting Beginner Issues

### Issue: "Python not recognized"

**Solution**: Python not in PATH
```bash
# Try with full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe --version

# Or reinstall Python and CHECK "Add Python to PATH"
```

### Issue: "ModuleNotFoundError: No module named 'streamlit'"

**Solution**: Virtual environment not activated
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Then try again
streamlit run app.py
```

### Issue: "Port 8501 is already in use"

**Solution**: Another Streamlit is running
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Issue: Connection to Bedrock failed

**Solution**: AWS not configured
```bash
# Either:
# 1. Configure AWS:
aws configure

# 2. Or disable Bedrock in .env:
# USE_BEDROCK=false
```

---

## Next Steps

### For Hackathon Submission

1. **Prepare Sample Code**
   - ZIP a real Java project
   - Test analysis works
   - Save migration plan

2. **Deploy to AWS** (optional but cool!)
   - See main README.md for EC2 deployment
   - Takes 10-15 minutes
   - Access from anywhere

3. **Create Demo**
   - Record 2-3 minute screen recording
   - Show: Upload → Analysis → Plan
   - Mention AI recommendations from Bedrock

### For Production Use

1. **Add Your Own Code**
   - Modify migration knowledge base
   - Add custom framework support
   - Enhance OpenAPI generation

2. **Deploy to AWS**
   - Lambda + API Gateway (serverless)
   - EC2 (traditional)
   - Streamlit Cloud (easiest)

3. **Customize**
   - Add your favicon/branding
   - Modify UI colors
   - Add more analysis modules

---

## Important Notes

### Keep Track of These

After AWS setup, you'll have:
- **AWS Access Key ID** → Keep safe
- **AWS Secret Access Key** → Keep safe
- **Region**: us-east-1

These are in `~/.aws/credentials` file

### Common Commands

```bash
# Start app
streamlit run app.py

# Stop app
# Press Ctrl+C in terminal

# Deactivate virtual environment
deactivate

# Reactivate
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Update dependencies
pip install --upgrade -r requirements.txt
```

### Free Tier Limits (Important!)

- **Bedrock**: Free tier available
- **EC2**: 750 hours/month free
- **Data Transfer**: 1 GB/month free
- **S3**: 5 GB free tier

Monitor your usage at: https://console.aws.amazon.com/cost-management

---

## Success Checklist

✅ Python installed and version 3.10+
✅ Git installed
✅ Project cloned/extracted
✅ Virtual environment created and activated
✅ Dependencies installed (pip install -r requirements.txt)
✅ App runs (streamlit run app.py)
✅ Browser opens to http://localhost:8501
✅ Can upload test Java code
✅ Analysis shows results
✅ AWS configured (optional)
✅ Bedrock enabled (optional)

**If all checked, you're ready to go! 🎉**

---

## Need Help?

1. Check README.md for detailed documentation
2. Check Troubleshooting section in README
3. Read code comments in src/ folder
4. Check migration knowledge files for examples

**Good luck with your hackathon! 🚀**
