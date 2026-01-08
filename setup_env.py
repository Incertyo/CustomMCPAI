"""
Setup script to create .env file from template
"""

import shutil
from pathlib import Path

def setup_env():
    """Create .env file from .env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path("env_template.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    # Create env template content
    env_content = """# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000

# Cloud API Keys (for real integrations)
# AWS_ACCESS_KEY_ID=your_aws_key
# AWS_SECRET_ACCESS_KEY=your_aws_secret
# GCP_PROJECT_ID=your_gcp_project
# GCP_CREDENTIALS_PATH=path/to/credentials.json
# AZURE_SUBSCRIPTION_ID=your_azure_subscription
# AZURE_CLIENT_ID=your_azure_client_id
# AZURE_CLIENT_SECRET=your_azure_secret
# AZURE_TENANT_ID=your_azure_tenant

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
"""
    
    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("⚠️  Please edit .env and add your GEMINI_API_KEY")
    print("   Get your key from: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    setup_env()
