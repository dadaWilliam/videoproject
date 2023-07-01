# # consumers.py
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json


# class NotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Generate a unique identifier for this client
#         self.client_id = str(uuid.uuid4())

#         # Join a group specific to this client
#         await self.channel_layer.group_add(f"client-{self.client_id}", self.channel_name)

#         # Accept the connection
#         await self.accept()

#         # Send the client_id back to the client
#         await self.send(text_data=json.dumps({
#             'client_id': self.client_id,
#         }))

#     async def disconnect(self, close_code):
#         # Leave the client's group
#         await self.channel_layer.group_discard(f"client-{self.client_id}", self.channel_name)

#     # Receive a message from the channel layer
#     async def login(self, event):
#         # Send a message to the WebSocket with the client_id
#         await self.send(text_data=json.dumps({
#             'message': f"Client {event['client_id']} authenticated. Please login.",
#         }))
