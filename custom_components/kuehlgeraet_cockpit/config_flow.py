"""Config flow for Kuehlgeraet Cockpit."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_AUTO_APPLY,
    CONF_CHEAP_ENTITY,
    CONF_CHEAP_OFF_TEMP,
    CONF_CHEAP_ON_TEMP,
    CONF_COMPRESSOR_RUNNING_WATTS,
    CONF_EVALUATION_INTERVAL,
    CONF_EXPENSIVE_OFF_TEMP,
    CONF_EXPENSIVE_ON_TEMP,
    CONF_FAILSAFE_ON,
    CONF_MIN_OFF_SECONDS,
    CONF_MIN_ON_SECONDS,
    CONF_POWER_ENTITY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_MAX_ENTITY,
    CONF_PRICE_MIN_ENTITY,
    CONF_TARGET_ENTITY,
    CONF_TEMPERATURE_ENTITY,
    DEFAULT_AUTO_APPLY,
    DEFAULT_CHEAP_ENTITY,
    DEFAULT_CHEAP_OFF_TEMP,
    DEFAULT_CHEAP_ON_TEMP,
    DEFAULT_COMPRESSOR_RUNNING_WATTS,
    DEFAULT_EVALUATION_INTERVAL,
    DEFAULT_EXPENSIVE_OFF_TEMP,
    DEFAULT_EXPENSIVE_ON_TEMP,
    DEFAULT_FAILSAFE_ON,
    DEFAULT_MIN_OFF_SECONDS,
    DEFAULT_MIN_ON_SECONDS,
    DEFAULT_POWER_ENTITY,
    DEFAULT_PRICE_ENTITY,
    DEFAULT_PRICE_MAX_ENTITY,
    DEFAULT_PRICE_MIN_ENTITY,
    DEFAULT_TARGET_ENTITY,
    DEFAULT_TEMPERATURE_ENTITY,
    DOMAIN,
)


def _defaults(source: dict[str, Any]) -> dict[str, Any]:
    return {
        CONF_TARGET_ENTITY: source.get(CONF_TARGET_ENTITY, DEFAULT_TARGET_ENTITY),
        CONF_TEMPERATURE_ENTITY: source.get(
            CONF_TEMPERATURE_ENTITY,
            DEFAULT_TEMPERATURE_ENTITY,
        ),
        CONF_POWER_ENTITY: source.get(CONF_POWER_ENTITY, DEFAULT_POWER_ENTITY),
        CONF_PRICE_ENTITY: source.get(CONF_PRICE_ENTITY, DEFAULT_PRICE_ENTITY),
        CONF_PRICE_MIN_ENTITY: source.get(
            CONF_PRICE_MIN_ENTITY,
            DEFAULT_PRICE_MIN_ENTITY,
        ),
        CONF_PRICE_MAX_ENTITY: source.get(
            CONF_PRICE_MAX_ENTITY,
            DEFAULT_PRICE_MAX_ENTITY,
        ),
        CONF_CHEAP_ENTITY: source.get(CONF_CHEAP_ENTITY, DEFAULT_CHEAP_ENTITY),
        CONF_AUTO_APPLY: source.get(CONF_AUTO_APPLY, DEFAULT_AUTO_APPLY),
        CONF_FAILSAFE_ON: source.get(CONF_FAILSAFE_ON, DEFAULT_FAILSAFE_ON),
        CONF_EVALUATION_INTERVAL: source.get(
            CONF_EVALUATION_INTERVAL,
            DEFAULT_EVALUATION_INTERVAL,
        ),
        CONF_COMPRESSOR_RUNNING_WATTS: source.get(
            CONF_COMPRESSOR_RUNNING_WATTS,
            DEFAULT_COMPRESSOR_RUNNING_WATTS,
        ),
        CONF_MIN_ON_SECONDS: source.get(CONF_MIN_ON_SECONDS, DEFAULT_MIN_ON_SECONDS),
        CONF_MIN_OFF_SECONDS: source.get(
            CONF_MIN_OFF_SECONDS,
            DEFAULT_MIN_OFF_SECONDS,
        ),
        CONF_CHEAP_ON_TEMP: source.get(CONF_CHEAP_ON_TEMP, DEFAULT_CHEAP_ON_TEMP),
        CONF_CHEAP_OFF_TEMP: source.get(CONF_CHEAP_OFF_TEMP, DEFAULT_CHEAP_OFF_TEMP),
        CONF_EXPENSIVE_ON_TEMP: source.get(
            CONF_EXPENSIVE_ON_TEMP,
            DEFAULT_EXPENSIVE_ON_TEMP,
        ),
        CONF_EXPENSIVE_OFF_TEMP: source.get(
            CONF_EXPENSIVE_OFF_TEMP,
            DEFAULT_EXPENSIVE_OFF_TEMP,
        ),
    }


def _build_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_TARGET_ENTITY, default=defaults[CONF_TARGET_ENTITY]): str,
            vol.Optional(
                CONF_TEMPERATURE_ENTITY,
                default=defaults[CONF_TEMPERATURE_ENTITY],
            ): str,
            vol.Optional(CONF_POWER_ENTITY, default=defaults[CONF_POWER_ENTITY]): str,
            vol.Optional(CONF_PRICE_ENTITY, default=defaults[CONF_PRICE_ENTITY]): str,
            vol.Optional(
                CONF_PRICE_MIN_ENTITY,
                default=defaults[CONF_PRICE_MIN_ENTITY],
            ): str,
            vol.Optional(
                CONF_PRICE_MAX_ENTITY,
                default=defaults[CONF_PRICE_MAX_ENTITY],
            ): str,
            vol.Optional(CONF_CHEAP_ENTITY, default=defaults[CONF_CHEAP_ENTITY]): str,
            vol.Required(CONF_AUTO_APPLY, default=defaults[CONF_AUTO_APPLY]): bool,
            vol.Required(CONF_FAILSAFE_ON, default=defaults[CONF_FAILSAFE_ON]): bool,
            vol.Required(
                CONF_EVALUATION_INTERVAL,
                default=defaults[CONF_EVALUATION_INTERVAL],
            ): vol.All(vol.Coerce(int), vol.Range(min=30, max=86400)),
            vol.Required(
                CONF_COMPRESSOR_RUNNING_WATTS,
                default=defaults[CONF_COMPRESSOR_RUNNING_WATTS],
            ): vol.Coerce(float),
            vol.Required(
                CONF_MIN_ON_SECONDS,
                default=defaults[CONF_MIN_ON_SECONDS],
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
            vol.Required(
                CONF_MIN_OFF_SECONDS,
                default=defaults[CONF_MIN_OFF_SECONDS],
            ): vol.All(vol.Coerce(int), vol.Range(min=0, max=86400)),
            vol.Required(
                CONF_CHEAP_ON_TEMP,
                default=defaults[CONF_CHEAP_ON_TEMP],
            ): vol.Coerce(float),
            vol.Required(
                CONF_CHEAP_OFF_TEMP,
                default=defaults[CONF_CHEAP_OFF_TEMP],
            ): vol.Coerce(float),
            vol.Required(
                CONF_EXPENSIVE_ON_TEMP,
                default=defaults[CONF_EXPENSIVE_ON_TEMP],
            ): vol.Coerce(float),
            vol.Required(
                CONF_EXPENSIVE_OFF_TEMP,
                default=defaults[CONF_EXPENSIVE_OFF_TEMP],
            ): vol.Coerce(float),
        }
    )


class KuehlgeraetCockpitConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kuehlgeraet Cockpit."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,  # noqa: ARG004
    ) -> config_entries.OptionsFlow:
        return KuehlgeraetCockpitOptionsFlow()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the first config step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            if not user_input.get(CONF_TARGET_ENTITY, "").strip():
                errors[CONF_TARGET_ENTITY] = "required"
            else:
                return self.async_create_entry(
                    title="Kuehlgeraet Cockpit",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(_defaults({})),
            errors=errors,
        )


class KuehlgeraetCockpitOptionsFlow(config_entries.OptionsFlow):
    """Handle Kuehlgeraet Cockpit options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        """Manage integration options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            if not user_input.get(CONF_TARGET_ENTITY, "").strip():
                errors[CONF_TARGET_ENTITY] = "required"
            else:
                return self.async_create_entry(title="", data=user_input)

        defaults = _defaults({**self.config_entry.data, **self.config_entry.options})
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(defaults),
            errors=errors,
        )
