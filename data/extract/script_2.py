# from websocket import create_connection
#
# ws = create_connection('wss://stream.lunarcrush.com/v2')
# ws.send('auth:1zvvnmdp02bakszho0e48m') # must authenticate using command: auth:<api_key>
#
# ws.send('subscribe:btc')
#
# while True:
#     result = ws.recv()
#     print(f'Received: {result}')
#

# import websocket
#
#
# def on_message(wsapp, message):
#     print(message)
#
#
# wsapp = websocket.WebSocketApp('wss://stream.lunarcrush.com/v2', on_message=on_message)
# # wsapp.send('subscribe:btc')
# wsapp.run_forever()

import asyncio
import websockets


async def hello():
    uri = "wss://stream.lunarcrush.com/v2"
    async with websockets.connect(uri) as websocket:
        # name = input("What's your name? ")

        await websocket.send('auth:1zvvnmdp02bakszho0e48m')
        # print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

asyncio.get_event_loop().run_until_complete(hello())
