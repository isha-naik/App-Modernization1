# 🚀 API Modernization Tool - Complete Guide

**A free, AI-powered tool for modernizing your legacy Java APIs using AWS Bedrock and open-source technologies.**

Built for hackathons. Deploys on free tier AWS. No credit card required after initial setup.

---

## 📋 Table of Contents

1. [Quick Start (5 minutes)](#quick-start-5-minutes)
2. [Full Setup Guide](#full-setup-guide)
3. [Features](#features)
4. [AWS Free Tier Deployment](#aws-free-tier-deployment)
5. [Architecture](#architecture)
6. [Troubleshooting](#troubleshooting)
7. [Resources](#resources)

---

## ⚡ Quick Start (5 minutes)

### Prerequisites
- Python 3.10 or higher
- Git
- AWS Free Tier Account (optional, for Bedrock)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd api_modernization_tool

# Create virtualenv
python -m venv venv

# Activate virtualenv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Locally

```bash
# Start Streamlit app
streamlit run app.py

# App opens at http://localhost:8501
```

### 3. Upload Code & Analyze

1. Go to **"Upload Code"** tab
2. Upload a ZIP file with your Java project
3. View analysis in **"Analysis"** tab
4. Generate migration plan in **"Migration Plan"** tab
5. Export OpenAPI spec in **"OpenAPI Spec"** tab

---

## 📚 Full Setup Guide

### Step 1: Environment Setup

#### Windows

```powershell
# Install Python 3.10+ if needed
python --version  # Should be 3.10+

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Linux / macOS

```bash
# Install Python 3.10+ if needed
python3 --version  # Should be 3.10+

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure AWS (Optional but Recommended)

#### Install AWS CLI

```bash
# Windows
pip install awscli

# Linux/Mac
pip install awscli
```

#### Configure AWS Credentials

```bash
# Run configuration
aws configure

# Enter:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: us-east-1
# Default output format: json
```

**Get AWS credentials:**
1. Go to https://console.aws.amazon.com/
2. Sign into your AWS account
3. Go to **IAM → Users → Your User → Security Credentials**
4. Create access key
5. Copy Access Key ID and Secret Access Key

#### Enable Bedrock (Free Tier Model)

```bash
# In .env file, set:
USE_BEDROCK=true
AWS_REGION=us-east-1
```

### Step 3: Run Application

```bash
# Make sure virtual environment is activated
streamlit run app.py

# Open http://localhost:8501 in your browser
```

---

## ✨ Features

### 1. 📁 Code Analysis
- Parse Java source code (with/without tree-sitter)
- Extract classes, methods, fields, annotations
- Identify REST endpoints
- Build knowledge graph

### 2. 🔍 API Analysis
- Detect API style (REST, SOAP, GraphQL, RPC)
- Calculate REST maturity level (0-3)
- Analyze endpoint patterns
- Identify frameworks used

### 3. 🤖 AI-Powered Migration
- AWS Bedrock integration for intelligent recommendations
- Generate migration plans with phases
- Risk assessment
- Timeline estimation
- Framework-specific recommendations

### 4. 📋 OpenAPI Generation
- Auto-generate OpenAPI 3.1 specs
- Export as YAML or JSON
- Ready for Swagger UI, Postman, etc.

### 5. 🔗 RAG Infrastructure
- FAISS vector store for semantic search
- Local embeddings (no API keys needed)
- Graph-to-documents conversion

---

## 🚀 AWS Free Tier Deployment

### Option 1: EC2 Deployment (Recommended)

#### 1. Launch EC2 Instance

```
1. Go to https://console.aws.amazon.com/ec2/
2. Click "Launch instance"
3. Choose Ubuntu 22.04 LTS
4. Instance type: t2.micro (FREE TIER ELIGIBLE)
5. Key pair: Create new (save .pem file)
6. Security group: Allow SSH (22), HTTP (80), HTTPS (443), Custom TCP 8501
7. Storage: 20 GB (FREE TIER ELIGIBLE)
8. Launch instance
```

#### 2. Connect and Setup

```bash
# SSH into instance (replace YOUR_KEY.pem and instance IP)
ssh -i "YOUR_KEY.pem" ubuntu@<instance-public-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone <your-repo-url>
cd api_modernization_tool

# Setup virtualenv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure AWS (if using Bedrock)
aws configure  # Enter credentials
```

#### 3. Run Application

```bash
# Option A: Direct Streamlit (dev mode)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Option B: Production with Gunicorn (better)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:server

# Access at http://<instance-public-ip>:8501
```

#### 4. Set up SystemD Service (Optional, for auto-start)

```bash
# Create service file
sudo nano /etc/systemd/system/api-modernization.service

# Paste:
[Unit]
Description=API Modernization Tool
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/api_modernization_tool
ExecStart=/home/ubuntu/api_modernization_tool/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# Save (Ctrl+X, Y, Enter)

# Enable and start
sudo systemctl enable api-modernization.service
sudo systemctl start api-modernization.service
sudo systemctl status api-modernization.service
```

### Option 2: Streamlit Cloud Deployment (Easiest)

```bash
# 1. Push code to GitHub
git push origin main

# 2. Go to https://streamlit.io/cloud
# 3. Click "New app"
# 4. Connect GitHub repository
# 5. Select your repo and app.py
# 6. Copy Secrets from .env to Streamlit Secrets
# 7. Deploy (automatic!)
```

**Pros**: 
- Completely free
- Auto-deploys on git push
- Streamlit maintains infrastructure

**Cons**:
- Bedrock requires AWS credentials in secrets
- May go to sleep if inactive

### Option 3: AWS Lambda + API Gateway

For advanced users who want serverless deployment:

```bash
# 1. Install Serverless Framework
npm install -g serverless

# 2. Configure for Python + Streamlit
# 3. Deploy:
serverless deploy
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    API MODERNIZATION TOOL                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  LAYER 1: CODE PARSING                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ JavaParser (Tree-Sitter or Regex)                        │   │
│  │ Extracts: Classes, Methods, Fields, Annotations         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        ↓                                         │
│  LAYER 2: KNOWLEDGE GRAPH                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ NetworkX MultiDiGraph                                    │   │
│  │ Nodes: Classes, Methods, Fields, Endpoints              │   │
│  │ Edges: Calls, Dependencies, Accesses                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        ↓                                         │
│  LAYER 3: ANALYSIS                                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ GraphSummarizer      - Code statistics                  │   │
│  │ APIStyleDetector     - REST maturity analysis           │   │
│  │ Inference            - Framework detection              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        ↓                                         │
│  LAYER 4: RAG INFRASTRUCTURE                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ GraphToDocuments    - Convert to LangChain Docs         │   │
│  │ VectorStore Manager - FAISS + Local Embeddings          │   │
│  │ Sentence Transformers - Free embeddings                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        ↓                                         │
│  LAYER 5: AI & MIGRATION                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ BedrockLLMManager    - AWS Bedrock integration           │   │
│  │ MigrationPlanGenerator - AI-powered planning             │   │
│  │ OpenAPIGenerator     - Spec creation                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        ↓                                         │
│  LAYER 6: UI                                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Streamlit Application                                    │   │
│  │ 5 Tabs: Upload, Analysis, Plan, OpenAPI, Docs           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Upload Code
    ↓
Parse Java Files
    ├── Extract Classes/Methods/Fields
    ├── Identify Annotations
    └── Find REST Endpoints
    ↓
Build Knowledge Graph (NetworkX)
    ├── Nodes: Code elements
    ├── Edges: Relationships
    └── Stats: Counts & Analysis
    ↓
Create Analysis
    ├── GraphSummarizer → Statistical summary
    ├── APIStyleDetector → REST maturity
    └── Inference → Framework detection
    ↓
Generate RAG Index (FAISS)
    ├── Convert graph to documents
    ├── Embed with sentence-transformers
    └── Store in vector database
    ↓
Migration Planning with Bedrock
    ├── Query AI for recommendations
    ├── Generate migration steps
    └── Assess risks
    ↓
Export Results
    ├── OpenAPI Specification
    ├── Migration Plan (JSON)
    └── Analysis Report
```

---

## 🔧 Dependencies & Free Alternatives

### Core Libraries (All Free/Open Source)

| Component | Library | Why | Size |
|-----------|---------|-----|------|
| **Parsing** | tree-sitter-java | Fast, reliable | ~50MB |
| **Graph** | NetworkX | Standard, mature | ~2MB |
| **Vectorstore** | FAISS | Optimized, fast | ~100MB |
| **Embeddings** | sentence-transformers | Free, no API | ~500MB first load |
| **LLM** | AWS Bedrock | Free tier available | API-based |
| **UI** | Streamlit | Intuitive, fast | ~50MB |
| **Chain** | LangChain 0.3+ | Latest API | ~10MB |

### Total Installation Size
- **Minimal** (without tree-sitter): ~800MB
- **Full** (with everything): ~1.5GB
- **Virtual Environment**: ~2GB

---

## 🐛 Troubleshooting

### Issue: Graph Connection Error

**Problem**: `Failed to connect to AWS Bedrock`

**Solution**:
```bash
# 1. Verify AWS credentials
aws sts get-caller-identity

# 2. Ensure Bedrock is available in your region
# Bedrock available in: us-east-1, us-west-2, eu-west-1, ap-northeast-1

# 3. Disable Bedrock in .env for now
USE_BEDROCK=false

# 4. Local fallback will work
```

### Issue: No Java Classes Found

**Problem**: Parser returns 0 classes

**Solution**:
```bash
# 1. Verify Java files exist
find /path/to/code -name "*.java" | wc -l

# 2. Check file permissions
ls -la /path/to/code

# 3. Try with explicit path
streamlit run app.py

# 4. Check console for error messages
```

### Issue: Memory Error on Large Codebase

**Problem**: `MemoryError` when processing 1000+ classes

**Solution**:
```python
# In app.py, add chunking:
chunk_size = 100  # Process in batches
for i in range(0, len(java_files), chunk_size):
    batch = java_files[i:i+chunk_size]
    parser.parse_files(batch, kg)
```

### Issue: Streamlit Slow on Remote Server

**Problem**: App loads slowly on EC2

**Solution**:
```bash
# 1. Increase memory
# Use t2.small or t3.small instead of t2.micro

# 2. Enable caching
streamlit run app.py --logger.level=warning

# 3. Use CDN for static files
# Put large files in S3
```

---

## 📖 Resources

### Official Documentation
- [LangChain 0.3 Docs](https://python.langchain.com/docs/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)

### AWS Tutorials
- [AWS Free Tier Eligibility](https://aws.amazon.com/free/)
- [EC2 Getting Started](https://docs.aws.amazon.com/ec2/index.html)
- [Bedrock Getting Started](https://aws.amazon.com/bedrock/getting-started/)
- [IAM Console](https://console.aws.amazon.com/iam/)

### Learning Resources
- [REST API Best Practices](https://restfulapi.net/)
- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Spring Boot 3 Migration Guide](https://spring.io/blog/2022/05/24/preparing-for-spring-boot-3-0)
- [Tree-Sitter Play Playground](https://tree-sitter.github.io/tree-sitter/playground)

### Python Packages
- [sentence-transformers PyPI](https://pypi.org/project/sentence-transformers/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [FAISS PyPI](https://pypi.org/project/faiss-cpu/)

---

## 🎯 Common Use Cases

### 1. Modernize Struts to Spring Boot

```
1. Upload Struts project
2. Analysis shows: Legacy RPC patterns
3. Migration plan suggests:
   - Replace ActionSupport with @RestController
   - Map Action methods to handler methods
   - Convert ValueStack to ResponseEntity
4. Generate OpenAPI spec for new API
5. Export migration plan for development team
```

### 2. Assess REST Maturity

```
1. Upload Spring project
2. Check REST maturity level
3. Get recommendations:
   - Level 1→2: Add proper HTTP methods
   - Level 2→3: Implement HATEOAS
4. Prioritize improvements
```

### 3. Framework Evaluation

```
1. Upload legacy Java codebase
2. Let AI recommend best target:
   - Spring Boot 3 (safe, well-known)
   - Quarkus (cloud-native, fast)
   - Jakarta EE (enterprise)
3. Get detailed comparison in migration plan
4. Make informed decision
```

---

## 📝 License & Credits

**Built with**: Python, LangChain, Streamlit, AWS Bedrock, FAISS, Tree-Sitter

**Open Source**: Feel free to fork, modify, and use for your projects

**For Hackathons**: This tool is specifically designed to run on free tier AWS resources

---

## 🤝 Contributing

Want to improve this tool?

```bash
# 1. Fork repository
# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes
# 4. Test locally
streamlit run app.py

# 5. Push and create PR
git push origin feature/your-feature
```

### Areas for Contribution
- Support for other languages (Python, C#, Go)
- Additional framework support
- Enhanced OpenAPI generation
- Performance optimizations
- Better error handling
- UI/UX improvements

---

## 📧 Support

Having issues?

1. Check [Troubleshooting](#troubleshooting) section
2. Review [AWS Free Tier Docs](https://aws.amazon.com/free/)
3. Check internet connection and AWS credentials
4. Post issue on GitHub

---

**Happy Modernizing! 🚀**

**Last Updated**: February 2026
**Version**: 1.0.0
