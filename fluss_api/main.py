import aiohttp
import asyncio
import logging
import typing
from aiohttp import ClientSession
from urllib.parse import urljoin

LOGGER = logging.getLogger(__name__)


class FlussApiClientError(Exception):
    """Exception to indicate a general API error."""


class FlussDeviceError(FlussApiClientError):
    """Exception to indicate an error occurred when retrieving devices."""


class FlussApiClientCommunicationError(FlussApiClientError):
    """Exception to indicate a communication error."""


class FlussApiClientAuthenticationError(FlussApiClientError):
    """Exception to indicate an authentication error."""


class FlussApiClient:
    """Fluss+ API Client.

    Uses the Fluss REST API v1 at https://api.fluss.co.za/v1.
    Authentication is via Bearer token (API key from the Fluss dashboard).
    """

    def __init__(
        self,
        api_key: str,
        session: typing.Optional[ClientSession] = None,
        timeout: int = 10,
        base_url: str = "https://api.fluss.co.za/v1/",
    ) -> None:
        """Initialize the Fluss+ API Client."""
        self._api_key = api_key
        self._base_url = base_url if base_url.endswith("/") else base_url + "/"
        self._timeout = timeout
        self._session = session or ClientSession()

    def _auth_headers(self) -> dict:
        """Return authorization headers for API requests."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    async def async_get_devices(self) -> typing.Any:
        """List all devices associated with the account."""
        try:
            return await self._api_wrapper(
                method="GET",
                endpoint="devices",
                headers=self._auth_headers(),
            )
        except FlussApiClientError as error:
            LOGGER.error("Failed to get devices: %s", error)
            raise FlussDeviceError("Failed to retrieve devices") from error

    async def async_get_device_status(self, device_id: str) -> typing.Any:
        """Get the current status of a device."""
        return await self._api_wrapper(
            method="GET",
            endpoint=f"devices/{device_id}/status",
            headers=self._auth_headers(),
        )

    async def async_trigger_device(
        self,
        device_id: str,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Trigger a device.

        Args:
            device_id: The ID of the device to trigger.
            **kwargs: Optional parameters forwarded to the API
                      (e.g. action="pulse", duration=3).
        """
        return await self._api_wrapper(
            method="POST",
            endpoint=f"devices/{device_id}/trigger",
            headers=self._auth_headers(),
            data=kwargs if kwargs else None,
        )

    async def async_open_device(
        self,
        device_id: str,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Open a device (gate/door).

        Args:
            device_id: The ID of the device to open.
            **kwargs: Optional parameters forwarded to the API.
        """
        return await self._api_wrapper(
            method="POST",
            endpoint=f"devices/{device_id}/open",
            headers=self._auth_headers(),
            data=kwargs if kwargs else None,
        )

    async def async_close_device(
        self,
        device_id: str,
        **kwargs: typing.Any,
    ) -> typing.Any:
        """Close a device (gate/door).

        Args:
            device_id: The ID of the device to close.
            **kwargs: Optional parameters forwarded to the API.
        """
        return await self._api_wrapper(
            method="POST",
            endpoint=f"devices/{device_id}/close",
            headers=self._auth_headers(),
            data=kwargs if kwargs else None,
        )

    async def _api_wrapper(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> typing.Any:
        """Make a request to the Fluss API."""
        url = urljoin(self._base_url, endpoint)
        try:
            async with asyncio.timeout(self._timeout):
                async with self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                ) as response:
                    if response.status == 401:
                        raise FlussApiClientAuthenticationError("Invalid credentials")
                    elif response.status == 403:
                        raise FlussApiClientAuthenticationError("Access forbidden")
                    response.raise_for_status()
                    return await response.json()

        except asyncio.TimeoutError as e:
            LOGGER.error("Timeout error fetching information from %s", url)
            raise FlussApiClientCommunicationError("Timeout error fetching information") from e
        except aiohttp.ClientError as ex:
            LOGGER.error("Client error fetching information from %s: %s", url, ex)
            raise FlussApiClientCommunicationError("Error fetching information") from ex
        except FlussApiClientAuthenticationError as auth_ex:
            LOGGER.error("Authentication error: %s", auth_ex)
            raise
        except Exception as exception:
            LOGGER.error("Unexpected error occurred: %s", exception)
            raise FlussApiClientError("An unexpected error occurred") from exception

    async def close(self):
        """Close the aiohttp session if it was created by this client."""
        if self._session and not self._session.closed:
            await self._session.close()
