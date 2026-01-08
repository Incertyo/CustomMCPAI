# ☁️ AI Cloud Optimization Agent

A production-ready AI system that analyzes cloud usage and generates optimization recommendations using **Gemini API**, **MCP Server**, and **Streamlit dashboard**.

## 🎯 System Overview

```
Cloud APIs → MCP Server → Gemini AI Agent → Streamlit Dashboard
```

### Components

- **MCP Server**: Exposes tools for cloud usage, billing, and optimization rules
- **Gemini AI Agent**: Analyzes data and generates recommendations
- **Streamlit Dashboard**: Displays recommendations with approval interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone and setup environment:**

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_key_here
```

2. **Start MCP Server:**

```bash
python mcp_server.py
```

The server will start on `http://localhost:8000`
- API Docs: http://localhost:8000/docs

3. **Run AI Agent (standalone):**

```bash
python gemini_agent.py
```

This will:
- Fetch data from MCP server
- Analyze with Gemini AI
- Save recommendations to `recommendations.json`

4. **Launch Streamlit Dashboard:**

```bash
streamlit run streamlit_app.py
```

Dashboard will open at `http://localhost:8501`

## 🧠 AI Agent System Prompt

The Gemini agent uses this system instruction:

```
You are an autonomous Cloud Optimization AI Agent.

Objectives:
- Analyze cloud usage, billing, and performance metrics
- Identify inefficiencies and idle resources
- Recommend cost and performance optimizations
- Never violate SLAs
- Always estimate savings

Rules:
- Use MCP tools ONLY for data
- Never hallucinate metrics
- Output STRICT JSON
- Prefer reversible, low-risk actions
```

## 🛠️ MCP Server Endpoints

### Tools

- `GET /mcp/tools` - List all available tools
- `POST /mcp/tools/get_cloud_usage` - Fetch cloud usage metrics
- `POST /mcp/tools/get_cloud_cost` - Fetch billing data
- `POST /mcp/tools/get_optimization_rules` - Get optimization rules

### Context

- `POST /mcp/context` - Update MCP context
- `GET /mcp/context` - Get current context

### Example Usage

```bash
# Get cloud usage
curl -X POST http://localhost:8000/mcp/tools/get_cloud_usage \
  -H "Content-Type: application/json" \
  -d '{"provider": "gcp", "time_range": "last_30_days"}'

# Get billing data
curl -X POST http://localhost:8000/mcp/tools/get_cloud_cost \
  -H "Content-Type: application/json" \
  -d '{"provider": "gcp", "time_range": "last_30_days"}'
```

## 📊 Streamlit Dashboard Features

- **Executive Summary**: Overview of findings and potential savings
- **Recommendations Table**: Detailed optimization recommendations
- **Filtering**: By risk, priority, and resource type
- **Approval Interface**: Approve/reject recommendations
- **Data Export**: Download recommendations as CSV
- **Insights**: Additional AI-generated insights

## 🔐 Security & Governance

- **Read-only access**: MCP server uses read-only cloud IAM roles
- **No delete permissions**: Agent cannot delete resources
- **Human approval**: All actions require approval via Streamlit
- **Audit logs**: Execution history tracks all runs

## 📈 Optimization Logic

| Condition | Recommendation | Risk |
|-----------|---------------|------|
| CPU < 20% | Downsize VM | Low |
| Idle disk | Move to cold storage | Low |
| High egress | Optimize routing | Medium |
| Constant load | Reserved instances | Low |

## 🚀 Deployment Options

### Local Development
- MCP Server: `python mcp_server.py`
- Streamlit: `streamlit run streamlit_app.py`

### Production Deployment

| Component | Platform |
|-----------|----------|
| MCP Server | Docker / VM / Cloud Run |
| Streamlit | Streamlit Cloud / VM |
| Gemini API | Google AI Studio |

## 📦 Project Structure

```
.
├── mcp_server.py          # MCP Server (FastAPI)
├── gemini_agent.py        # Gemini AI Agent
├── streamlit_app.py       # Streamlit Dashboard
├── requirements.txt       # Python Dependencies
├── .env.example           # Environment Template
└── README.md              # This file
```

## 🔄 Integration with Real Cloud APIs

To connect to real cloud providers:

1. **AWS**: Use boto3
2. **GCP**: Use google-cloud-monitoring, google-cloud-billing
3. **Azure**: Use azure-mgmt-monitor, azure-mgmt-costmanagement

Example for GCP:

```python
from google.cloud import monitoring_v3
from google.cloud import billing_v1

# In mcp_server.py, replace mock data with:
client = monitoring_v3.MetricServiceClient()
# Fetch real metrics...
```

## 📝 Output Format

Recommendations are saved as JSON:

```json
{
  "summary": "Multiple underutilized compute instances found",
  "total_potential_savings": "$185.00/month",
  "recommendations": [
    {
      "resource_id": "vm-prod-gcp-01",
      "resource_type": "compute",
      "issue": "CPU usage below 20%",
      "current_state": "CPU: 15.5% avg, Memory: 32.1%",
      "action": "Downsize machine type from n1-standard-4 to n1-standard-2",
      "estimated_savings": "$110/month",
      "risk": "low",
      "priority": "high",
      "implementation_effort": "low"
    }
  ],
  "insights": [
    "3 compute instances show underutilization",
    "Storage costs are within acceptable range"
  ]
}
```

## 🎓 Academic Use

This project is suitable for:
- **Final Year Projects**: Complete system with AI, automation, and UI
- **Research**: Cloud optimization using AI agents
- **Startup MVP**: Production-ready foundation

## 🔥 Next Steps

- [ ] Add real cloud API integrations (AWS/GCP/Azure)
- [ ] Implement forecasting and anomaly detection
- [ ] Add multi-cloud support
- [ ] Create automated approval workflows
- [ ] Add cost tracking and ROI calculations
- [ ] Implement notification system (email/Slack)

## 📄 License

MIT License - Feel free to use for academic or commercial purposes.

## 🤝 Contributing

Contributions welcome! Please open issues or pull requests.

## 📧 Support

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ using Gemini AI, MCP, and Streamlit**
