import requests,json
 
data = {
    'id': 1,
    'suggest_1':'san SIKL',
}
 
resp = requests.post('http://localhost:5050/save-data', data = json.dumps(data))
print(resp.content.decode('utf-8'))