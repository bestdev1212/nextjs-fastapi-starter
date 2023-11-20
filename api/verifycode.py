from types import SimpleNamespace
from fastapi import FastAPI, Request
import requests
from api.config import settings
from api.cloudredis import read, write
from freshbooks import Client as FreshBooksClient
from  api.cloudredis import read, write
from api.config import settings
from api.schema import WebhookVerify
from api.slack import send_notification
import time
import json
import urllib.parse

def verify_controller(code, webhook=False):
    freshBooksClient = None
    token_response = None
    access_token = None
    refresh_token = None
    access_token_expires_at = None

    if  not code=="abc":
        freshBooksClient = FreshBooksClient(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            redirect_uri=settings.redirect_uri
        )
        print(settings.redirect_uri)
        token_response = freshBooksClient.get_access_token(code)
        access_token = token_response.access_token
        refresh_token = token_response.refresh_token
        access_token_expires_at = str(int(time.time()) + settings.token_duration)
        # print(access_token, refresh_token, access_token_expires_at)
        write(settings.access_token_kname, access_token)
        write(settings.refresh_token_kname, refresh_token)
        write(settings.access_token_exired_at_kname, access_token_expires_at)
        print(access_token)
        print()
        print(str(access_token))
        print()
        print(read(settings.access_token_kname))
    else:
        

        access_token = read(settings.access_token_kname)
        print(access_token)
        refresh_token = read(settings.refresh_token_kname)
        access_token_expires_at = read(settings.access_token_exired_at_kname)
        freshBooksClient = FreshBooksClient(
            client_id=settings.client_id,
            client_secret=settings.client_secret,
            redirect_uri=settings.redirect_uri,
            access_token=access_token,
            refresh_token=refresh_token
        )
        if int(access_token_expires_at) < int(time.time()):
            print('token expired. refreshing')
            token_response = freshBooksClient.refresh_access_token()
            access_token = token_response.access_token
            refresh_token = token_response.refresh_token
            access_token_expires_at = str(int(time.time()) + settings.token_duration)
            # print(access_token, refresh_token, access_token_expires_at)
            write(settings.access_token_kname, access_token)
            write(settings.refresh_token_kname, refresh_token)
            write(settings.access_token_exired_at_kname, access_token_expires_at)
        # print(freshBooksClient.current_user())
    # print(freshBooksClient)
    identity = freshBooksClient.current_user()
    
    businesses = []
    for num, business_membership in enumerate(identity.business_memberships, start=1):
        business = business_membership.business
        businesses.append(
            SimpleNamespace(name=business.name, business_id=business.id, account_id=business.account_id)
        )


    # print(businesses)
    projects = []
    tracks = []

    for i in range(len(businesses)):
        _projects =freshBooksClient.projects.list(business_id=businesses[i].business_id)
        _tracks = freshBooksClient.time_entries.list(business_id=businesses[i].business_id)
        projects += _projects.data["projects"]
        tracks += _tracks.data["time_entries"]

    # print(tracks)
    slack_message ="---- FreshBooks Notification Start ---- \n"
    slack_message_empty = True
    for i in range(len(projects)):
        project_id = projects[i]["id"]
        tracks_per_project = [track for track in tracks if track["project_id"] == project_id]
        track_per_project = sum([x["duration"] for x in tracks_per_project])
        projects[i]["tracked"] = track_per_project
        projects[i]["completed_amount"] = int(projects[i]["tracked"] / projects[i]["budget"] * 100) if not projects[i]["budget"] == None else 0
        projects[i]["completed_amount_grade"] = 0 if projects[i]["completed_amount"] < 50 else 1 if projects[i]["completed_amount"] <75 else 2 if projects[i]["completed_amount"] <100 else 3
        slack_is_send = (webhook and (not str(read(project_id))==str(projects[i]["completed_amount_grade"]))) or (not webhook)
        print(webhook, read(project_id), projects[i]["completed_amount_grade"], (webhook and (not str(read(project_id))==str(projects[i]["completed_amount_grade"]))),slack_is_send)
        write(project_id, projects[i]["completed_amount_grade"])
        if slack_is_send:
            slack_message_empty = False
            slack_message += "Project Name: {}  -  {} % \n ".format(projects[i]["title"], projects[i]["completed_amount"] )
    slack_message +="---- FreshBooks Notification End ---- \n"

    if not webhook:
        for i in range(len(businesses)):
            print(businesses[i])
            webhooks = freshBooksClient.callbacks.list(businesses[i].account_id)
            print(webhooks.data)
            for callback in webhooks.data["callbacks"]:
                print(callback)
                # res = freshBooksClient.callbacks.delete(businesses[i].account_id, int(callback["callbackid"]))
                url = "https://api.freshbooks.com/events/account/{}/events/callbacks/{}".format(businesses[i].account_id,callback["callbackid"])
            

                headers = {'Authorization': 'Bearer {}'.format(access_token), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
                res = requests.delete(url, data=None, headers=headers)
                print(res)

            url = "https://api.freshbooks.com/events/account/{}/events/callbacks".format(businesses[i].account_id)
            payload = {'callback': {
                'event': "time_entry",
                'uri': "{}/api/webhook".format(settings.host_url_prefix)
            }
            }

            headers = {'Authorization': 'Bearer {}'.format(access_token), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
            res = requests.post(url, data=json.dumps(payload), headers=headers)
            print(res.json())
    print('--- slack message ---')
    if not slack_message_empty:
        send_notification(slack_message)
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
                         <img src="https://cdn-icons-png.flaticon.com/512/148/148767.png" class="my-4" width="100" />
                        <span class="text-gray-300">Setup Completed!</span>
                    </div>
                    
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
    return body


async def webhook_verify(req: Request):
    try:
        s =await req.body()
        s= urllib.parse.unquote(s)
        d = urllib.parse.parse_qs(s)
        d = {k: v[0] for k, v in d.items()}
        print(d)
        url = "https://api.freshbooks.com/events/account/{}/events/callbacks/{}".format(d["account_id"], d["object_id"])
        payload = {'callback': {
            'verifier': d["verifier"]
        }
        }

        headers = {'Authorization': 'Bearer {}'.format(read(settings.access_token_kname)), 'Api-Version': 'alpha', 'Content-Type': 'application/json'}
        res = requests.put(url, data=json.dumps(payload), headers=headers)
        print('---- webhook verify result -----')
        print(res, res.content)
    except:
        verify_controller(code="abc", webhook=True)
    return 'success'