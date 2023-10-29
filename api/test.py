# This is an example where we run through the OAuth flow,
# select a business, and display a client from that business.

from types import SimpleNamespace
from freshbooks import Client as FreshBooksClient
import requests

FB_CLIENT_ID = "71f8d9e091f36ac5e40b8939b4793da813c3df51b45735271bb380ede4e903d9"
SECRET = "cc2bc7903a859510616d0582d60d4d8d6e86dffdc21838b9a39a20f1df559c10"
REDIRECT_URI = "https://nextjs-fastapi-starter-bay-seven.vercel.app/"

freshBooksClient = FreshBooksClient(
    client_id=FB_CLIENT_ID,
    client_secret=SECRET,
    redirect_uri=REDIRECT_URI
)

authorization_url = freshBooksClient.get_auth_request_url(
    scopes=['user:profile:read', 'user:projects:read', 'user:time_entries:read']
)
print(f"Go to this URL to authorize: {authorization_url}")
print()
print()
# Going to that URL will prompt the user to log into FreshBooks and authorize the application.
# Once authorized, FreshBooks will redirect the user to your `redirect_uri` with the authorization
# code will be a parameter in the URL.
auth_code = input("Enter the code you get after authorization: ")

# This will exchange the authorization code for an access token
token_response = freshBooksClient.get_access_token(auth_code)
print(token_response.access_token)

# print(f"This is the access token the client is now configurated with: {token_response.access_token}")
# print(f"It is good until {token_response.access_token_expires_at}")
# print()

# Get the current user's identity
identity = freshBooksClient.current_user()
print(identity.business_memberships)
businesses = []

# # Display all of the businesses the user has access to
for num, business_membership in enumerate(identity.business_memberships, start=1):
    business = business_membership.business
    businesses.append(
        SimpleNamespace(name=business.name, business_id=business.id, account_id=business.account_id)
    )
    print(f"{num}: {business.name} {business.id}")
# business_index = int(input("Which business do you want to use? ")) - 1

# business_id = businesses[business_index].business_id  # Used for project-related calls
# account_id = businesses[business_index].account_id  # Used for accounting-related calls

# # Get a client for the business to show successful access
# client = freshBooksClient.clients.list(account_id)[0]
# print(f"'{client.organization}' is a client of {businesses[business_index].name}")

# print(freshBooksClient.projects.get_single_project(12364599, 11763941).budget)

# token = token_response.access_token
base_url = "https://api.freshbooks.com"

# Define the headers for authorization and content type
data = {
    "grant_type": "authorization_code", 
    "client_id": FB_CLIENT_ID,
    "code": "auth_code",
    "client_secret": SECRET,
    "redirect_uri": REDIRECT_URI
}

endpoint = f"/auth/oauth/token"

# Make a GET request to the endpoint and store the response
response = requests.post(base_url + endpoint, json=data)
print(response.json())

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

business_id = 12364599
project_id = 11763941
# Define the endpoint for getting a single project
endpoint = f"/projects/business/{business_id}/project/{project_id}"

# Make a GET request to the endpoint and store the response
response = requests.get(base_url + endpoint, headers=headers)
# print(response.json())

endpoint = f"/timetracking/business/{business_id}/time_entries"
response = requests.get(base_url + endpoint, headers=headers)
# print(response.json())

endpoint = f"/auth/api/v1/users/me"
response = requests.get(base_url + endpoint, headers=headers)
# print(response.json())
# Check if the response status code is 200 (OK)
if response.status_code == 200:
    # Parse the response as JSON and get the project data
    data = response.json()
    
else:
    # Print an error message if the response status code is not 200 (OK)
    print(f"An error occurred: {response.status_code}")

    print(freshBooksClient)