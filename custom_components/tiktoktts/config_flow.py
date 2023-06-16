"""Support TikTokTTS UI configuration."""

from homeassistant import config_entries
from homeassistant.components.tts import CONF_LANG
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_ENDPOINT,
    CONF_VOICE,
    DEFAULT_ENDPOINT,
    DEFAULT_LANG,
    DEFAULT_VOICE,
    SUPPORTED_LANGUAGES,
    SUPPORTED_VOICES,
)


class TikTokTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for TikTokTTS."""

    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1

    async def is_valid(self, info):
        """Validate User input."""
        if (
            vol.In(SUPPORTED_VOICES, info[CONF_VOICE])
            and vol.In(SUPPORTED_LANGUAGES, info[CONF_LANG])
            and info[CONF_ENDPOINT] is not None
        ):
            return True
        return False

    async def async_step_user(self, info):
        """Allow user to setup the integration."""
        if info is not None:
            valid = await self.is_valid(info)
            if valid:
                return self.async_create_entry(
                    title="TikTok TTS",
                    data={
                        CONF_ENDPOINT: info[CONF_ENDPOINT],
                        CONF_LANG: info[CONF_LANG],
                        CONF_VOICE: info[CONF_VOICE],
                    },
                )

        #        await self.async_set_unique_id(UNIQUE_ID)
        #        self._abort_if_unique_id_configured()

        data_schema = {
            vol.Required(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
            vol.Optional(CONF_LANG, default=DEFAULT_LANG): str,
            vol.Optional(CONF_VOICE, default=DEFAULT_VOICE): str,
        }

        return self.async_show_form(step_id="user", data_schema=vol.Schema(data_schema))
