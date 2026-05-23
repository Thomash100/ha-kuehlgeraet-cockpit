"""Binary sensors for Kuehlgeraet Cockpit."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .runtime import KuehlgeraetCockpitRuntime, async_get_runtime


@dataclass(frozen=True, slots=True)
class BinaryDescription:
    """Description for a runtime binary sensor."""

    key: str
    name: str
    icon_on: str
    icon_off: str


BINARY_DESCRIPTIONS = (
    BinaryDescription(
        "cheap_slot",
        "Kuehlgeraet Cockpit Preisfenster guenstig",
        "mdi:cash-check",
        "mdi:cash-clock",
    ),
    BinaryDescription(
        "compressor_running",
        "Kuehlgeraet Cockpit Kompressor laeuft",
        "mdi:engine",
        "mdi:engine-off",
    ),
    BinaryDescription(
        "price_data_valid",
        "Kuehlgeraet Cockpit Preisdaten aktiv",
        "mdi:chart-line",
        "mdi:chart-line-variant",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up binary sensors for a config entry."""
    runtime = await async_get_runtime(hass)
    async_add_entities(
        [
            KuehlgeraetCockpitBinarySensor(runtime, description)
            for description in BINARY_DESCRIPTIONS
        ],
        True,
    )


class KuehlgeraetCockpitBinarySensor(BinarySensorEntity):
    """Expose a boolean runtime status field."""

    _attr_should_poll = False

    def __init__(
        self,
        runtime: KuehlgeraetCockpitRuntime,
        description: BinaryDescription,
    ) -> None:
        self._runtime = runtime
        self._description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the binary state."""
        value = self._runtime.status.get(self._description.key)
        return bool(value) if value is not None else None

    @property
    def icon(self) -> str:
        """Return an icon matching the current state."""
        return (
            self._description.icon_on
            if self.is_on
            else self._description.icon_off
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        self.async_write_ha_state()
