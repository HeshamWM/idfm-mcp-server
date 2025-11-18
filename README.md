# Île-de-France Mobilités MCP Server

A **Model Context Protocol (MCP) server** that provides AI assistants with access to real-time Paris public transport data through the IDFM PRIM API.

## 🚇 Overview

This Docker-based MCP server enables AI assistants like Claude to access live information about the Paris public transport network (métro, RER, bus, tram, Transilien trains) managed by Île-de-France Mobilités.

### Key Features

- **Real-time Departures**: Get next departure times for any transport stop
- **Traffic Disruptions**: Monitor service alerts and disruptions across the network
- **Docker Integration**: Runs as a containerized MCP server with Docker Desktop
- **Secure API Management**: Uses Docker MCP Toolkit's secret management
- **SIRI Protocol Support**: Compatible with the official IDFM PRIM API

## 🛠️ Technologies

- **Python 3.11** with FastMCP framework
- **Docker** containerization with multi-stage builds
- **SIRI (Service Interface for Real Time Information)** protocol
- **HTTPX** for async HTTP requests
- **Model Context Protocol** for AI assistant integration

## 📋 Available Tools

| Tool | Status | Description |
|------|--------|-------------|
| `get_next_departures` | ✅ Working | Real-time departure times for specific stops |
| `get_traffic_info` | ✅ Working | Service disruptions and network messages |
| `search_stops` | ❌ Limited API | Stop search (API limitations explained) |
| `search_routes` | ❌ Limited API | Journey planning (API limitations explained) |
| `get_line_info` | ❌ Limited API | Line information (API limitations explained) |

## 🚀 Quick Start

### Prerequisites

- Docker Desktop with MCP Toolkit enabled
- IDFM PRIM API key from [prim.iledefrance-mobilites.fr](https://prim.iledefrance-mobilites.fr/)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd idfm-mcp-server
   ```

2. **Set up your API key**
   ```bash
   docker mcp secret set IDFM_API_KEY=your-api-key-here
   ```

3. **Build the Docker image**
   ```bash
   docker build -t idfm-mcp-server .
   ```

4. **Test the server**
   ```bash
   echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | \
   docker run --rm -i -l x-secret:IDFM_API_KEY=/tmp/api_key.txt -e IDFM_API_KEY_FILE=/tmp/api_key.txt idfm-mcp-server
   ```

## 💡 Usage Examples

### With Claude Desktop

Ask natural language questions like:
- *"What are the next trains at Châtelet station?"*
- *"Are there any disruptions on the RER A line?"*
- *"Show me departure times for stop STIF:StopPoint:Q:41304:"*

### Direct API Calls

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_next_departures",
    "arguments": {
      "stop_id": "STIF:StopPoint:Q:41304:",
      "max_results": "5"
    }
  },
  "id": 1
}
```

## 🔧 Configuration

### Docker MCP Secrets

The server reads the API key from Docker MCP secrets:

```bash
# Set the secret
docker mcp secret set IDFM_API_KEY=your-key-here

# Run with secret mounting
docker run -l x-secret:IDFM_API_KEY=/tmp/api_key.txt -e IDFM_API_KEY_FILE=/tmp/api_key.txt idfm-mcp-server
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `IDFM_API_KEY` | Direct API key (fallback) | Empty |
| `IDFM_API_KEY_FILE` | Path to API key file | Empty |

## 🏗️ Architecture

```
Claude Desktop → MCP Protocol → Docker Container → IDFM PRIM API
                      ↓
              Docker MCP Secrets
```

The server implements the MCP protocol to provide a secure, standardized interface between AI assistants and the IDFM transport data.

## 📊 API Limitations

The IDFM PRIM API has evolved and currently supports:

- ✅ **SIRI Protocol**: Real-time monitoring and disruption data
- ❌ **NavItia Protocol**: Historical search endpoints have been deprecated

This server provides honest error messages explaining these limitations and suggests alternatives for unavailable functionality.

## 🔒 Security

- API keys stored securely in Docker MCP secrets
- Non-root user execution in container
- No API key logging or exposure
- Rate limiting awareness (1M requests/day for monitoring)

## 🐛 Troubleshooting

### Common Issues

**Tools not appearing in Claude:**
- Verify Docker image built successfully: `docker images | grep idfm`
- Check MCP server registration
- Restart Claude Desktop

**Authentication errors:**
- Verify secret: `docker mcp secret ls`
- Ensure API key is valid at PRIM portal
- Check container has secret access

**No departure data:**
- Verify stop ID format (use SIRI format: `STIF:StopPoint:Q:XXXXX:`)
- Some stops may not have real-time data
- Check service schedules (reduced on weekends/holidays)

### Stop ID Formats

The API requires specific SIRI-compliant stop IDs:
- ✅ `STIF:StopPoint:Q:41304:` (Châtelet-Les Halles)
- ❌ `stop_area:IDFM:71571` (Old NavItia format)

## 📈 Rate Limits

- **Stop Monitoring**: 1,000,000 requests/day
- **General Access**: 20,000 requests/day

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with real API data
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Resources

- [IDFM PRIM API Portal](https://prim.iledefrance-mobilites.fr/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Docker MCP Toolkit Documentation](https://docs.docker.com/desktop/mcp/)
- [Île-de-France Mobilités](https://www.iledefrance-mobilites.fr/)

## 📞 Support

For API-related issues, contact IDFM support. For server issues, please open a GitHub issue.

---

*Built with ❤️ for the Paris public transport community*