from __future__ import annotations

import asyncio
import logging
import typing

import aiohttp
from aiohttp import ClientSession
from urllib.parse import urljoin

LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://v1.fluss-api.com/v1/"


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

    Uses the Fluss REST API v1 at https://v1.fluss-api.com/v1.
    Authentication is via API key passed in the Authorization header.
    """

    def __init__(
        self,
        api_key: str,
        session: typing.Optional[ClientSession] = None,
        timeout: int = 10,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        """Initialize the Fluss+ API Client."""
        self._api_key = api_key
        self._base_url = base_url if base_url.endswith("/") else base_url + "/"
        self._timeout = timeout
        self._session = session or ClientSession()

    def _auth_headers(self) -> dict:
        """Return authorization headers for API requests."""
        return {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

    async def async_get_devices(self) -> typing.Any:
        """List all devices associated with the account."""
        try:
            return await self._api_wrapper(
                method="GET",
                endpoint="list",
                headers=self._auth_headers(),
            )
        except FlussApiClientError as error:
            LOGGER.error("Failed to get devices: %s", error)
            raise FlussDeviceError("Failed to retrieve devices") from error

    async def async_get_device_status(self, device_id: str) -> typing.Any:
        """Get the current status of a device."""
        return await self._api_wrapper(
            method="GET",
            endpoint=f"status/{device_id}",
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
        data: dict[str, typing.Any] = {"metaData": kwargs.get("metaData", "")}
        return await self._api_wrapper(
            method="POST",
            endpoint=f"trigger/{device_id}",
            headers=self._auth_headers(),
            data=data,
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
            endpoint=f"open/{device_id}",
            headers=self._auth_headers(),
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
            endpoint=f"close/{device_id}",
            headers=self._auth_headers(),
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
            raise FlussApiClientCommunicationError(
                "Timeout error fetching information"
            ) from e
        except aiohttp.ClientError as ex:
            msg = str(ex)
            if "Domain name not found" in msg or "Name or service not known" in msg:
                LOGGER.error(
                    "DNS resolution failed for %s — the Fluss API host is "
                    "unreachable. Verify the base URL is correct",
                    url,
                )
                raise FlussApiClientCommunicationError(
                    f"Cannot resolve API host for {url}. "
                    "The Fluss API domain may have changed."
                ) from ex
            LOGGER.error("Client error fetching information from %s: %s", url, ex)
            raise FlussApiClientCommunicationError(
                "Error fetching information"
            ) from ex
        except FlussApiClientAuthenticationError:
            raise
        except Exception as exception:
            LOGGER.error("Unexpected error occurred: %s", exception)
            raise FlussApiClientError(
                "An unexpected error occurred"
            ) from exception

    async def close(self) -> None:
        """Close the aiohttp session if it was created by this client."""
        if self._session and not self._session.closed:
            await self._session.close()
