import requests

api = 'http://127.0.0.1:8000/api/auth/'
response = requests.post(url=api, data={'username': 'lena', 'pwd': '123'})
print(response.text)
response = requests.post(url=api, data={'username': 'dada', 'pwd': 'Iamdada811'})
print(response.text)

index = response.text.find("token")
tk=response.text[index+9:-2]
print(tk);
api2 = 'http://127.0.0.1:8000/api/video'
response2 = requests.get(url=api2, params={'tk': tk})
print(response2.text)


# Create your tests here.
