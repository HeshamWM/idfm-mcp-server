#!/usr/bin/env python3
"""
Simple Île-de-France Mobilités MCP Server - Access Paris public transport real-time data
"""
import os
import sys
import logging
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("idfm-server")

# Initialize MCP server
mcp = FastMCP("idfm")

# Configuration
def get_api_key():
    """Get API key from environment or Docker secret file."""
    # First try environment variable
    api_key = os.environ.get("IDFM_API_KEY", "")
    if api_key:
        return api_key
    
    # Then try Docker MCP secret file
    secret_file = os.environ.get("IDFM_API_KEY_FILE", "")
    if secret_file and os.path.exists(secret_file):
        try:
            with open(secret_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read API key from {secret_file}: {e}")
    
    return ""

API_KEY = get_api_key()
BASE_URL = "https://prim.iledefrance-mobilites.fr/marketplace"
TIMEOUT = 30.0

# === UTILITY FUNCTIONS ===

def get_headers():
    """Get headers with API key."""
    if not API_KEY:
        logger.warning("IDFM_API_KEY not set")
    return {
        "apikey": API_KEY,
        "Accept": "application/json"
    }

def format_datetime(dt_string):
    """Format datetime string to readable format."""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime('%H:%M:%S')
    except:
        return dt_string

# === MCP TOOLS ===

@mcp.tool()
async def get_next_departures(stop_id: str = "", max_results: str = "10") -> str:
    """Get real-time next departures for a specific stop in Paris transport network."""
    logger.info(f"Getting next departures for stop {stop_id}")
    
    if not stop_id.strip():
        return "❌ Error: stop_id is required. Use search_stops to find stop IDs."
    
    if not API_KEY:
        return "❌ Error: IDFM_API_KEY not configured. Set your API token in Docker secrets."
    
    try:
        max_int = int(max_results) if max_results.strip() else 10
        if max_int < 1 or max_int > 50:
            max_int = 10
    except ValueError:
        max_int = 10
    
    url = f"{BASE_URL}/stop-monitoring"
    params = {
        "MonitoringRef": stop_id
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=get_headers(), params=params, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            # Parse SIRI Lite response
            siri = data.get("Siri", {})
            delivery = siri.get("ServiceDelivery", {})
            monitoring = delivery.get("StopMonitoringDelivery", [])
            
            if not monitoring:
                return f"❌ No departure data found for stop: {stop_id}"
            
            visits = monitoring[0].get("MonitoredStopVisit", [])
            
            if not visits:
                return f"ℹ️ No upcoming departures found for stop: {stop_id}"
            
            result = f"🚇 Next Departures for Stop {stop_id}\n\n"
            
            for i, visit in enumerate(visits[:max_int]):
                journey = visit.get("MonitoredVehicleJourney", {})
                line_ref = journey.get("LineRef", {}).get("value", "Unknown")
                destination = journey.get("DestinationName", [{}])[0].get("value", "Unknown")
                
                call = journey.get("MonitoredCall", {})
                expected_time = call.get("ExpectedDepartureTime", "")
                aimed_time = call.get("AimedDepartureTime", "")
                
                time_display = format_datetime(expected_time) if expected_time else format_datetime(aimed_time)
                
                result += f"{i+1}. Line {line_ref} → {destination}\n"
                result += f"   ⏰ Departure: {time_display}\n\n"
            
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        return f"❌ API Error: {e.response.status_code} - {e.response.text[:200]}"
    except httpx.TimeoutException:
        return "⏱️ Request timed out. Please try again."
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def search_stops(query: str = "", limit: str = "10") -> str:
    """Search for transport stops by name or location in Paris region. NOTE: This endpoint is currently not available in the IDFM PRIM API."""
    logger.info(f"Searching stops with query: {query}")
    
    return "❌ Error: The search_stops functionality is not available in the current IDFM PRIM API. \nThe API only supports SIRI endpoints for real-time data, not NavItia-style place searches. \nYou'll need to use known stop IDs or find them through other means."


@mcp.tool()
async def search_routes(from_place: str = "", to_place: str = "", datetime_param: str = "") -> str:
    """Calculate journey itineraries between two places in Paris transport network. NOTE: This endpoint is not available in the current IDFM PRIM API."""
    logger.info(f"Searching routes from {from_place} to {to_place}")
    
    return "❌ Error: The search_routes functionality is not available in the current IDFM PRIM API. \nThe API only supports SIRI endpoints for real-time monitoring data, not NavItia-style journey planning. \nFor route planning, you'll need to use other services like Citymapper, Google Maps, or the official IDFM mobile app."


@mcp.tool()
async def get_traffic_info(line_id: str = "") -> str:
    """Get real-time traffic disruptions and messages for Paris transport lines."""
    logger.info(f"Getting traffic info for line: {line_id}")
    
    if not API_KEY:
        return "❌ Error: IDFM_API_KEY not configured."
    
    url = f"{BASE_URL}/general-message"
    params = {}
    
    if line_id.strip():
        params["LineRef"] = line_id.strip()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=get_headers(), params=params, timeout=TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            siri = data.get("Siri", {})
            delivery = siri.get("ServiceDelivery", {})
            messages = delivery.get("GeneralMessageDelivery", [])
            
            if not messages:
                return "ℹ️ No traffic messages available."
            
            info_messages = messages[0].get("InfoMessage", [])
            
            if not info_messages:
                if line_id.strip():
                    return f"✅ No disruptions for line: {line_id}"
                return "✅ No current disruptions on the network."
            
            result = "🚦 Traffic Information\n\n"
            
            for i, msg in enumerate(info_messages):
                content = msg.get("Content", {})
                message_text = content.get("Message", [{}])[0].get("MessageText", {}).get("value", "No details")
                
                affected = msg.get("InfoMessageIdentifier", {})
                line_ref = affected.get("InfoChannelRef", {}).get("value", "Network")
                
                result += f"{i+1}. Line/Network: {line_ref}\n"
                result += f"   ℹ️ {message_text}\n\n"
            
            return result
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        return f"❌ API Error: {e.response.status_code}"
    except Exception as e:
        logger.error(f"Error: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_line_info(line_id: str = "") -> str:
    """Get detailed information about a specific transport line in Paris region. NOTE: This endpoint is not available in the current IDFM PRIM API."""
    logger.info(f"Getting line info for: {line_id}")
    
    return "❌ Error: The get_line_info functionality is not available in the current IDFM PRIM API. \nThe API only supports SIRI endpoints for real-time data, not NavItia-style line information. \nFor line information, please use the official IDFM website or mobile app."


# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Île-de-France Mobilités MCP server...")
    
    if not API_KEY:
        logger.warning("⚠️ IDFM_API_KEY not set - tools will not work without API key")
    else:
        logger.info("✅ API key configured")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)