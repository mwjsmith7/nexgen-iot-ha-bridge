from __future__ import annotations
import aiohttp


class CannotConnect(Exception):
    pass


class InvalidAuth(Exception):
    pass


class NotYetApproved(Exception):
    pass


class NexGenApiClient:
    def __init__(
        self,
        api_url: str,
        token: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._api_url = api_url.rstrip("/")
        self._token = token
        self._session = session
        self._owns_session = session is None

    async def _session_get(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def set_token(self, token: str) -> None:
        self._token = token

    async def close(self) -> None:
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()

    # ── Auth flow ──────────────────────────────────────────────────────────

    async def request_link_code(self) -> str:
        session = await self._session_get()
        try:
            async with session.post(f"{self._api_url}/ha/link") as resp:
                if not resp.ok:
                    raise CannotConnect(f"Link code request failed: {resp.status}")
                data = await resp.json()
                return data["code"]
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err

    async def verify_link_code(self, code: str) -> str:
        session = await self._session_get()
        try:
            async with session.post(
                f"{self._api_url}/ha/link/verify",
                json={"code": code},
            ) as resp:
                if not resp.ok:
                    raise NotYetApproved("Code not yet approved")
                data = await resp.json()
                if data.get("status") == "approved" and data.get("token"):
                    return data["token"]
                raise NotYetApproved("Code not yet approved")
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err

    # ── Device API ─────────────────────────────────────────────────────────

    async def get_devices(self) -> list[dict]:
        data = await self._get("/devices")
        return data.get("devices", [])

    async def get_device_state(self, device_id: str) -> dict:
        return await self._get(f"/devices/{device_id}/state")

    async def send_command(self, device_id: str, payload: dict) -> dict:
        return await self._post(f"/devices/{device_id}/command", {"payload": payload})

    # ── Helpers ────────────────────────────────────────────────────────────

    async def _get(self, path: str) -> dict:
        session = await self._session_get()
        try:
            async with session.get(
                f"{self._api_url}{path}", headers=self._auth_headers()
            ) as resp:
                if resp.status == 401:
                    raise InvalidAuth("Token rejected")
                if not resp.ok:
                    raise CannotConnect(f"GET {path} failed: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err

    async def _post(self, path: str, body: dict) -> dict:
        session = await self._session_get()
        try:
            async with session.post(
                f"{self._api_url}{path}", json=body, headers=self._auth_headers()
            ) as resp:
                if resp.status == 401:
                    raise InvalidAuth("Token rejected")
                if not resp.ok:
                    raise CannotConnect(f"POST {path} failed: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise CannotConnect(str(err)) from err

    def _auth_headers(self) -> dict:
        if not self._token:
            raise InvalidAuth("No token configured")
        return {"Authorization": f"Bearer {self._token}"}
