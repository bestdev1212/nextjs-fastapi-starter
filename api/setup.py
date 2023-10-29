from api.config import settings
from api.cloudredis import read, write
from freshbooks import Client as FreshBooksClient


def setup_controller():
    
        # print(type(settings.client_id))
    freshBooksClient = FreshBooksClient(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
        redirect_uri=settings.redirect_uri
    )
    
    authorization_url = freshBooksClient.get_auth_request_url(
        scopes=['user:profile:read', 'user:projects:read', 'user:time_entries:read']
    )
    print(authorization_url)
    # business_index = int(input("Which business do you want to use? ")) - 1
    body = """
    <html>
        <body>
            <div class="row">
                    <h1 style="font-size:48px;">Try to log in freshbooks by clicking bellow link</h1>
                    <a style="color:white;text-decoration:none;font-size: 32px; padding: 16px; background-color: blue; border-radius: 12px;" 
                    href="{}" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                        Login
                    </a>
                    
                </div>
        </body>
    
    <html>


    """
    return body.format(authorization_url)