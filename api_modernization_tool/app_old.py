"""Main Streamlit Application for API Modernization"""
import streamlit as st
import json
from pathlib import Path
from src.knowledge_graph.graph import KnowledgeGraph
from src.parser.java_parser import GenericJavaParser
from src.rag.vectorstore import GraphToDocuments, VectorStoreManager, convert_graph_to_documents
from src.inference.api_detector import APIStyleDetector, GraphSummarizer
from src.migration.migration_engine import MigrationPlanGenerator, OpenAPIGenerator
from src.utils.config import Config

# Configure page
st.set_page_config(
    page_title="API Modernization Tool",
    page_icon="🚀",
    layout="wide"
)

# Initialize config
Config.init_folders()

# Session state initialization
if 'kg' not in st.session_state:
    st.session_state.kg = None
if 'migration_plan' not in st.session_state:
    st.session_state.migration_plan = None
if 'openapi_spec' not in st.session_state:
    st.session_state.openapi_spec = None

# Header
st.markdown("""
# 🚀 API Modernization Tool

Transform your legacy APIs into modern, cloud-native REST services using AI-powered analysis.

**Free tier AWS deployment with AWS Bedrock for intelligent recommendations.**
""")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📁 Upload Code",
    "📊 Analysis",
    "🤖 Migration Plan",
    "📋 OpenAPI Spec",
    "📚 Documentation"
])

