import httpx
from desktop_agent.settings import config


class Windmill:
    def __init__(self, instance_url: str, super_admin_token: str):
        self.instance_url = instance_url.rstrip("/")
        self.super_admin_token = super_admin_token
        self.base_api_url = self.instance_url + "/api"
        headers = {"Authorization": f"Bearer {self.super_admin_token}"}
        self.client = httpx.Client(base_url=self.base_api_url, headers=headers)

    def get(self, url: str):
        return self.client.get(url)

    def post(self, url: str, data: dict):
        return self.client.post(url, json=data)

    def user_exists(self, email: str):
        return self.get(f"/users/exists/{email}")
