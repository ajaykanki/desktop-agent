import httpx
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from app.logging import log


class Windmill:
    DEFAULT_TOKEN_DURATION = timedelta(minutes=2)

    def __init__(self, instance_url: str, super_admin_token: str):
        self.instance_url = instance_url.rstrip("/")
        self.token = super_admin_token
        self.base_api_url = f"{self.instance_url}/api"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
        }
        self.client = httpx.Client(
            base_url=self.base_api_url,
            headers=self.headers,
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        token: Optional[str] = None,
        raise_for_status: bool = True,
        **kwargs,
    ) -> httpx.Response:
        """
        Make an HTTP request to the Windmill API.

        Args:
            method: HTTP method to use (GET, POST, etc.)
            endpoint: API endpoint to call
            token: Optional impersonation token to override the default
            raise_for_status: Whether to raise an exception for HTTP error status codes
            **kwargs: Additional arguments to pass to the request

        Returns:
            httpx.Response: The response from the API
        """
        endpoint = endpoint.lstrip("/")

        # Prepare headers with optional token override
        if token:
            headers = self.headers.copy()
            headers["Authorization"] = f"Bearer {token}"
            kwargs["headers"] = headers

        # Make the HTTP request
        method_func = getattr(self.client, method.lower())
        resp = method_func(f"/{endpoint}", **kwargs)

        # Handle error status if requested
        if raise_for_status:
            self._handle_response_errors(resp)

        return resp

    def _handle_response_errors(self, resp: httpx.Response) -> None:
        """
        Handle HTTP response errors consistently.

        Args:
            resp: The response object to check for errors

        Raises:
            Exception: If the response contains an HTTP error status
        """
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as err:
            error = (
                f"{err.request.url}: {err.response.status_code}, {err.response.text}"
            )
            log.error(error)
            raise Exception(error)

    def get(
        self,
        endpoint: str,
        token: Optional[str] = None,
        raise_for_status: bool = True,
        **kwargs,
    ) -> httpx.Response:
        return self._make_request("GET", endpoint, token, raise_for_status, **kwargs)

    def post(
        self, endpoint: str, raise_for_status: bool = True, **kwargs
    ) -> httpx.Response:
        return self._make_request("POST", endpoint, None, raise_for_status, **kwargs)

    def get_all_runnables(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all runnables for a user.

        Args:
            token: Optional impersonation token

        Returns:
            Dictionary containing all runnables for the user
        """
        return self.get("/users/all_runnables", token=token).json()

    def run_async(
        self, url: str, body: dict[str, Any], token: str | None = None
    ) -> str:
        """
        Run a script or a flow by it's async URL.

        Args:
            url: Async URL of the flow to run
            body: The arguments to pass to the script or flow
            token: Optional impersonation token

        Returns:
            A Job ID of the execution
        """
        return self.post(url, json=body, token=token).text

    def create_token_impersonate(
        self,
        impersonate_email: str,
        duration=timedelta(minutes=2),
        label: str | None = None,
        workspace_id: str | None = None,
    ):
        payload = {
            "impersonate_email": impersonate_email,
            "expiration": (datetime.now(timezone.utc) + duration).isoformat(),
        }

        if label:
            payload["label"] = label.strip()

        if workspace_id:
            payload["workspace_id"] = workspace_id

        resp = self.post("/users/tokens/impersonate", json=payload)

        if resp.status_code == 201:
            return resp.text

        raise Exception(f"Failed to impersonate user: {resp.text}")

    def user_exists(self, email: str) -> bool:
        return self.get(f"/users/exists/{email}").json()

    def authorize_user(self, email: str) -> str:
        return self.user_exists