# ============================================================================
# TAB 1: Upload Code
# ============================================================================
with tab1:
    st.header("Step 1: Upload Your Java Code")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### How to use:
        1. **Upload** a ZIP file containing your Java project
        2. or **Enter** a local directory path
        3. The tool will analyze all `.java` files
        
        ### What we analyze:
        - REST API endpoints
        - Framework patterns
        - Code structure
        - API maturity level
        """)
    
    with col2:
        upload_option = st.radio("Choose upload method:", 
                                 ["Upload ZIP", "Local Directory Path"])
        
        if upload_option == "Upload ZIP":
            uploaded_file = st.file_uploader(
                "Choose a ZIP file",
                type="zip",
                help="Upload a ZIP containing your Java source code"
            )
            
            if uploaded_file:
                import zipfile
                import tempfile
                
                with st.spinner("Extracting and analyzing..."):
                    with tempfile.TemporaryDirectory() as tmpdir:
                        with zipfile.ZipFile(uploaded_file) as zf:
                            zf.extractall(tmpdir)
                        
                        # Parse the extracted code
                        kg = KnowledgeGraph()
                        parser = GenericJavaParser()
                        parser.parse_directory(tmpdir, kg)
                        st.session_state.kg = kg
                        
                        # Show results
                        stats = kg.get_stats()
                        st.success("✅ Code analyzed successfully!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Classes Found", stats['classes'])
                        with col2:
                            st.metric("Methods Found", stats['methods'])
                        with col3:
                            st.metric("Endpoints Found", stats['endpoints'])
        
        else:  # Local directory
            local_path = st.text_input(
                "Enter local directory path:",
                placeholder="e.g., C:/my-project/src"
            )
            
            if local_path and st.button("🔍 Analyze Directory"):
                try:
                    with st.spinner("Analyzing your code..."):
                        kg = KnowledgeGraph()
                        parser = GenericJavaParser()
                        parser.parse_directory(local_path, kg)
                        st.session_state.kg = kg
                        
                        stats = kg.get_stats()
                        st.success("✅ Code analyzed successfully!")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Classes Found", stats['classes'])
                        with col2:
                            st.metric("Methods Found", stats['methods'])
                        with col3:
                            st.metric("Endpoints Found", stats['endpoints'])
                except Exception as e:
                    st.error(f"Error analyzing code: {e}")

# ============================================================================
# TAB 2: Analysis
# ============================================================================
with tab2:
    st.header("Step 2: Code Analysis")
    
    if st.session_state.kg is None:
        st.warning("⚠️ Please upload code first using the 'Upload Code' tab")
    else:
        kg = st.session_state.kg
        
        # Create summary
        summarizer = GraphSummarizer(kg)
        api_sig = summarizer.create_api_signature()
        
        detector = APIStyleDetector()
        api_style = detector.detect_style(kg)
        maturity = detector.analyze_rest_maturity(kg)
        
        # Display Analysis
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📌 API Style")
            st.metric("Primary Style", api_style['primary_style'])
            st.metric("Has REST Endpoints", "✅ Yes" if api_style['has_rest_endpoints'] else "❌ No")
        
        with col2:
            st.subheader("⭐ REST Maturity")
            st.metric("Maturity Level", f"{maturity['level']}/3")
            st.info(maturity['description'])
        
        with col3:
            st.subheader("📊 Statistics")
            st.metric("Classes", api_sig['total_classes'])
            st.metric("Methods", api_sig['total_methods'])
            st.metric("Endpoints", api_sig['total_endpoints'])
        
        # Detailed Analysis
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏷️ Top Annotations")
            if api_sig['annotation_counts']:
                ann_data = api_sig['annotation_counts']
                st.bar_chart(ann_data)
            else:
                st.info("No annotations found. This might be a legacy codebase.")
        
        with col2:
            st.subheader("🌐 HTTP Methods Usage")
            if api_sig['http_methods']:
                st.bar_chart(api_sig['http_methods'])
            else:
                st.info("No HTTP methods found.")
        
        # Recommendations
        st.divider()
        st.subheader("💡 Recommendations")
        recommendations = detector.analyze_rest_maturity(kg)['recommendations']
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
        
        # Endpoints
        if api_sig['total_endpoints'] > 0:
            st.divider()
            st.subheader("📍 Detected Endpoints")
            endpoint_data = []
            for endpoint in api_sig['endpoints']:
                endpoint_data.append({
                    "Method": endpoint['method'],
                    "Path": endpoint['path'],
                    "Handler": endpoint['handler']
                })
            st.dataframe(endpoint_data, use_container_width=True)

# ============================================================================
# TAB 3: Migration Plan
# ============================================================================
with tab3:
    st.header("Step 3: AI-Powered Migration Plan")
    
    if st.session_state.kg is None:
        st.warning("⚠️ Please upload code first using the 'Upload Code' tab")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            source_framework = st.selectbox(
                "Current Framework",
                ["Legacy/Unknown", "Struts", "Spring 3", "Spring 4", "JAX-RS", "Custom"]
            )
        
        with col2:
            target_framework = st.selectbox(
                "Target Framework",
                ["Spring Boot 3", "Quarkus", "Jakarta EE", "Micronaut", "Helidon"]
            )
        
        with col3:
            approach = st.selectbox(
                "Migration Approach",
                ["Incremental", "Big Bang", "Strangler Fig Pattern"]
            )
        
        if st.button("🤖 Generate Migration Plan", use_container_width=True):
            with st.spinner("Generating AI-powered migration plan..."):
                try:
                    generator = MigrationPlanGenerator(st.session_state.kg)
                    plan = generator.generate_migration_plan(
                        source_framework=source_framework,
                        target_framework=target_framework,
                        migration_approach=approach
                    )
                    st.session_state.migration_plan = plan
                    st.success("✅ Migration plan generated!")
                except Exception as e:
                    st.error(f"Error generating plan: {e}")
        
        # Display Plan
        if st.session_state.migration_plan:
            plan = st.session_state.migration_plan
            
            # Summary
            st.subheader("📋 Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Endpoints to Migrate", plan['summary']['endpoint_count'])
            with col2:
                st.metric("Estimated Effort", plan['summary']['estimated_effort'])
            with col3:
                st.metric("Target Framework", plan['summary']['target_framework'])
            with col4:
                st.metric("Approach", plan['summary']['approach'])
            
            st.divider()
            
            # Recommendations
            st.subheader("✨ Recommendations")
            for rec in plan['recommendations']:
                st.write(f"• {rec}")
            
            st.divider()
            
            # Migration Steps
            st.subheader("📅 Migration Timeline")
            for step in plan['migration_steps']:
                with st.expander(f"**{step['phase']}** ({step['duration']})"):
                    for task in step['tasks']:
                        st.write(f"- {task}")
            
            st.divider()
            
            # Risk Assessment
            st.subheader("⚠️ Risk Assessment")
            risk = plan['risk_assessment']
            risk_level = risk['overall_risk_level']
            risk_color = {
                "High": "🔴",
                "Medium": "🟡",
                "Low": "🟢"
            }
            st.write(f"## {risk_color.get(risk_level, '⚪')} Overall Risk: {risk_level}")
            
            for r in risk['identified_risks']:
                with st.expander(f"**{r['risk']}** - {r['probability']}"):
                    st.write(f"**Mitigation:** {r['mitigation']}")
            
            # Download Plan
            st.divider()
            plan_json = json.dumps(plan, indent=2)
            st.download_button(
                "⬇️ Download Migration Plan (JSON)",
                plan_json,
                "migration_plan.json",
                "application/json"
            )

# ============================================================================
# TAB 4: OpenAPI Spec
# ============================================================================
with tab4:
    st.header("Step 4: Generate OpenAPI Specification")
    
    if st.session_state.kg is None:
        st.warning("⚠️ Please upload code first using the 'Upload Code' tab")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            api_title = st.text_input("API Title", "My API")
        
        with col2:
            api_version = st.text_input("API Version", "1.0.0")
        
        if st.button("📋 Generate OpenAPI Spec", use_container_width=True):
            with st.spinner("Generating OpenAPI 3.1 specification..."):
                try:
                    generator = OpenAPIGenerator(st.session_state.kg)
                    spec = generator.generate_openapi_spec(api_title, api_version)
                    st.session_state.openapi_spec = spec
                    st.success("✅ OpenAPI spec generated!")
                except Exception as e:
                    st.error(f"Error generating spec: {e}")
        
        # Display Spec
        if st.session_state.openapi_spec:
            spec = st.session_state.openapi_spec
            
            # Overview
            st.subheader("📊 Specification Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("API Title", spec['info']['title'])
            with col2:
                st.metric("Version", spec['info']['version'])
            with col3:
                st.metric("Endpoints", len(spec['paths']))
            
            st.divider()
            
            # Paths
            st.subheader("🔗 Endpoints")
            for path, methods in spec['paths'].items():
                st.write(f"### {path}")
                for method, details in methods.items():
                    st.write(f"- **{method.upper()}**: {details.get('summary', 'No description')}")
            
            st.divider()
            
            # Download Spec
            spec_yaml = f"""openapi: {spec['openapi']}
