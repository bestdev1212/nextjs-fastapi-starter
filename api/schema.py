from pydantic import BaseModel

class WebhookVerify(BaseModel):
    verifier: str
    object_id: str
    account_id: str