"""Support for the TikTokTTS service."""
from __future__ import annotations

import logging
import json
import base64
import asyncio
from http import HTTPStatus

import voluptuous as vol
import aiohttp
import async_timeout

from homeassistant.components.tts import CONF_LANG, PLATFORM_SCHEMA, Provider
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.const import Platform

from .const import (
    CONF_ENDPOINT,
    CONF_VOICE,
    DEFAULT_ENDPOINT,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    SUPPORTED_LANGUAGES,
    SUPPORTED_OPTIONS,
    SUPPORTED_VOICES,
    DOMAIN,
)

PLATFORMS = Platform.TTS

_LOGGER = logging.getLogger(__name__)

# Platform schema for configuration via configuration.yml
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): cv.string,
        vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): vol.In(SUPPORTED_VOICES),
        vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORTED_LANGUAGES),
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    """Set up TikTokTTS speech component."""
    _LOGGER.warning("TikTokTTS async_get_engine called: " + str(config))
    return TikTokTTSProvider(
        hass, config.get(CONF_ENDPOINT), config.get(CONF_LANG), config.get(CONF_VOICE)
    )


async def async_setup_entry(hass, entry):
    """Set up TTS from a config entry."""
    _LOGGER.warning("TikTokTTS async_setup_entry called: " + str(entry))
    if entry is None:
        return True

    tiktoktts = TikTokTTSProvider(
        hass, entry.data[CONF_ENDPOINT], entry.data[CONF_LANG], entry.data[CONF_VOICE]
    )
    hass.data[DOMAIN][entry.data[CONF_ENDPOINT]] = tiktoktts
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.data[CONF_ENDPOINT])
    return True


async def async_setup(hass, config):
    """Activate Alexa component."""
    _LOGGER.warning("TikTokTTS async_setup called: " + str(config))

    config = config.get(DOMAIN, {})
    return True


class TikTokTTSProvider(Provider):
    """TikTokTTS speech api provider."""

    def __init__(self, hass, endpoint, lang, voice):
        """Init TikTokTTS TTS service."""
        self.hass = hass
        self.name = "TikTokTTS"
        self._endpoint = endpoint
        self._voice = voice
        self._language = lang

    @property
    def supported_languages(self):
        """Return list of supported languages."""
        return SUPPORTED_LANGUAGES

    @property
    def default_language(self):
        """Return the default language."""
        return self._language

    @property
    def supported_options(self):
        """Return list of supported options."""
        return SUPPORTED_OPTIONS

    async def async_get_tts_audio(self, message, language, options=None):
        """Load TTS from TikTokTTS."""

        websession = async_get_clientsession(self.hass)
        # actual_language = language
        options = options or {}

        # api_status_request = requests.get(self._endpoint + "/api/status")
        # result = api_status_request.json()
        # if result["data"]:
        #    if result["data"]["available"] is True:
        #        print("Service available")
        #    else:
        #        print("Service unavailable")
        #        return None, None

        try:
            async with async_timeout.timeout(20):
                post_data = {
                    "text": message,
                    "voice": options.get(CONF_VOICE, self._voice),
                }

                request = await websession.post(
                    url=self._endpoint + "/api/generation", json=post_data
                )

                if request.status != HTTPStatus.OK:
                    _LOGGER.error(
                        "Error %d on load URL %s", request.status, request.url
                    )
                    _LOGGER.error(request)
                    return (None, None)

                data = await request.read()
                audio = json.loads(data.decode("utf8"))
                data = base64.b64decode(audio["data"])
                audiotype = "wav"

        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Timeout for TikTokTTS API")
            return (None, None)
        return audiotype, data
