# Simplified Deribit Market Maker. Please adjust for your own use.

import asyncio
import websockets
import json

spread = 50 #dollar spread

refresh_token = ""
expires_in = 0
access_token = ""

msg = \
{
  "jsonrpc" : "2.0",
  "id" : 42,
  "method" : "public/auth",
  "params" : {
    "grant_type" : "client_credentials",
    "client_id" : "deribit-api-key",
    "client_secret" : "deribit-api-secret"
  }
}

async def call_api(msg):
   async with websockets.connect('wss://www.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       
       while websocket.open:
           response = json.loads(await websocket.recv())
           #print(response)
           if "result" in response:
             result = response["result"]
             #print(result)
             if "access_token" in result:
               access_token = result["access_token"]
               #print(access_token)
               msg1 = {"jsonrpc": "2.0","method": "private/subscribe", "id": 42, "params": {"access_token":access_token, "channels": ["user.orders.BTC-PERPETUAL.raw"]} }
               await websocket.send(json.dumps(msg1))
           if "params" in response:
             params = response["params"]
             if "data" in params:
               data = params["data"]
               #print(data)
               order_state = data["order_state"]
               order_type = data["order_type"]
               if order_state == "filled" and order_type != "stop_limit":
                 price = data["price"]
                 direction = data["direction"]
                 qty = data["amount"]
                 msg2=msg1
                 if direction == "buy":
                   sellprice = price + spread 
                   msg2 = {"jsonrpc": "2.0","method": "private/sell", "id": 42, "params": {"access_token":access_token, "instrument_name" : "BTC-PERPETUAL", "amount" : qty, "type" : "limit","price":sellprice,"post_only":True} }
                 if direction == "sell":
                   buyprice = price - spread
                   msg2 = {"jsonrpc": "2.0","method": "private/buy", "id": 42, "params": {"access_token":access_token, "instrument_name" : "BTC-PERPETUAL", "amount" : qty, "type" : "limit","price":buyprice,"post_only":True} }
                 await websocket.send(json.dumps(msg2))
           
loop = asyncio.get_event_loop()
loop.run_until_complete(call_api(json.dumps(msg)))
loop.run_forever()

