import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def fetch_discovery_data():
    server_params = StdioServerParameters(command="python", args=["server.py"])
    
    # Senior Quant Portfolio: High Liquidity + High Volatility
    symbols = ["EURUSD", "GBPUSD", "USDJPY", "US100.cash", "US30.cash"]
    timeframes = ["M5"]
    limit = 50000

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to MCP. Starting Discovery Data Fetch...")
            
            for symbol in symbols:
                for tf in timeframes:
                    print(f"Fetching {limit} bars for {symbol} on {tf}...")
                    try:
                        result = await session.call_tool("data_fetch_candles", 
                                                        {"symbol": symbol, "timeframe": tf, "limit": limit})
                        
                        filename = f"{symbol}_{tf}_discovery.txt"
                        with open(filename, "w") as f:
                            f.write(result.content[0].text)
                        print(f"Saved: {filename}")
                    except Exception as e:
                        print(f"Failed to fetch {symbol} {tf}: {e}")

if __name__ == "__main__":
    asyncio.run(fetch_discovery_data())