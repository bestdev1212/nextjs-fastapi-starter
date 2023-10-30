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

    <!doctype html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body>
        <div class="flex h-screen w-full items-center justify-center bg-gray-900 bg-cover bg-no-repeat" style="background-image:url('https://images.unsplash.com/photo-1499123785106-343e69e68db1?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1748&q=80')">
            <div class="rounded-xl bg-gray-800 bg-opacity-50 px-16 py-10 shadow-lg backdrop-blur-md max-sm:px-8 m-2">
                <div class="text-white">
                    <div class="mb-8 flex flex-col items-center text-center">
                        <img src="https://app.integrately.com/i/integrations/freshbooks_slack_integrations.png" class="mb-8" width="150" alt="" srcset="" />
                        <h1 class="mb-2 text-2xl">Slack Bot for Freshbooks progress</h1>
                        <span class="text-gray-300">Click Login to proceed</span>
                    </div>
                    <form action="#">
                        <div class="mt-8 flex justify-center text-lg text-black">
                        <a class="rounded-3xl bg-yellow-400 bg-opacity-50 px-10 py-2 text-white shadow-xl backdrop-blur-md transition-colors duration-300 hover:bg-yellow-600" 
                                    href="{}" >
                                        Login
                                    </a>
                        </div>
                    </form>
                    <div class="m-8 flex flex-col items-center">
                        <span class="text-gray-300">@Copyright Marcus O</span>
                        <a href="https://github.com/ihortecker/nextjs-fastapi-starter" target="_blank"  class="mt-4">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="mr-2" viewBox="0 0 1792 1792">
                                <path d="M896 128q209 0 385.5 103t279.5 279.5 103 385.5q0 251-146.5 451.5t-378.5 277.5q-27 5-40-7t-13-30q0-3 .5-76.5t.5-134.5q0-97-52-142 57-6 102.5-18t94-39 81-66.5 53-105 20.5-150.5q0-119-79-206 37-91-8-204-28-9-81 11t-92 44l-38 24q-93-26-192-26t-192 26q-16-11-42.5-27t-83.5-38.5-85-13.5q-45 113-8 204-79 87-79 206 0 85 20.5 150t52.5 105 80.5 67 94 39 102.5 18q-39 36-49 103-21 10-45 15t-57 5-65.5-21.5-55.5-62.5q-19-32-48.5-52t-49.5-24l-20-3q-21 0-29 4.5t-5 11.5 9 14 13 12l7 5q22 10 43.5 38t31.5 51l10 23q13 38 44 61.5t67 30 69.5 7 55.5-3.5l23-4q0 38 .5 88.5t.5 54.5q0 18-13 30t-40 7q-232-77-378.5-277.5t-146.5-451.5q0-209 103-385.5t279.5-279.5 385.5-103zm-477 1103q3-7-7-12-10-3-13 2-3 7 7 12 9 6 13-2zm31 34q7-5-2-16-10-9-16-3-7 5 2 16 10 10 16 3zm30 45q9-7 0-19-8-13-17-6-9 5 0 18t17 7zm42 42q8-8-4-19-12-12-20-3-9 8 4 19 12 12 20 3zm57 25q3-11-13-16-15-4-19 7t13 15q15 6 19-6zm63 5q0-13-17-11-16 0-16 11 0 13 17 11 16 0 16-11zm58-10q-2-11-18-9-16 3-14 15t18 8 14-14z"></path>
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
  


    """
    return body.format(authorization_url)