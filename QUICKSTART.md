# 🚀 Quick Start Guide

Get the AI Cloud Optimization Agent running in 5 minutes!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Setup Environment

```bash
python setup_env.py
```

Then edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

## Step 3: Start MCP Server

In one terminal:
```bash
python mcp_server.py
```

You should see:
```
🚀 Starting MCP Server on http://localhost:8000
📚 API Documentation: http://localhost:8000/docs
```

## Step 4: Run AI Agent

In another terminal:
```bash
python gemini_agent.py
```

This will:
- Fetch data from MCP server
- Analyze with Gemini AI
- Save recommendations to `recommendations.json`

## Step 5: View Dashboard

In another terminal:
```bash
streamlit run streamlit_app.py
```

Open http://localhost:8501 in your browser!

## 🎯 Alternative: Use the Launcher

```bash
python run_all.py
```

Select option 4 to run the complete workflow.

## ✅ Verify Everything Works

Test the MCP server:
```bash
python test_mcp_server.py
```

## 🐳 Docker Option

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 📋 What's Next?

1. **Import n8n workflow**: Open n8n, import `n8n_workflow.json`
2. **Schedule automation**: Set up weekly runs
3. **Customize**: Add your cloud provider APIs
4. **Deploy**: Use Streamlit Cloud or your own server

## 🆘 Troubleshooting

**MCP Server won't start?**
- Check if port 8000 is available
- Make sure all dependencies are installed

**Gemini API errors?**
- Verify your API key in `.env`
- Check your API quota

**Streamlit won't load?**
- Make sure `recommendations.json` exists
- Check terminal for errors

**Need help?** Check the main README.md for detailed documentation.
