import httpx
from desktop_agent.settings import config


class Windmill:
    def __init__(self, instance_url: str, super_admin_token: str):
        self.instance_url = instance_url.rstrip("/")
        self.super_admin_token = super_admin_token
        self.base_api_url = self.instance_url + "/api"
        self.client = httpx.Client()
