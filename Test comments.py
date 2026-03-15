import requests

token = "EAARghOXjjywBQ45tbhF06WIHhkLbKSyV6QUqA4bmL4bTITazbrfIpdZAKPU77dYWZCLsbSvVzHc01ZC2QjS4FXeSsr7zjZBttyqqTr4Q6YUtB3TZBvRNVB6MJZCW0c8aHOgG8dGc8OZBK1oB5CtWOZCQ8vPZBB81Iu2CrzzymWxnlRHrDkRd8ZCtFNMwXRiEonsb0J01ckiM2982saU897itMgPqhOV8UC1ebvafhNW1dC1DIugtoIZBZCQHUd69"

# Get latest post
r = requests.get(
    "https://graph.facebook.com/v19.0/684298664768779/posts",
    params={"access_token": token, "fields": "id,message", "limit": 1}
)
data = r.json()
print("Posts response:", data)

if "data" in data and data["data"]:
    post_id = data["data"][0]["id"]
    print("Post ID:", post_id)

    # Get comments with from field
    r2 = requests.get(
        f"https://graph.facebook.com/v19.0/{post_id}/comments",
        params={"access_token": token, "fields": "id,message,from", "limit": 5}
    )
    print("Comments response:", r2.json())
else:
    print("No posts found or error")