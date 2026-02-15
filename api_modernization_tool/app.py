"""Comprehensive Streamlit App for Full App Modernization"""
import streamlit as st
import json
from pathlib import Path
from src.knowledge_graph.graph import KnowledgeGraph
from src.parser.java_parser import GenericJavaParser
from src.rag.vectorstore import GraphToDocuments, VectorStoreManager, convert_graph_to_documents
from src.inference.api_detector import APIStyleDetector, GraphSummarizer
from src.migration.migration_engine import MigrationPlanGenerator, OpenAPIGenerator
from src.assessment.assessment_engine import ArchitectureAssessment
from src.assessment.security_analyzer import SecurityAnalyzer
from src.assessment.cost_estimator import CostEstimator
from src.assessment.roadmap_generator import RoadmapGenerator
from src.utils.config import Config
from src.utils.preferences import ModernizationPreferences, PreferenceManager
from src.migration.code_generator import ModernizedCodeGenerator

# Configure page
st.set_page_config(
    page_title="Full App Modernization Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS Styling with Animations
st.markdown("""
<style>
    /* Global Styles */
    :root {
        --primary-color: #0066CC;
        --secondary-color: #00D9FF;
        --success-color: #00C853;
        --danger-color: #FF5252;
        --warning-color: #FFB74D;
    }

    /* Custom Font and Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 20px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
    }

    /* Button Animations */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }

    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }

    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
    }

    /* Download Button Special Style */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00C853 0%, #00BCD4 100%);
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #00BCD4 0%, #00C853 100%);
    }

    /* Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #F5F7FF 0%, #FFFAFF 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
    }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #F5F7FF 0%, #FFFAFF 100%);
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #E8ECFF 0%, #FFF5F7 100%);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #F5F7FF 0%, #FFFAFF 100%);
    }

    /* Success/Info/Error Styling */
    .stSuccess {
        background-color: rgba(0, 200, 83, 0.1);
        border-left: 4px solid #00C853;
        border-radius: 8px;
        padding: 12px 16px;
    }

    .stError {
        background-color: rgba(255, 82, 82, 0.1);
        border-left: 4px solid #FF5252;
        border-radius: 8px;
        padding: 12px 16px;
    }

    .stWarning {
        background-color: rgba(255, 183, 77, 0.1);
        border-left: 4px solid #FFB74D;
        border-radius: 8px;
        padding: 12px 16px;
    }

    .stInfo {
        background-color: rgba(0, 102, 204, 0.1);
        border-left: 4px solid #0066CC;
        border-radius: 8px;
        padding: 12px 16px;
    }

    /* Slider Styling */
    .stSlider [data-baseweb="slider"] {
        padding: 16px 0;
    }

    /* Metric Styling */
    .stMetric {
        background: linear-gradient(135deg, #F5F7FF 0%, #FFFAFF 100%);
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }

    .stMetric:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
    }

    /* Code Block Styling */
    .stCodeBlock {
        background: #1e1e1e;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    /* Divider Styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 24px 0;
    }

    /* Loading Animation */
    @keyframes pulse {
        0% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
        100% {
            opacity: 1;
        }
    }

    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    /* Floating Animation */
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    .float-icon {
        animation: float 3s ease-in-out infinite;
    }

    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Selection Animation */
    .stSelectbox [data-baseweb="select"] {
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }

    /* Checkbox Styling */
    .stCheckbox [data-baseweb="checkbox"] {
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    /* Input Styling */
    .stTextInput input, .stNumberInput input {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }

    /* Progress Bar Animation */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize config
Config.init_folders()

# Session state initialization
if 'kg' not in st.session_state:
    st.session_state.kg = None
if 'file_processed' not in st.session_state:
    st.session_state.file_processed = False
if 'preferences' not in st.session_state:
    st.session_state.preferences = ModernizationPreferences()
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = {}

# Sidebar - Professional Design
with st.sidebar:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("🚀", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <span style='font-size: 18px; font-weight: 700; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>
        Modernization Platform
        </span>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Status indicator
    if st.session_state.kg:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #F5F7FF 0%, #FFFAFF 100%); 
            padding: 12px; border-radius: 8px; border-left: 4px solid #00C853;'>
            <span style='font-weight: 600; color: #667eea;'>{len(st.session_state.kg.classes)} Classes</span><br>
            <span style='font-size: 12px; color: #666;'>{len(st.session_state.kg.methods)} Methods</span><br>
            <span style='font-size: 12px; color: #666;'>{len(st.session_state.kg.endpoints)} Endpoints</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #F5F7FF 0%, #FFFAFF 100%); 
        padding: 12px; border-radius: 8px; border-left: 4px solid #0066CC; text-align: center;'>
        <span style='font-weight: 600; color: #667eea;'>Ready to Analyze</span><br>
        <span style='font-size: 12px; color: #666;'>Upload code to begin</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick links
    st.markdown("**Quick Navigation:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Dashboard"):
            st.info("Dashboard features coming soon")
    with col2:
        if st.button("📚 Help"):
            st.info("Visit the Knowledge Base tab for help")
    
    st.divider()
    
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>
    <p><strong>Version 3.0.0</strong></p>
    <p>🏆 Ready for Hackathon</p>
    <p>Powered by AI & LLMs</p>
    </div>
    """, unsafe_allow_html=True)

# Main header - Enhanced with gradient and animation
st.markdown("""
<div style='text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
border-radius: 16px; padding: 40px 20px; margin-bottom: 30px; 
box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);'>
    <h1 style='color: white; margin: 0; font-size: 48px; font-weight: 700; letter-spacing: -1px;'>
    🚀 App Modernization Platform
    </h1>
    <p style='color: rgba(255,255,255,0.9); font-size: 18px; margin: 12px 0 0 0; font-weight: 500;'>
    Enterprise-Grade Application Transformation with AI Intelligence
    </p>
    <p style='color: rgba(255,255,255,0.8); font-size: 14px; margin: 8px 0 0 0;'>
    Analyze • Assess • Plan • Generate • Deploy
    </p>
</div>
""", unsafe_allow_html=True)

# Create comprehensive tabs
tabs = st.tabs([
    "📁 Upload",
    "⚙️ Preferences",
    "🏗️ Architecture",
    "🔒 Security",
    "⚡ Performance",
    "💰 Cost & ROI",
    "🗺️ Roadmap",
    "📊 Analysis",
    "🤖 Migration",
    "📋 OpenAPI",
    "💻 Generate Code",
    "📚 Knowledge Base"
])

# ============================================================================
# TAB 0: Upload Code
# ============================================================================
with tabs[0]:
    st.header("📁 Step 1: Upload Your Application Code")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Upload Options:
        - **Single Java File** (.java)
        - **ZIP Archive** (complete project)
        - **Directory Path** (local scan)
        
        ### What We Analyze:
        ✓ Code structure and complexity
        ✓ API endpoints and frameworks
        ✓ Architecture patterns
        ✓ Dependencies and libraries
        ✓ Security vulnerabilities
        ✓ Performance bottlenecks
        """)
    
    with col2:
        upload_method = st.radio("Choose upload method:", 
                                 ["Upload File", "Enter Directory Path"])
        
        if upload_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose a Java file or ZIP",
                type=["java", "zip"],
                help="Upload Java source code or ZIP archive"
            )
            
            if uploaded_file and st.button("🔍 Analyze Code"):
                with st.spinner("Analyzing application..."):
                    import tempfile
                    
                    kg = KnowledgeGraph()
                    parser = GenericJavaParser()
                    
                    if uploaded_file.type == "application/zip":
                        import zipfile
                        with tempfile.TemporaryDirectory() as tmpdir:
                            with zipfile.ZipFile(uploaded_file) as zf:
                                zf.extractall(tmpdir)
                            parser.parse_directory(tmpdir, kg)
                    else:
                        with tempfile.NamedTemporaryFile(suffix=".java") as tmp:
                            tmp.write(uploaded_file.getbuffer())
                            tmp.flush()
                            parser.parse_file(tmp.name, kg)
                    
                    st.session_state.kg = kg
                    st.session_state.file_processed = True
                    st.success("✅ Application analyzed successfully!")
        
        else:
            dir_path = st.text_input(
                "Enter directory path:",
                value="D:\\App Modernization\\api_modernization_tool\\uploaded_files",
                help="Full path to directory containing Java files"
            )
            
            if st.button("🔍 Scan Directory"):
                with st.spinner("Scanning directory..."):
                    kg = KnowledgeGraph()
                    parser = GenericJavaParser()
                    
                    if Path(dir_path).exists():
                        parser.parse_directory(dir_path, kg)
                        st.session_state.kg = kg
                        st.session_state.file_processed = True
                        st.success("✅ Directory scanned successfully!")
                    else:
                        st.error("❌ Directory not found!")

# ============================================================================
# TAB 1: Preferences & Customization
# ============================================================================
with tabs[1]:
    st.header("⚙️ Modernization Preferences")
    
    st.markdown("**Configure modernization parameters to customize analysis and code generation**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Architecture & Framework")
        target_framework = st.selectbox(
            "Target Framework",
            ["Spring Boot 3.x", "Quarkus", "Micronaut", "Jakarta EE"],
            index=0
        )
        
        api_style = st.selectbox(
            "API Style",
            ["REST", "GraphQL", "gRPC", "WebSocket"],
            index=0
        )
        
        architecture = st.selectbox(
            "Architecture Pattern",
            ["Monolith", "Microservices", "Serverless", "Hybrid"],
            index=1
        )
        
        async_enabled = st.checkbox("Enable Async Patterns", value=True)
        reactive_enabled = st.checkbox("Enable Reactive (WebFlux)", value=False)
    
    with col2:
        st.subheader("☁️ Cloud & DevOps")
        
        cloud_provider = st.selectbox(
            "Cloud Provider",
            ["AWS", "Azure", "GCP", "Multi-cloud", "On-premise"],
            index=0
        )
        
        containerization = st.selectbox(
            "Containerization",
            ["Docker", "Kubernetes", "Serverless"],
            index=0
        )
        
        database_type = st.selectbox(
            "Database",
            ["PostgreSQL", "MySQL", "DynamoDB", "MongoDB", "Cassandra"],
            index=0
        )

        build_system = st.selectbox(
            "Build System",
            ["Maven", "Gradle"],
            index=0
        )
        
        cache_strategy = st.selectbox(
            "Caching Strategy",
            ["Redis", "Memcached", "None"],
            index=0
        )
    
    st.divider()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🔒 Security & Compliance")
        
        security_framework = st.selectbox(
            "Security Framework",
            ["Spring Security", "OAuth2", "Custom"],
            index=0
        )
        
        authentication = st.selectbox(
            "Authentication",
            ["JWT", "OAuth2", "SAML", "LDAP"],
            index=0
        )
        
        encryption = st.selectbox(
            "Encryption",
            ["TLS1.3", "TLS1.2", "Custom"],
            index=0
        )
        
        compliance = st.multiselect(
            "Compliance Requirements",
            ["GDPR", "HIPAA", "PCI-DSS", "SOC2", "NIST"],
            default=["GDPR", "SOC2"]
        )
    
    with col4:
        st.subheader("💰 Budget & Timeline")
        
        budget = st.slider(
            "Budget (USD)",
            min_value=50000,
            max_value=500000,
            value=150000,
            step=10000
        )
        
        timeline = st.slider(
            "Timeline (Months)",
            min_value=3,
            max_value=24,
            value=6,
            step=1
        )
        
        team_size = st.slider(
            "Team Size",
            min_value=3,
            max_value=50,
            value=8,
            step=1
        )
        
        performance_priority = st.selectbox(
            "Performance Priority",
            ["Speed", "Balanced", "Stability"],
            index=1
        )
    
    st.divider()
    
    # Save preferences
    if st.button("💾 Save Preferences"):
        st.session_state.preferences = ModernizationPreferences(
            target_framework=target_framework,
            api_style=api_style,
            architecture=architecture,
            async_enabled=async_enabled,
            reactive_enabled=reactive_enabled,
            cloud_provider=cloud_provider,
            containerization=containerization,
            database_type=database_type,
            build_system=build_system,
            cache_strategy=cache_strategy,
            security_framework=security_framework,
            authentication=authentication,
            encryption=encryption,
            budget_usd=budget,
            timeline_months=timeline,
            team_size=team_size,
            performance_priority=performance_priority,
            compliance_requirements=compliance
        )
        st.success("✅ Preferences saved!")
    
    st.divider()
    
    st.subheader("📋 Current Preferences Summary")
    
    prefs = st.session_state.preferences
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Framework", prefs.target_framework)
    with summary_col2:
        st.metric("API Style", prefs.api_style)
    with summary_col3:
        st.metric("Architecture", prefs.architecture)
    with summary_col4:
        st.metric("Cloud", prefs.cloud_provider)
    
    # Show build system (use getattr for backward compatibility)
    st.write(f"**Build System:** {getattr(prefs, 'build_system', 'Maven')}")

# ============================================================================
# TAB 2: Architecture Assessment
# ============================================================================
with tabs[2]:
    st.header("🏗️ Architecture Assessment")
    
    if st.session_state.kg:
        assessment = ArchitectureAssessment(st.session_state.kg)
        results = assessment.assess_architecture()
        
        # Score cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Modularity Score", f"{results['modularity_score']}/100")
        with col2:
            st.metric("Scalability Score", f"{results['scalability_score']}/100")
        with col3:
            st.metric("Maintainability", f"{results['maintainability_score']}/100")
        with col4:
            st.metric("Testability", f"{results['testability_score']}/100")
        
        st.divider()
        
        # Security concerns
        st.subheader("🔍 Identified Issues")
        for concern in results['security_concerns']:
            st.info(concern)
        
        # Technical debt
        st.subheader("📊 Technical Debt Analysis")
        debt = results['technical_debt']
        st.warning(f"**Severity: {debt['severity']}** | Score: {debt['score']}/100")
        
        for item in debt['items']:
            st.write(f"• {item}")
    else:
        st.info("📁 Upload code first in the Upload tab to see architecture assessment")

# ============================================================================
# TAB 3: Security Analysis
# ============================================================================
with tabs[3]:
    st.header("🔒 Security & Compliance Analysis")
    
    if st.session_state.kg:
        security = SecurityAnalyzer(st.session_state.kg)
        results = security.analyze_security()
        
        # Overall score
        st.metric("Security Score", f"{results['overall_score']}/100")
        
        # Vulnerabilities
        st.subheader("🚨 Detected Vulnerabilities")
        for vuln in results['vulnerabilities']:
            if "Low" in vuln.get("severity", ""):
                st.success(vuln.get("description", ""))
            elif "Info" in vuln.get("severity", ""):
                st.info(vuln.get("description", ""))
            elif "Medium" in vuln.get("severity", ""):
                st.warning(vuln.get("description", ""))
            else:
                st.error(f"**{vuln.get('severity', 'Unknown')}**: {vuln.get('description', '')}")
        
        # Compliance gaps
        st.subheader("📋 Compliance Gaps")
        for gap in results['compliance_gaps']:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.write(f"**{gap['framework']}**")
            with col2:
                st.write(gap['status'])
            with col3:
                st.write(f"`{gap['requirement']}`")
        
        # Data protection
        st.subheader("🛡️ Data Protection Assessment")
        data = results['data_protection']
        for key, value in data.items():
            if key != "recommendations":
                st.write(f"• {key}: {value}")
        
        # Recommendations
        st.subheader("✅ Security Recommendations")
        for rec in results['recommendations']:
            st.write(rec)
    else:
        st.info("📁 Upload code first to see security analysis")

# ============================================================================
# TAB 4: Performance Analysis
# ============================================================================
with tabs[4]:
    st.header("⚡ Performance Analysis")
    
    if st.session_state.kg:
        st.subheader("📊 Current Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Classes", len(st.session_state.kg.classes))
        with col2:
            st.metric("Total Methods", len(st.session_state.kg.methods))
        with col3:
            st.metric("API Endpoints", len(st.session_state.kg.endpoints))
        with col4:
            avg_methods = (len(st.session_state.kg.methods) / max(len(st.session_state.kg.classes), 1))
            st.metric("Methods/Class", f"{avg_methods:.1f}")
        
        st.divider()
        
        st.subheader("🎯 Performance Bottlenecks")
        
        bottlenecks = [
            {"type": "Large Methods", "description": "Methods > 100 lines may have performance issues", "priority": "Medium"},
            {"type": "N+1 Queries", "description": "Check for nested loops in data fetching", "priority": "High"},
            {"type": "Missing Caching", "description": "Repeated calculations not cached", "priority": "Medium"},
            {"type": "Synchronous I/O", "description": "Consider async patterns for I/O operations", "priority": "High"},
        ]
        
        for idx, bottleneck in enumerate(bottlenecks):
            with st.expander(f"{bottleneck['type']} - {bottleneck['priority']} Priority"):
                st.write(bottleneck['description'])
                if idx == 0:
                    st.code("// Example refactoring", language="java")
        
        st.subheader("⚙️ Optimization Recommendations")
        recommendations = [
            "✓ Implement connection pooling for database",
            "✓ Add caching layer (Redis/Memcached)",
            "✓ Use async/await patterns for I/O",
            "✓ Enable gzip compression for responses",
            "✓ Implement CDN for static content",
            "✓ Use database query optimization",
            "✓ Implement rate limiting and throttling"
        ]
        
        for rec in recommendations:
            st.write(rec)
    else:
        st.info("📁 Upload code first to see performance analysis")

# ============================================================================
# TAB 5: Cost & ROI Analysis
# ============================================================================
with tabs[5]:
    st.header("💰 Cost Estimation & ROI Analysis")
    
    if st.session_state.kg:
        cost_estimator = CostEstimator(st.session_state.kg)
        costs = cost_estimator.estimate_costs()
        roi = cost_estimator.calculate_roi()
        
        st.subheader("📊 Cost Breakdown")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Planning", f"${costs['planning']:,}")
        with col2:
            st.metric("Development", f"${costs['development']:,}")
        with col3:
            st.metric("Testing", f"${costs['testing']:,}")
        with col4:
            st.metric("Deployment", f"${costs['deployment']:,}")
        with col5:
            st.metric("Training", f"${costs['training']:,}")
        with col6:
            st.metric("**Total Cost**", f"**${costs['total_cost']:,}**")
        
        st.divider()
        
        st.subheader("📈 Return on Investment (3-Year)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Payback Period", f"{roi['payback_period_months']:.1f} months")
        with col2:
            st.metric("3-Year ROI", f"{roi['roi_3_years']:.0f}%")
        with col3:
            st.metric("Annual Benefits", f"${roi['annual_benefits']['total']:,}")
        with col4:
            st.metric("Team Size", f"{costs['team_size']['total']} people")
        
        st.divider()
        
        st.subheader("💡 Benefits Breakdown")
        
        benefits = roi['annual_benefits']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.write(f"**Efficiency Gains**\n${benefits['efficiency_gains']:,}")
        with col2:
            st.write(f"**Reduced Incidents**\n${benefits['reduction_in_incidents']:,}")
        with col3:
            st.write(f"**Faster Deploys**\n${benefits['faster_deployments']:,}")
        with col4:
            st.write(f"**Infrastructure**\n${benefits['infrastructure_savings']:,}")
        
        st.success(roi['recommendation'])
        
        st.divider()
        
        st.subheader("👥 Recommended Team Composition")
        team = costs['team_size']
        for role, count in team.items():
            if role != 'total':
                st.write(f"• {role.replace('_', ' ').title()}: {count}")
    else:
        st.info("📁 Upload code first to see cost analysis")

# ============================================================================
# TAB 6: Migration Roadmap
# ============================================================================
with tabs[6]:
    st.header("🗺️ Detailed Migration Roadmap")
    
    if st.session_state.kg:
        roadmap_gen = RoadmapGenerator(st.session_state.kg)
        roadmap = roadmap_gen.generate_roadmap()
        
        st.markdown(roadmap['executive_summary'])
        
        st.divider()
        
        st.subheader("📅 Migration Phases")
        
        for phase in roadmap['phases']:
            with st.expander(f"**{phase['phase']}** - {phase['duration']}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Activities:**")
                    for activity in phase['activities']:
                        st.write(f"• {activity}")
                
                with col2:
                    st.write("**Deliverables:**")
                    for deliverable in phase['deliverables']:
                        st.write(f"✓ {deliverable}")
                
                st.write(f"**Resources:** {phase['resources']}")
                st.write(f"**Owner:** {phase['owner']}")
        
        st.divider()
        
        st.subheader("⚠️ Risk Assessment")
        
        for risk in roadmap['risks']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{risk['risk']}**")
            with col2:
                st.write(f"Prob: {risk['probability']}\nImpact: {risk['impact']}")
            with col3:
                st.write(f"**Mitigation:**\n{risk['mitigation']}")
        
        st.divider()
        
        st.subheader("✅ Success Metrics")
        
        for metric in roadmap['success_metrics']:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{metric['metric']}**")
            with col2:
                st.write(f"Baseline:\n{metric['baseline']}")
            with col3:
                st.write(f"Target:\n{metric['target']}")
    else:
        st.info("📁 Upload code first to see migration roadmap")

# ============================================================================
# TAB 7: Code Analysis
# ============================================================================
with tabs[7]:
    st.header("📊 Detailed Code Analysis")
    
    if st.session_state.kg:
        summarizer = GraphSummarizer(st.session_state.kg)
        api_sig = summarizer.create_api_signature()
        
        st.subheader("📈 API Signature")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Classes", api_sig['total_classes'])
        with col2:
            st.metric("Total Methods", api_sig['total_methods'])
        with col3:
            st.metric("Endpoints", api_sig['total_endpoints'])
        with col4:
            st.metric("Packages", len(api_sig['packages']))
        
        st.divider()
        
        st.subheader("🏷️ Top Annotations")
        
        annotations = api_sig['annotation_counts']
        if annotations:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Most Used Annotations:**")
                for ann, count in sorted(annotations.items(), key=lambda x: x[1], reverse=True)[:10]:
                    st.write(f"• {ann}: {count}x")
            
            with col2:
                st.bar_chart({ann: count for ann, count in list(annotations.items())[:5]})
        
        st.divider()
        
        st.subheader("🌐 HTTP Methods")
        
        http_methods = api_sig['http_methods']
        if http_methods:
            for method, count in http_methods.items():
                st.write(f"• **{method}**: {count} endpoints")
        
        st.divider()
        
        st.subheader("📍 Sample Endpoints")
        
        if api_sig['endpoints']:
            for idx, endpoint in enumerate(api_sig['endpoints'][:5]):
                st.write(f"{idx+1}. **{endpoint['method']}** `{endpoint['path']}` → `{endpoint['handler']}`")
    else:
        st.info("📁 Upload code first to see analysis")

# ============================================================================
# TAB 8: Migration Plan & Recommendations
# ============================================================================
with tabs[8]:
    st.header("🤖 AI-Powered Migration Plan")
    
    if st.session_state.kg:
        detector = APIStyleDetector()
        style = detector.detect_style(st.session_state.kg)
        maturity = detector.analyze_rest_maturity(st.session_state.kg)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 API Style")
            st.info(f"**Detected:** {style['primary_style']}\n\nEndpoint Count: {style['endpoint_count']}")
        
        with col2:
            st.subheader("📊 REST Maturity")
            level = maturity['level']
            levels = ["POX (Plain Old XML)", "Resources", "HTTP Verbs", "HATEOAS"]
            st.success(f"**Level {level}/3:** {levels[level]}\n\n{maturity['description']}")
        
        st.divider()
        
        st.subheader("💡 Recommendations")
        for i, rec in enumerate(maturity['recommendations'], 1):
            st.write(f"{i}. {rec}")
        
        st.divider()
        
        # Generate migration plan if Bedrock is available
        st.subheader("📋 Detailed Migration Plan")
        
        if st.button("🚀 Generate Migration Plan"):
            with st.spinner("Generating AI-powered migration plan..."):
                migrator = MigrationPlanGenerator(st.session_state.kg)
                migration_plan = migrator.generate_migration_plan(
                    source_framework="Legacy Spring 2.x",
                    target_framework="Spring Boot 3.x"
                )
                
                st.session_state.migration_plan = migration_plan
                st.json(migration_plan)
    else:
        st.info("📁 Upload code first to generate migration plan")

# ============================================================================
# TAB 9: OpenAPI Specification
# ============================================================================
with tabs[9]:
    st.header("📋 OpenAPI 3.0 Specification")
    
    if st.session_state.kg:
        openapi_gen = OpenAPIGenerator(st.session_state.kg)
        spec = openapi_gen.generate_openapi_spec(
            title="Modernized API",
            version="3.0.0"
        )
        
        st.subheader("📄 Generated OpenAPI Spec")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Download as YAML"):
                import yaml
                yaml_content = yaml.dump(spec, default_flow_style=False)
                st.download_button(
                    label="Download YAML",
                    data=yaml_content,
                    file_name="openapi.yaml",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📥 Download as JSON"):
                json_content = json.dumps(spec, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_content,
                    file_name="openapi.json",
                    mime="application/json"
                )
        
        st.divider()
        
        st.subheader("👁️ Preview")
        
        with st.expander("View Specification"):
            st.json(spec)
    else:
        st.info("📁 Upload code first to generate OpenAPI spec")

# ============================================================================
# TAB 10: Generate Code
# ============================================================================
with tabs[10]:
    st.header("💻 Generate Modernized Code")
    
    if st.session_state.kg:
        st.markdown("**Generate ready-to-use modernized code based on your preferences**")
        
        st.subheader("🔄 Code Generation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        prefs = st.session_state.preferences
        
        with col1:
            st.metric("Framework", prefs.target_framework)
        with col2:
            st.metric("API Style", prefs.api_style)
        with col3:
            st.metric("Database", prefs.database_type)
        with col4:
            st.metric("Cloud", prefs.cloud_provider)
        
        st.divider()
        
        if st.button("🚀 Generate Complete Codebase"):
            with st.spinner("Generating modernized code..."):
                generator = ModernizedCodeGenerator(st.session_state.kg, st.session_state.preferences)
                st.session_state.generated_code = generator.generate_all_code()
                st.success("✅ Code generation complete!")
        
        st.divider()
        
        if st.session_state.generated_code:
            st.subheader("📁 Generated Files")
            
            files = list(st.session_state.generated_code.keys())
            selected_file = st.selectbox("Select file to view:", files)
            
            if selected_file:
                st.subheader(f"📄 {selected_file}")
                st.code(st.session_state.generated_code[selected_file], language="java" if selected_file.endswith(".java") else "yaml" if selected_file.endswith((".yml", ".yaml")) else "dockerfile")
                
                st.download_button(
                    label=f"📥 Download {selected_file}",
                    data=st.session_state.generated_code[selected_file],
                    file_name=selected_file,
                    mime="text/plain"
                )
            
            st.divider()
            
            st.subheader("📦 Download All Files")
            
            import zipfile
            import io
            
            if st.button("📦 Create ZIP Archive"):
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for filename, content in st.session_state.generated_code.items():
                        zip_file.writestr(filename, content)
                
                zip_buffer.seek(0)
                
                st.download_button(
                    label="📥 Download All Generated Files (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="modernized-app-code.zip",
                    mime="application/zip"
                )
        else:
            st.info("👆 Click 'Generate Complete Codebase' to generate modernized code")
    else:
        st.info("📁 Upload code first in the Upload tab to generate modernized code")

# ============================================================================
# TAB 11: Knowledge Base
# ============================================================================
with tabs[11]:
    st.header("📚 Modernization Knowledge Base")
    
    st.subheader("🎓 Learning Resources")
    
    resources = {
        "Spring Boot 3 Migration": {
            "desc": "Complete guide for migrating to Spring Boot 3.x",
            "link": "/migration_knowledge/frameworks/spring_boot_3.md"
        },
        "Controller Migration": {
            "desc": "REST controller patterns and migration strategies",
            "link": "/migration_knowledge/skills/controller_migration.md"
        },
        "Service Layer": {
            "desc": "Service layer best practices and refactoring",
            "link": "/migration_knowledge/skills/service_migration.md"
        }
    }
    
    for title, resource in resources.items():
        with st.expander(f"📖 {title}"):
            st.write(resource['desc'])
            
            try:
                with open(f"migration_knowledge/{resource['link'].split('migration_knowledge/')[-1]}", "r") as f:
                    content = f.read()
                    st.markdown(content[:500] + "...")
            except:
                st.info("Knowledge base file not found")
    
    st.divider()
    
    st.subheader("🏆 Best Practices")
    
    best_practices = [
        {
            "title": "Microservices Architecture",
            "tips": [
                "Keep services loosely coupled",
                "Use event-driven communication",
                "Implement circuit breakers",
                "Monitor and trace requests"
            ]
        },
        {
            "title": "Cloud-Native Patterns",
            "tips": [
                "12-factor app methodology",
                "Containerization with Docker",
                "Kubernetes orchestration",
                "Infrastructure as Code"
            ]
        },
        {
            "title": "API Design",
            "tips": [
                "RESTful principles",
                "Versioning strategy",
                "Documentation (OpenAPI)",
                "Rate limiting and throttling"
            ]
        }
    ]
    
    for practice in best_practices:
        with st.expander(f"✅ {practice['title']}"):
            for tip in practice['tips']:
                st.write(f"• {tip}")

st.divider()

st.markdown("""
---
**Need Help?** Check our [Documentation](/) | **AWS Free Tier** | **AI-Powered Recommendations**
""")
