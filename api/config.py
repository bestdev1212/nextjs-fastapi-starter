from decouple import config

class Settings:
    client_id = config('client_id', cast=str)
    client_secret = config('client_secret', cast=str)
    redirect_uri = config('host_url_prefix', cast=str) + '/api/verify'
    host_url_prefix = config('host_url_prefix', cast=str)
    redis_host = config("redis_host", cast=str)
    redis_port = config("redis_port", cast=int)
    redis_db = config("redis_db", cast=str)
    redis_password = config("redis_password", cast=str)
    access_token_kname = "access_token"
    refresh_token_kname = "refresh_token"
    access_token_exired_at_kname = "access_token_exired_at"
    slack_webhook_url = config("slack_webhook_url", cast=str)
    token_duration = 10*3600


settings = Settings()