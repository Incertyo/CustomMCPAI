"""
Convenience script to run the complete system
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import google.generativeai
        import fastapi
        import uvicorn
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_env():
    """Check if .env file exists and has API key"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found. Copying from .env.example...")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ Created .env file. Please add your GEMINI_API_KEY!")
            return False
        else:
            print("❌ .env.example not found")
            return False
    
    # Check for API key
    with open(".env", "r") as f:
        content = f.read()
        if "GEMINI_API_KEY=your_gemini_api_key_here" in content or "GEMINI_API_KEY=" not in content:
            print("⚠️  Please set GEMINI_API_KEY in .env file")
            return False
    
    print("✅ Environment configured")
    return True

def main():
    """Main runner"""
    print("🚀 AI Cloud Optimization Agent - System Launcher")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    if not check_env():
        print("\n⚠️  Please configure .env file before running")
        sys.exit(1)
    
    print("\n📋 Available options:")
    print("1. Start MCP Server only")
    print("2. Run AI Agent analysis (standalone)")
    print("3. Start Streamlit Dashboard only")
    print("4. Run complete workflow (Agent + Save results)")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        print("\n🌐 Starting MCP Server...")
        print("Server will run on http://localhost:8000")
        print("API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop\n")
        subprocess.run([sys.executable, "mcp_server.py"])
    
    elif choice == "2":
        print("\n🤖 Running AI Agent analysis...")
        subprocess.run([sys.executable, "gemini_agent.py"])
    
    elif choice == "3":
        print("\n📊 Starting Streamlit Dashboard...")
        print("Dashboard will open at http://localhost:8501")
        print("\nPress Ctrl+C to stop\n")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    
    elif choice == "4":
        print("\n🔄 Running complete workflow...")
        print("Step 1: Running AI Agent...")
        result = subprocess.run([sys.executable, "gemini_agent.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Analysis complete!")
            print("\nStep 2: Starting Streamlit Dashboard...")
            print("Dashboard will open at http://localhost:8501")
            print("\nPress Ctrl+C to stop\n")
            subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
        else:
            print("❌ Analysis failed:")
            print(result.stderr)
            sys.exit(1)
    
    elif choice == "5":
        print("👋 Goodbye!")
        sys.exit(0)
    
    else:
        print("❌ Invalid choice")
        sys.exit(1)

if __name__ == "__main__":
    main()
