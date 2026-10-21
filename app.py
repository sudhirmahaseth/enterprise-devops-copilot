import streamlit as st
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# 1. Page Configuration
st.set_page_config(
    page_title="Enterprise AI DevOps Copilot",
    page_icon="🤖",
    layout="wide"
)

# 2. Main Title & Description
st.title("🤖 Enterprise AI DevOps & Troubleshooting Copilot")
st.subheader("Llama-3 Powered CloudWatch Log Analysis & MTTR Reduction")
st.markdown("---")

# 3. Setup Groq Llama-3 Model (Reads your API Key from Streamlit Secrets)
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.sidebar.warning("⚠️ Please configure your GROQ_API_KEY in Streamlit Secrets.")
    st.info("To test locally, you can provide the API key below:")
    groq_api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# 4. Define Response Structure using Pydantic
class DevOpsAnalysis(BaseModel):
    root_cause: str = Field(description="The primary reason why the infrastructure or server error occurred.")
    severity: str = Field(description="Severity level: Low, Medium, High, or Critical.")
    remediation_steps: list = Field(description="Step-by-step technical instructions to fix the issue.")
    suggested_commands: list = Field(description="Terminal, AWS CLI, or kubectl commands to resolve the problem.")

# 5. Core Processing Function
def analyze_devops_logs(log_data):
    try:
        # Using ultra-fast Llama-3-8b via Groq API (100% Free)
        llm = ChatGroq(
            model="llama3-8b-8192", 
            temperature=0.1, 
            groq_api_key=groq_api_key
        )
        
        parser = JsonOutputParser(pydantic_object=DevOpsAnalysis)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert AWS DevOps and Site Reliability Engineer (SRE). Analyze the provided AWS CloudWatch logs, system crashes, or Kubernetes errors. Provide a clear root cause analysis and precise remediation steps.\n{format_instructions}"),
            ("user", "Analyze the following log infrastructure data:\n\n{logs}")
        ])
        
        chain = prompt | llm | parser
        
        response = chain.invoke({
            "logs": log_data,
            "format_instructions": parser.get_format_instructions()
        })
        return response
    except Exception as e:
        st.error(f"Error communicating with Llama-3 model: {str(e)}")
        return None

# 6. Streamlit User Layout (Fixed st.columns error)
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 Paste CloudWatch / Server Logs")
    sample_log = "ERROR: connection to database at 'aws-rds-cluster' failed: Connection timeout\nFATAL: microservice-pod-abc crashed with Exit Code 137 (OOMKilled)\naws-lambda: Out of memory during processing event-id-9981"
    
    log_input = st.text_area(
        "Input Logs here:", 
        value=sample_log, 
        height=300,
        placeholder="Paste your AWS CloudWatch, Kubernetes, or Docker logs here..."
    )
    
    analyze_btn = st.button("🚀 Run AI Root Cause Diagnosis", type="primary")

with col2:
    st.markdown("### 🔍 AI Copilot Diagnosis (Llama-3)")
    
    if analyze_btn:
        if not groq_api_key:
            st.error("Missing Groq API Key! Please supply a key in the sidebar or Secrets to run analysis.")
        elif not log_input.strip():
            st.warning("Please paste some log data first.")
        else:
            with st.spinner("Llama-3 is analyzing infrastructure logs and generating solutions..."):
                result = analyze_devops_logs(log_input)
                
                if result:
                    # Display Severity Badge
                    sev = result.get('severity', 'Medium').upper()
                    if sev in ['HIGH', 'CRITICAL']:
                        st.error(f"🚨 Severity Level: {sev}")
                    else:
                        st.warning(f"⚠️ Severity Level: {sev}")
                        
                    # Display Root Cause
                    st.markdown("#### **Root Cause Analysis**")
                    st.info(result.get('root_cause'))
                    
                    # Display Remediation Steps
                    st.markdown("#### **Remediation Steps**")
                    for step in result.get('remediation_steps', []):
                        st.write(f"- {step}")
                        
                    # Display CLI Commands
                    st.markdown("#### **Suggested Execution Commands**")
                    for cmd in result.get('suggested_commands', []):
                        st.code(cmd, language="bash")
