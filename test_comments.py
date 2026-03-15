import requests

token = "EAARghOXjjywBQ9tsNTTXIf53TtFRE1Q9yjEHS7AVzmRNAql8jeelCRkgucPz4NiwRFBhe2ZAF6eREgLaweHZB4u8N7ZATIGVO6StYOAZCmUpKVroPO0UJn6kMAeJ7lCMqX1ZAcquwnxe8JaIPQhFeImlGjrkRuPoGZCG0J4CCnNsAB6yxdtV7udyaxBwQg7RWZAkRzerEzBkRZBzejehrVBZB"

print("=== Checking comments on the INFO post ===")
post_id = "684298664768779_122163985976925582"
r = requests.get(
    f"https://graph.facebook.com/v19.0/{post_id}/comments",
    params={"access_token": token, "fields": "id,message,from", "limit": 20}
)
data = r.json()
comments = data.get("data", [])
print(f"Total comments found: {len(comments)}")
for c in comments:
    print(f"  from: {c.get('from')} | message: {c.get('message','')[:40]}")

if "error" in data:
    print(f"Error: {data['error']}")