import requests

from django.contrib.auth import get_user_model


def get_linkedin_user_details(user):
    try:
        linkedin_social = user.socialaccount_set.get(provider="linkedin")
    except:
        raise Exception("LinkedIn is not connected on this user.")
    return linkedin_social

def get_share_headers(linkedin_social):
    tokens = linkedin_social.socialtoken_set.all()
    if not tokens.exists():
        raise Exception("LinkedIn connection is invalid. Please login again.")
    social_token = tokens.first()
    return {
        "Authorization": f"Bearer {social_token.token}",
        "X-Restli-Protocol-Version": "2.0.0"
    }


def post_to_linkedin(user, text:str):
    User = get_user_model()
    if not isinstance(user, User):
        raise Exception("Must be a user")
    linkedin_social = get_linkedin_user_details(user)
    linkedin_user_id = linkedin_social.uid
    if not linkedin_user_id:
        raise Exception("Invalid LinkedIn User Id")
    headers = get_share_headers(linkedin_social)
    endpoint = "https://api.linkedin.com/v2/ugcPosts"
    payload = {
        "author": f"urn:li:person:{linkedin_user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": f"{text}"
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    response = requests.post(endpoint, json=payload, headers=headers)
    try:
        response.raise_for_status()
    except:
        raise Exception("Invalid post, please try again later")
    return response