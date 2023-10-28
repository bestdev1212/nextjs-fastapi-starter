from fastapi import FastAPI, Request
from freshbooks import Client

freshBooksClient = Client(
    client_id="71f8d9e091f36ac5e40b8939b4793da813c3df51b45735271bb380ede4e903d9",
    client_secret="cc2bc7903a859510616d0582d60d4d8d6e86dffdc21838b9a39a20f1df559c10",
    redirect_uri="https://nextjs-fastapi-starter-bay-seven.vercel.app/"
)
app = FastAPI()
print(freshBooksClient)
@app.get("/api/python")
def hello_world():
    return {"message": "Hello World123"}