info:
  title: {spec['info']['title']}
  version: {spec['info']['version']}
  description: {spec['info']['description']}
servers:
  - url: {spec['servers'][0]['url']}
    description: {spec['servers'][0]['description']}
paths:
"""
            for path, methods in spec['paths'].items():
                spec_yaml += f"  {path}:\n"
                for method, details in methods.items():
                    spec_yaml += f"    {method}:\n"
                    spec_yaml += f"      summary: {details.get('summary', '')}\n"
                    spec_yaml += f"      operationId: {details.get('operationId', '')}\n"
            
            st.download_button(
                "⬇️ Download OpenAPI Spec (YAML)",
                spec_yaml,
                "openapi.yaml",
                "text/yaml"
            )
            
            st.download_button(
                "⬇️ Download OpenAPI Spec (JSON)",
                json.dumps(spec, indent=2),
                "openapi.json",
                "application/json"
            )

# ============================================================================
# TAB 5: Documentation
# ============================================================================
with tab5:
    st.header("📚 Getting Started Guide")
    
    st.markdown("""
    ## Quick Start (5 minutes)
    
    ### 1️⃣ **Upload Your Code**
    - Go to the "Upload Code" tab
    - Upload a ZIP file with your Java project or provide a local directory path
    - The tool analyzes all `.java` files automatically
    
    ### 2️⃣ **Review Analysis**
    - Check the "Analysis" tab to see:
      - Detected API style (REST, SOAP, GraphQL, etc.)
      - REST maturity level (0-3)
      - Code statistics
      - Recommendations for improvement
    
    ### 3️⃣ **Generate Migration Plan**
    - Go to "Migration Plan" tab
    - Select your current and target frameworks
    - Choose migration approach
    - Click "Generate Migration Plan"
    - Get AI-powered recommendations from AWS Bedrock
    
    ### 4️⃣ **Export OpenAPI Spec**
    - Generate OpenAPI 3.1 specification
    - Download as YAML or JSON
    - Use with tools like Swagger UI, Postman, etc.
    
    ---
    
    ## AWS Bedrock Integration
    
    This tool uses **AWS Bedrock** for intelligent API modernization recommendations.
    
    ### Setup (Optional)
    ```bash
    # Install AWS CLI
    pip install awscli
    
    # Configure AWS credentials
    aws configure
    # Enter: Access Key ID, Secret Access Key, Region (us-east-1), Format (json)
    ```
    
    ### Free Tier Benefits
    - **AWS Bedrock**: Free tier available (limited calls)
    - **EC2**: 750 hours/month free tier
    - **S3**: 5 GB storage free
    - **Lambda**: 1 million requests/month free
    
    ---
    
    ## REST Maturity Levels
    
    | Level | Description | Examples |
    |-------|-------------|----------|
    | 0 | POX (Plain Old XML) | Custom RPC-style endpoints |
    | 1 | Resources | `/api/users`, `/api/products` |
    | 2 | HTTP Verbs | GET, POST, PUT, DELETE properly used |
    | 3 | HATEOAS | Links in responses for discoverability |
    
    ---
    
    ## Architecture
    
    ```
    Upload Java Code
         ↓
    Parse with Tree-Sitter
         ↓
    Knowledge Graph Construction
         ↓
    RAG Vector Store Creation
         ↓
    API Analysis (Inference)
         ↓
    AWS Bedrock Migration Planning
         ↓
    OpenAPI Spec Generation
    ```
    
    ---
    
    ## Supported Frameworks
    
    ### Source Frameworks
    - Spring Boot (2.x, 3.x)
    - Struts
    - JAX-RS / Jersey
    - Jakarta EE
    - Custom/Legacy
    
    ### Target Frameworks
    - **Spring Boot 3** (Recommended for most)
    - **Quarkus** (Cloud-native, fast)
    - **Jakarta EE** (Enterprise standard)
    - **Micronaut** (Lightweight, AOT)
    - **Helidon** (Oracle's framework)
    
    ---
    
    ## Troubleshooting
    
    ### No endpoints detected?
    - Ensure you have REST controller annotations (@RestController, @Controller)
    - Check that methods have mapping annotations (@GetMapping, @PostMapping, etc.)
    
    ### Bedrock not connecting?
    - Verify AWS credentials are configured
    - Check AWS region is correct
    - Fallback to local analysis still works
    
    ### Large codebase analysis slow?
    - The tool processes incrementally
    - Large projects (1000+ classes) may take 1-2 minutes
    - This is normal and safe to wait
    
    ---
    
    ## Free Tier AWS Deployment
    
    ### Deploy to EC2 (Free Tier)
    ```bash
    # 1. Launch EC2 instance (t2.micro, free tier eligible)
    # 2. SSH into instance
    # 3. Install dependencies:
    git clone <your-repo>
    cd api-modernization-tool
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # 4. Run with gunicorn
    gunicorn -w 4 -b 0.0.0.0:8000 app:server
    ```
    
    ### Deploy to Lambda (Free Tier)
    ```bash
    # Requires Streamlit Cloud or similar
    # Or use AWS Lambda + API Gateway
    ```
    
    ---
    
    ## Contact & Support
    
    Built for hackathons with ❤️ using:
    - **Python** with LangChain 0.3+, LangGraph
    - **Streamlit** for UI
    - **AWS Bedrock** for LLM
    - **FAISS** for vector search
    - **Tree-Sitter** for Java parsing
    """)

# ============================================================================
# Footer
# ============================================================================
st.divider()
st.markdown("""
<div style='text-align: center'>
    <p><strong>API Modernization Tool v1.0.0</strong> | Built for Hackathons | Free Tier AWS Ready</p>
    <p>Powered by: LangChain · LangGraph · AWS Bedrock · FAISS · Tree-Sitter</p>
</div>
""", unsafe_allow_html=True)
