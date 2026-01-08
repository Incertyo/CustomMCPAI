# Dockerfile for MCP Server
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY mcp_server.py .
COPY gemini_agent.py .

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "mcp_server.py"]
