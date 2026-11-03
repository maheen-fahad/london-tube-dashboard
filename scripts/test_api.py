import requests

url = "https://api.tfl.gov.uk/Line/Mode/tube"
response = requests.get(url)
lines = response.json()

for line in lines:
    print(line["id"], "-", line["name"])