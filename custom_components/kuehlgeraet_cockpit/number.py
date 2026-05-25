"""Number entities for live rule tuning."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_CHEAP_OFF_TEMP,
    CONF_CHEAP_ON_TEMP,
    CONF_COMPRESSOR_RUNNING_WATTS,
    CONF_EXPENSIVE_OFF_TEMP,
    CONF_EXPENSIVE_ON_TEMP,
    CONF_MIN_OFF_SECONDS,
    CONF_MIN_ON_SECONDS,
    DOMAIN,
)
from .runtime import KuehlgeraetCockpitRuntime, async_get_runtime


@dataclass(frozen=True, slots=True)
class NumberDescription:
    """Description for a runtime number entity."""

    key: str
    name: str
    unit: str
    icon: str
    minimum: float
    maximum: float
    step: float
    object_id: str


NUMBER_DESCRIPTIONS = (
    NumberDescription(
        CONF_CHEAP_ON_TEMP,
        "Kuehlgeraet Cockpit Grenze guenstig einschalten ab",
        "C",
        "mdi:thermometer-plus",
        -30,
        30,
        0.1,
        "guenstig_einschalten_ab",
    ),
    NumberDescription(
        CONF_CHEAP_OFF_TEMP,
        "Kuehlgeraet Cockpit Grenze guenstig ausschalten bei",
        "C",
        "mdi:thermometer-minus",
        -30,
        30,
        0.1,
        "guenstig_ausschalten_bei",
    ),
    NumberDescription(
        CONF_EXPENSIVE_ON_TEMP,
        "Kuehlgeraet Cockpit Grenze teuer einschalten ab",
        "C",
        "mdi:thermometer-plus",
        -30,
        30,
        0.1,
        "teuer_einschalten_ab",
    ),
    NumberDescription(
        CONF_EXPENSIVE_OFF_TEMP,
        "Kuehlgeraet Cockpit Grenze teuer ausschalten bei",
        "C",
        "mdi:thermometer-minus",
        -30,
        30,
        0.1,
        "teuer_ausschalten_bei",
    ),
    NumberDescription(
        CONF_MIN_ON_SECONDS,
        "Kuehlgeraet Cockpit Schutz Mindest-Ein-Zeit",
        "s",
        "mdi:timer-play-outline",
        0,
        86400,
        30,
        "mindest_ein_zeit",
    ),
    NumberDescription(
        CONF_MIN_OFF_SECONDS,
        "Kuehlgeraet Cockpit Schutz Mindest-Aus-Zeit",
        "s",
        "mdi:timer-stop-outline",
        0,
        86400,
        30,
        "mindest_aus_zeit",
    ),
    NumberDescription(
        CONF_COMPRESSOR_RUNNING_WATTS,
        "Kuehlgeraet Cockpit Schutz Kompressor aktiv ab",
        "W",
        "mdi:flash",
        0,
        5000,
        1,
        "kompressor_aktiv_ab",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for a config entry."""
    runtime = await async_get_runtime(hass)
    async_add_entities(
        [
            KuehlgeraetCockpitNumber(runtime, description)
            for description in NUMBER_DESCRIPTIONS
        ],
        True,
    )


class KuehlgeraetCockpitNumber(NumberEntity):
    """Expose a numeric runtime setting."""

    _attr_should_poll = False

    def __init__(
        self,
        runtime: KuehlgeraetCockpitRuntime,
        description: NumberDescription,
    ) -> None:
        self._runtime = runtime
        self._description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_suggested_object_id = f"{DOMAIN}_{description.object_id}"
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit
        self._attr_native_min_value = description.minimum
        self._attr_native_max_value = description.maximum
        self._attr_native_step = description.step
        self._attr_mode = "box"

    @property
    def native_value(self) -> float | int | None:
        """Return the current setting value."""
        value = self._runtime.setting_value(self._description.key)
        if value is None:
            return None
        if self._description.key in {CONF_MIN_ON_SECONDS, CONF_MIN_OFF_SECONDS}:
            return int(value)
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Persist a new setting value in runtime storage."""
        await self._runtime.async_set_setting(self._description.key, value)

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        self.async_write_ha_state()
