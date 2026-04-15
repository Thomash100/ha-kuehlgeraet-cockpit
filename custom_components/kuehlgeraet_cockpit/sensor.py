"""Sensorplattform fuer Kuehlgeraet Cockpit."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import STATUS_SENSOR_NAME, STATUS_SENSOR_UNIQUE_ID
from .runtime import KuehlgeraetCockpitRuntime, async_get_runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet den Statussensor fuer einen Konfigurationseintrag ein."""
    runtime = await async_get_runtime(hass)
    async_add_entities([KuehlgeraetCockpitStatusSensor(runtime)], True)


class KuehlgeraetCockpitStatusSensor(SensorEntity):
    """Stellt den letzten Status der Kuehlgeraete-Automation als Sensor bereit."""

    _attr_name = STATUS_SENSOR_NAME
    _attr_unique_id = STATUS_SENSOR_UNIQUE_ID
    _attr_icon = "mdi:fridge-outline"
    _attr_should_poll = False

    def __init__(self, runtime: KuehlgeraetCockpitRuntime) -> None:
        self._runtime = runtime

    @property
    def native_value(self) -> str:
        """Gibt den primaeren Sensorzustand zurueck."""
        return str(self._runtime.status.get("mode") or "Bereitschaft")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Gibt die letzte Status-Nutzlast als Attribute zurueck."""
        return dict(self._runtime.status)

    async def async_added_to_hass(self) -> None:
        """Abonniert Statusaktualisierungen zur Laufzeit."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        """Schreibt den neuesten Zustand in Home Assistant."""
        self.async_write_ha_state()