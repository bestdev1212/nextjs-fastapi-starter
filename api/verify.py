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
    slack_message =""
    for i in range(len(projects)):
        project_id = projects[i]["id"]
        tracks_per_project = [track for track in tracks if track["project_id"] == project_id]
        track_per_project = sum([x["duration"] for x in tracks_per_project])
        projects[i]["tracked"] = track_per_project
        projects[i]["completed_amount"] = int(projects[i]["tracked"] / projects[i]["budget"] * 100) if not projects[i]["budget"] == None else 0
        projects[i]["completed_amount_grade"] = 0 if projects[i]["completed_amount"] < 50 else 1 if projects[i]["completed_amount"] <75 else 2
        slack_message += "Project Name: {}  -  {} % \n".format(projects[i]["title"], projects[i]["completed_amount"] )
    

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
       
    send_notification(slack_message)
    return slack_message
    return 'success'


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