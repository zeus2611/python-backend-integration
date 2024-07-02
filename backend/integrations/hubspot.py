import json
import secrets
import base64
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
from datetime import datetime
from integrations.integration_item import IntegrationItem
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

CLIENT_ID = 'your-client-id'
CLIENT_SECRET = 'your-client-secret'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
SCOPE = 'crm.objects.contacts.read%20crm.objects.contacts.write%20crm.schemas.contacts.read%20crm.schemas.contacts.write'
AUTHORIZATION_URL = (
    f'https://app.hubspot.com/oauth/authorize?client_id={CLIENT_ID}'
    f'&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
)
TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'

async def authorize_hubspot(user_id: str, org_id: str) -> str:
    """Initiates the HubSpot OAuth2 flow. Returns the URL to which the user should be redirected."""
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }

    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', encoded_state, expire=600)
    auth_url = f'{AUTHORIZATION_URL}&state={encoded_state}'

    return auth_url

async def oauth2callback_hubspot(request: Request):
    """Callback function for HubSpot OAuth2 flow. This function is called by HubSpot after the user has authorized the app."""
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error'))
    
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')
    if not saved_state or original_state != json.loads(base64.urlsafe_b64decode(saved_state).decode('utf-8')).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'redirect_uri': REDIRECT_URI,
                    'code': code,
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                }
            ),
            delete_key_redis(f'hubspot_state:{org_id}:{user_id}')
        )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)

    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id: str, org_id: str) -> dict:
    """Retrieves the stored HubSpot credentials from Redis and deletes them afterwards."""
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')

    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    
    credentials = json.loads(credentials)
    await delete_key_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return credentials

async def get_items_hubspot(credentials) -> list[IntegrationItem]:
    """Aggregates all metadata relevant for a HubSpot integration"""
    credentials = json.loads(credentials)
    headers = {
        'Authorization': f'Bearer {credentials.get("access_token")}',
        'Content-Type': 'application/json'
    }
    
    items = []
    url = 'https://api.hubapi.com/crm/v3/objects/contacts'
    params = {'limit': 100}

    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                break
            
            data = response.json()
            contacts = data.get('results', [])
            for contact in contacts:
                # Creating an IntegrationItem for each contact
                item = IntegrationItem(
                    id=contact.get("id"),
                    type="contact",
                    name=(
                        (contact.get("properties", {}).get("firstname", "") or "") + " " +
                        (contact.get("properties", {}).get("lastname", "") or "")
                    ).strip(),
                    creation_time=datetime.strptime(contact.get("properties", {}).get("createdate"), "%Y-%m-%dT%H:%M:%S.%fZ") if contact.get("properties", {}).get("createdate") else None,
                    last_modified_time=datetime.strptime(contact.get("properties", {}).get("lastmodifieddate"), "%Y-%m-%dT%H:%M:%S.%fZ") if contact.get("properties", {}).get("lastmodifieddate") else None,
                    parent_id=None,
                    parent_path_or_name=None,
                    url=f"https://app.hubspot.com/contacts/{contact.get('id')}",
                )
                items.append(item)
            
            # Check if there's a next page
            if 'paging' in data and 'next' in data['paging']:
                params['after'] = data['paging']['next']['after']
            else:
                break

            print(f"Total contacts fetched: {len(items)}")
    print(items)
    return items

# async def get_items_hubspot(credentials) -> list[IntegrationItem]:
#     """Aggregates all metadata relevant for a HubSpot integration"""
#     credentials = json.loads(credentials)
#     headers = {
#         'Authorization': f'Bearer {credentials.get("access_token")}',
#         'Content-Type': 'application/json'
#     }
    
#     items = []
    
#     # Fetch contacts
#     url = 'https://api.hubapi.com/crm/v3/objects/contacts'
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url, headers=headers)
#         if response.status_code == 200:
#             contacts = response.json().get('results', [])
#             for contact in contacts:
#             # Creating an IntegrationItem for each contact
#                 item = IntegrationItem(
#                     id=contact.get("id"),
#                     type="contact",
#                     name=(
#                         (contact.get("properties", {}).get("firstname", "") or "") + " " +
#                         (contact.get("properties", {}).get("lastname", "") or "")
#                     ).strip(),
#                     creation_time=datetime.strptime(contact.get("properties", {}).get("createdate"), "%Y-%m-%dT%H:%M:%S.%fZ") if contact.get("properties", {}).get("createdate") else None,
#                     last_modified_time=datetime.strptime(contact.get("properties", {}).get("lastmodifieddate"), "%Y-%m-%dT%H:%M:%S.%fZ") if contact.get("properties", {}).get("lastmodifieddate") else None,
#                     parent_id=None,
#                     parent_path_or_name=None,
#                     url=f"https://app.hubspot.com/contacts/{contact.get('id')}",
#                 )
#                 items.append(item)
#             print(f"Length of contacts: {len(contacts)}")
#             print(items)

#     return items