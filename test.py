import httpx

webhook = httpx.get("https://cloud.xvirus.lol/secret/secret.txt")

print(webhook.text)