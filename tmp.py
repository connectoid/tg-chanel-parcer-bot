import requests

headers = {
    'RqUID': '6f0b1291-c7f3-43c6-bb2e-9f3efb2dc98e',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json',
    'Authorization': 'Basic ODIzMGU4YzktMmZhZS00MzZhLTlmNjItMWNjNWE4YzMzN2Q4OmIyMjkyODlkLTRhZDctNDdmYS1iZjYzLTBmOWZjYTFkYmI0OQ==',
}

data = {
    'scope': 'GIGACHAT_API_PERS',
}

response = requests.post(
    'https://ngw.devices.sberbank.ru:9443/api/v2/oauth',
    headers=headers,
    data=data,
    verify=False
)

print(response.status_code)
print(response.text)