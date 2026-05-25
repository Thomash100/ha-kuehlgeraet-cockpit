"""Switches for Kuehlgeraet Cockpit."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ENABLED_SWITCH_OBJECT_ID,
    ENABLED_SWITCH_UNIQUE_ID,
    SIMULATION_SWITCH_OBJECT_ID,
    SIMULATION_SWITCH_UNIQUE_ID,
)
from .runtime import KuehlgeraetCockpitRuntime, async_get_runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up runtime switches for a config entry."""
    runtime = await async_get_runtime(hass)
    async_add_entities(
        [
            KuehlgeraetCockpitEnabledSwitch(runtime),
            KuehlgeraetCockpitSimulationSwitch(runtime),
        ],
        True,
    )


class _KuehlgeraetCockpitSwitch(SwitchEntity):
    """Base switch bound to runtime updates."""

    _attr_should_poll = False

    def __init__(self, runtime: KuehlgeraetCockpitRuntime) -> None:
        self._runtime = runtime

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        self.async_write_ha_state()


class KuehlgeraetCockpitEnabledSwitch(_KuehlgeraetCockpitSwitch):
    """Enable or disable the rule engine."""

    _attr_name = "Kuehlgeraet Cockpit Steuerung Regel-Engine aktiv"
    _attr_unique_id = ENABLED_SWITCH_UNIQUE_ID
    _attr_suggested_object_id = ENABLED_SWITCH_OBJECT_ID
    _attr_icon = "mdi:power-cycle"

    @property
    def is_on(self) -> bool:
        """Return whether the rule engine is enabled."""
        return self._runtime.enabled

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003, ARG002
        """Enable the rule engine."""
        await self._runtime.async_set_enabled(True)

    async def async_turn_off(self, **kwargs) -> None:  # noqa: ANN003, ARG002
        """Disable the rule engine."""
        await self._runtime.async_set_enabled(False)


class KuehlgeraetCockpitSimulationSwitch(_KuehlgeraetCockpitSwitch):
    """Enable or disable simulation mode."""

    _attr_name = "Kuehlgeraet Cockpit Steuerung Simulationsmodus aktiv"
    _attr_unique_id = SIMULATION_SWITCH_UNIQUE_ID
    _attr_suggested_object_id = SIMULATION_SWITCH_OBJECT_ID
    _attr_icon = "mdi:flask-outline"

    @property
    def is_on(self) -> bool:
        """Return whether simulation mode is enabled."""
        return self._runtime.simulation

    async def async_turn_on(self, **kwargs) -> None:  # noqa: ANN003, ARG002
        """Enable simulation mode."""
        await self._runtime.async_set_simulation(True)

    async def async_turn_off(self, **kwargs) -> None:  # noqa: ANN003, ARG002
        """Disable simulation mode."""
        await self._runtime.async_set_simulation(False)
