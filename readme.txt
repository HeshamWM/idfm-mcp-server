# Île-de-France Mobilités MCP Server

A Model Context Protocol (MCP) server that provides access to real-time Paris public transport data through the PRIM API.

## Purpose

This MCP server provides a secure interface for AI assistants to access real-time information about the Paris public transport network (Île-de-France Mobilités), including metros, RER, buses, trams, and trains.

## Features

### Current Implementation

- **`get_next_departures`** - Get real-time departure times for a specific stop/station
- **`search_stops`** - Search for transport stops by name or location to find their IDs
- **`search_routes`** - Calculate journey itineraries between two places
- **`get_traffic_info`** - Get real-time traffic disruptions and service messages
- **`get_line_info`** - Get detailed information about a specific transport line

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp` command)
- PRIM API key from https://prim.iledefrance-mobilites.fr/

## Installation

See the step-by-step instructions provided with the files.

## Usage Examples

In Claude Desktop, you can ask:

- "What are the next trains at Châtelet station?"
- "Search for stops near Gare de Lyon"
- "How do I get from Charles de Gaulle Étoile to La Défense?"
- "Are there any disruptions on Metro Line 1?"
- "Show me information about RER A"
- "When is the next bus at stop XYZ?"

### Finding Stop IDs

Before using `get_next_departures`, you need to find the stop ID:
1. Use `search_stops` with the station name
2. Copy the ID from the results
3. Use that ID with `get_next_departures`

Example flow:
- "Search for Châtelet stops" → Get stop ID
- "Get next departures for stop:IDFM:12345" → See departure times

## Architecture
```
Claude Desktop → MCP Gateway → IDFM MCP Server → PRIM API
                     ↓
         Docker Desktop Secrets
              (IDFM_API_KEY)
```

## API Details

- **Base URL**: https://prim.iledefrance-mobilites.fr/marketplace
- **Authentication**: API key via `apiKey` header
- **Rate Limits**: 
  - Next Departures: 1,000,000 requests/day
  - Generic Access: 20,000 requests/day

## Development

### Local Testing
```bash
# Set environment variables for testing
export IDFM_API_KEY="your-api-key-here"

# Run directly
python idfm_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python idfm_server.py
```

### Adding New Tools

1. Add the function to `idfm_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

## Troubleshooting

### Tools Not Appearing

- Verify Docker image built successfully: `docker images | grep idfm`
- Check catalog and registry files
- Ensure Claude Desktop config includes custom catalog
- Restart Claude Desktop completely

### Authentication Errors

- Verify secret is set: `docker mcp secret list`
- Ensure secret name is exactly `IDFM_API_KEY`
- Check that your API key is valid on the PRIM portal

### No Results Returned

- Stop IDs must be exact (use search_stops first)
- Some stops may not have real-time data available
- Check if the service is running (weekends/holidays may have different schedules)

## Common Stop ID Formats

- Metro stations: `stop_area:IDFM:xxxxx`
- RER stations: Similar format with different codes
- Bus stops: Various formats depending on operator

Use `search_stops` to find the correct ID format.

## Security Considerations

- All API keys stored in Docker Desktop secrets
- Never hardcode credentials in the code
- Running as non-root user in container
- API key never logged or exposed

## Resources

- PRIM API Portal: https://prim.iledefrance-mobilites.fr/
- API Documentation: Available after registration
- Île-de-France Mobilités: https://www.iledefrance-mobilites.fr/

## License

MIT License