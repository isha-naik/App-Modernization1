# 🎯 QUICK START FOR NOOBS

**Start to finish: 10 minutes on Windows, Linux, or Mac**

---

## What You'll Need

✅ Computer with Windows/Mac/Linux
✅ Internet connection
✅ Free AWS account (optional but recommended)
✅ **That's it!**

---

## Video: Visual Guide

If you prefer video, watch this (5 min guide on YouTube):
[Search: "Python Streamlit setup 2025"]

---

## STEP 1: Download Python (2 Minutes)

### On Windows
1. Go: https://www.python.org/downloads/
2. Click big **"Download Python 3.11"** button
3. Run the installer
4. **MOST IMPORTANT**: Check the box "Add Python to PATH"
5. Click "Install Now"
6. Wait...Done!

### On Mac
1. Go: https://www.python.org/downloads/
2. Click **"Download Python 3.11"**
3. Run .pkg file
4. Follow setup wizard
5. Done!

### On Linux
```bash
sudo apt install python3 python3-venv python3-pip -y
```

---

## STEP 2: Get the Code (2 Minutes)

### EASIEST: Download ZIP

1. Go to GitHub page
2. Click **"Code"** (green button)
3. Click **"Download ZIP"**
4. Extract to `C:\Users\YourName\api-modernization` (Windows)
5. Or `~/api-modernization` (Mac/Linux)

### OR: Use Git

```bash
git clone <repo-url>
cd api-modernization
```

---

## STEP 3: Setup (3 Minutes)

### On Windows (Command Prompt)

```bash
cd C:\Users\YourName\api-modernization

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

### On Mac/Linux (Terminal)

```bash
cd ~/api-modernization

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

**Wait for installation (might take 2-3 minutes)**

---

## STEP 4: Run! (1 Minute)

```bash
streamlit run app.py
```

**Opens automatically in browser at http://localhost:8501**

---

## STEP 5: Use the App (2 Minutes)

### Upload Code:
1. Click "📁 Upload Code" tab
2. Upload ZIP of Java project OR enter directory path
3. Wait for "✅ Code analyzed successfully!"

### See Analysis:
1. Click "📊 Analysis" tab
2. See: Classes, Methods, REST endpoints detected
3. See REST maturity level (0-3)

### Generate Plan:
1. Click "🤖 Migration Plan" tab
2. Select target framework
3. Click "Generate Migration Plan"
4. Read AI recommendations!

### Get OpenAPI Spec:
1. Click "📋 OpenAPI Spec" tab
2. Generate spec
3. Download as YAML/JSON

---

## Optional: Use AWS Bedrock (For AI)

### Get AWS Account

1. Go: https://aws.amazon.com/free
2. Click "Create Free Account"
3. Enter email, password
4. Add payment method (won't charge)

### Configure AWS

```bash
pip install awscli

aws configure
# Enter Access Key ID, Secret Access Key, region (us-east-1)
```

### Enable in App

Edit `.env` file:
```
USE_BEDROCK=true
```

---

## Troubleshooting

### Python doesn't work?
```bash
# Try full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe --version
```

### streamlit command not found?
```bash
# Make sure venv is activated (see (venv) in prompt)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Port 8501 in use?
```bash
streamlit run app.py --server.port 8502
```

---

## Next: Deploy to AWS

Want to share your app with others?

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy"
git push

# 2. Go to Streamlit Cloud: https://streamlit.io/cloud
# 3. Connect GitHub, select repo
# 4. Boom! Live online!
```

Or see `AWS_DEPLOYMENT.md` for EC2 deployment.

---

## Support

Lost? Check these files:
- `README.md` - Full documentation
- `GETTING_STARTED.md` - Detailed setup
- `AWS_DEPLOYMENT.md` - Deploy online

---

**You're done! 🎉**

Check out the tabs and try uploading your first Java project!
