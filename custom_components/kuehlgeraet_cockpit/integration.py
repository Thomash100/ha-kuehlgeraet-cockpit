"""Runtime setup for Kuehlgeraet Cockpit."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_APPLY,
    CONF_CONFIG_ENTRY_ID,
    CONF_ENABLED,
    CONF_SETTING,
    CONF_VALUE,
    DATA_PANEL_REGISTERED,
    DATA_SERVICES_REGISTERED,
    DOMAIN,
    PLATFORMS,
    RUNTIME_SETTING_KEYS,
    SERVICE_EVALUATE_NOW,
    SERVICE_SET_ENABLED,
    SERVICE_SET_SETTING,
    SERVICE_SET_SIMULATION,
)


def _resolve_entry(hass: HomeAssistant, entry_id: str | None) -> ConfigEntry:
    entries = hass.config_entries.async_entries(DOMAIN)

    if not entries:
        raise HomeAssistantError("Kuehlgeraet Cockpit ist noch nicht eingerichtet.")

    if entry_id is None:
        if len(entries) == 1:
            return entries[0]
        raise HomeAssistantError(
            "Bitte config_entry_id angeben, wenn mehrere Eintraege vorhanden sind."
        )

    for entry in entries:
        if entry.entry_id == entry_id:
            return entry

    raise HomeAssistantError(f"Unbekannte config_entry_id: {entry_id}")


async def _async_update_listener(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_integration(
    hass: HomeAssistant,
    config: dict[str, Any],  # noqa: ARG001
) -> bool:
    """Set up services and frontend panel."""
    from .frontend import async_register_frontend
    from .runtime import async_get_runtime

    runtime = await async_get_runtime(hass)
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get(DATA_PANEL_REGISTERED):
        await async_register_frontend(hass)
        domain_data[DATA_PANEL_REGISTERED] = True

    if domain_data.get(DATA_SERVICES_REGISTERED):
        return True

    evaluate_now_schema = vol.Schema(
        {
            vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
            vol.Optional(CONF_APPLY, default=False): cv.boolean,
        }
    )
    enabled_schema = vol.Schema(
        {
            vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
            vol.Required(CONF_ENABLED): cv.boolean,
        }
    )
    setting_schema = vol.Schema(
        {
            vol.Optional(CONF_CONFIG_ENTRY_ID): cv.string,
            vol.Required(CONF_SETTING): vol.In(sorted(RUNTIME_SETTING_KEYS)),
            vol.Required(CONF_VALUE): vol.Any(vol.Coerce(float), cv.string),
        }
    )

    async def async_handle_evaluate_now(call: ServiceCall) -> None:
        _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        await runtime.async_evaluate(
            apply_decision=call.data[CONF_APPLY],
            reason="service",
        )

    async def async_handle_set_enabled(call: ServiceCall) -> None:
        _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        await runtime.async_set_enabled(call.data[CONF_ENABLED])

    async def async_handle_set_simulation(call: ServiceCall) -> None:
        _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        await runtime.async_set_simulation(call.data[CONF_ENABLED])

    async def async_handle_set_setting(call: ServiceCall) -> None:
        _resolve_entry(hass, call.data.get(CONF_CONFIG_ENTRY_ID))
        await runtime.async_set_setting(call.data[CONF_SETTING], call.data[CONF_VALUE])

    hass.services.async_register(
        DOMAIN,
        SERVICE_EVALUATE_NOW,
        async_handle_evaluate_now,
        schema=evaluate_now_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ENABLED,
        async_handle_set_enabled,
        schema=enabled_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SIMULATION,
        async_handle_set_simulation,
        schema=enabled_schema,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SETTING,
        async_handle_set_setting,
        schema=setting_schema,
    )
    domain_data[DATA_SERVICES_REGISTERED] = True
    return True


async def async_setup_entry_integration(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up Kuehlgeraet Cockpit from a config entry."""
    from .runtime import async_get_runtime

    runtime = await async_get_runtime(hass)
    await runtime.async_setup_entry(entry)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry_integration(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload Kuehlgeraet Cockpit."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        from .runtime import async_get_runtime

        runtime = await async_get_runtime(hass)
        await runtime.async_unload_entry(entry)
    return unload_ok
