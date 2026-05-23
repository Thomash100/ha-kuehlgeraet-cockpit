"""Frontend panel registration for Kuehlgeraet Cockpit."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    PANEL_ELEMENT,
    PANEL_FILENAME,
    PANEL_STATIC_URL,
    PANEL_URL_PATH,
)


async def async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and register the cockpit web panel."""
    frontend_path = Path(__file__).parent / "frontend"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(PANEL_STATIC_URL, str(frontend_path), False)]
    )

    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=PANEL_ELEMENT,
        sidebar_title="Kuehlgeraet Cockpit",
        sidebar_icon="mdi:fridge-outline",
        module_url=f"{PANEL_STATIC_URL}/{PANEL_FILENAME}?v=1",
        require_admin=False,
        config={"domain": DOMAIN},
    )


def async_unregister_frontend(hass: HomeAssistant) -> None:
    """Remove the custom panel from the Home Assistant sidebar."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH)
