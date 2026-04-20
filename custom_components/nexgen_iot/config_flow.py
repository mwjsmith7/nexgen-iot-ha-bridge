from __future__ import annotations
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .api import NexGenApiClient, CannotConnect, NotYetApproved
from .const import DOMAIN, DEFAULT_API_URL, DEFAULT_LINK_URL, CONF_API_URL, CONF_TOKEN

STEP_USER_SCHEMA = vol.Schema(
    {vol.Optional(CONF_API_URL, default=DEFAULT_API_URL): str}
)


class NexGenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._api_url: str = DEFAULT_API_URL
        self._link_code: str | None = None
        self._client: NexGenApiClient | None = None

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._api_url = user_input.get(CONF_API_URL, DEFAULT_API_URL)
            self._client = NexGenApiClient(api_url=self._api_url)
            try:
                self._link_code = await self._client.request_link_code()
                return await self.async_step_link()
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def async_step_link(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                token = await self._client.verify_link_code(self._link_code)
                await self._client.close()
                return self.async_create_entry(
                    title="NexGen IoT",
                    data={CONF_API_URL: self._api_url, CONF_TOKEN: token},
                )
            except NotYetApproved:
                errors["base"] = "not_yet_approved"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="link",
            data_schema=vol.Schema({}),
            description_placeholders={
                "link_code": self._link_code or "—",
                "link_url": DEFAULT_LINK_URL,
            },
            errors=errors,
        )
