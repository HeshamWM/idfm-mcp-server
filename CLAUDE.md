# CLAUDE.md - Île-de-France Mobilités MCP Server Implementation Guide

## Overview

This MCP server provides Claude Desktop with access to the Paris public transport network (Île-de-France Mobilités) through the PRIM API.

## Implementation Details

### API Integration

The server integrates with the PRIM (Platform for Regional Information on Mobility) API which provides:

1. **SIRI Lite API** - Real-time departures (`/stop-monitoring`)
2. **Navitia API** - Journey planning and search (`/v2/navitia/`)
3. **General Messages API** - Traffic disruptions (`/general-message`)

### Authentication

- Uses API key authentication via HTTP header `apiKey`
- API key stored securely in Docker Desktop secrets as `IDFM_API_KEY`
- Key obtained from: https://prim.iledefrance-mobilites.fr/

### Tools Implemented

#### 1. get_next_departures
- **Purpose**: Get real-time departure times for a specific stop
- **Input**: Stop ID (from search_stops), optional max results
- **Output**: List of next departures with line, destination, and time
- **API**: SIRI Lite Stop Monitoring endpoint

#### 2. search_stops
- **Purpose**: Find stop IDs by searching for station names
- **Input**: Search query (station name or location)
- **Output**: List of matching stops with IDs and coordinates
- **API**: Navitia Places endpoint
- **Note**: Essential for finding stop IDs needed by get_next_departures

#### 3. search_routes
- **Purpose**: Calculate journey itineraries between two locations
- **Input**: From location, to location, optional datetime
- **Output**: Multiple journey options with transfers and timings
- **API**: Navitia Journeys endpoint
- **Formats**: Can use coordinates (lat;lon) or place IDs

#### 4. get_traffic_info
- **Purpose**: Get real-time service disruptions and messages
- **Input**: Optional line ID to filter
- **Output**: List of current disruptions and service messages
- **API**: SIRI Lite General Message endpoint

#### 5. get_line_info
- **Purpose**: Get detailed information about a transport line
- **Input**: Line ID
- **Output**: Line details, routes, and directions
- **API**: Navitia Lines endpoint

### Data Formats

#### Stop IDs
- Format: `stop_area:IDFM:xxxxx`
- Must be exact (obtained via search_stops)

#### Line IDs
- Format: `line:IDFM:Cxxxxx`
- Examples: Metro Line 1 = `line:IDFM:C01371`

#### Coordinates
- Format: `{longitude};{latitude}`
- Example: `2.3522;48.8566` (Paris center)

### Error Handling

All tools include comprehensive error handling for:
- Missing API key
- Invalid parameters
- HTTP errors (4xx, 5xx)
- Timeout errors
- JSON parsing errors
- Empty results

### Rate Limits

The PRIM API has the following limits:
- Stop Monitoring: 1,000,000 requests/day
- Navitia APIs: 20,000 requests/day

The server does not implement rate limiting internally but logs all requests.

### Logging

- All operations logged to stderr (Docker best practice)
- Log level: INFO for normal operations, ERROR for failures
- Logs include: tool calls, API responses, errors

### Best Practices for Claude

When using these tools:

1. **Always search first**: Use `search_stops` before `get_next_departures`
2. **Use exact IDs**: Stop and line IDs must be exact
3. **Handle French names**: Many stations have French names with accents
4. **Check for errors**: Tools return error messages with ❌ prefix
5. **Combine tools**: Search stops → Get departures → Check traffic info

### Example Workflow
```
User: "When is the next metro at Châtelet?"

1. search_stops(query="Châtelet")
   → Returns stop ID: stop_area:IDFM:71234

2. get_next_departures(stop_id="stop_area:IDFM:71234")
   → Returns next 10 departures

3. (Optional) get_traffic_info()
   → Check for any disruptions
```

### Known Limitations

1. **Real-time data availability**: Not all stops have real-time data
2. **Service hours**: No departures returned outside service hours
3. **Stop ID variations**: Some stations have multiple stop IDs (different platforms)
4. **API response time**: Can be slow during peak hours (timeout set to 30s)

### Future Enhancements

Possible additions:
- Station accessibility information
- Bike availability at Vélib stations
- Park & Ride availability
- Multi-modal journey options
- Favorite stops/routes storage
- Historical disruption data

### Troubleshooting Guide

**Problem**: "No departures found"
- **Solution**: Check if stop ID is correct, verify service hours

**Problem**: API timeout
- **Solution**: Retry request, check PRIM API status

**Problem**: Invalid stop ID
- **Solution**: Use search_stops to find correct ID

**Problem**: Authentication error
- **Solution**: Verify IDFM_API_KEY secret is set correctly

### Security Notes

- API key never exposed in responses or logs
- All external API calls use HTTPS
- No user data stored locally
- Running as non-root user in container

### Testing

Test the server with these commands:
```bash
# Test API connectivity
curl -H "apiKey: YOUR_KEY" \
  "https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/coverage"

# Test stop search
# Via Claude: "Search for stops near Gare du Nord"

# Test departures
# Via Claude: "Get next departures for stop_area:IDFM:XXXXX"
```

## Maintenance

- Keep httpx and mcp dependencies updated
- Monitor PRIM API changelog for breaking changes
- Check Docker MCP Toolkit updates
- Review logs for common errors

## Support

- PRIM API Issues: Contact support via PRIM portal
- MCP Server Issues: Check Docker MCP documentation
- Integration Issues: Review Claude Desktop logs