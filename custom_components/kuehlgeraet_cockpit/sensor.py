"""Sensor platform for Kuehlgeraet Cockpit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, STATUS_SENSOR_NAME, STATUS_SENSOR_UNIQUE_ID
from .runtime import KuehlgeraetCockpitRuntime, async_get_runtime


@dataclass(frozen=True, slots=True)
class MetricDescription:
    """Description for a metric exposed from runtime status."""

    key: str
    name: str
    unit: str | None
    icon: str


METRIC_DESCRIPTIONS = (
    MetricDescription("temperature_c", "Kuehlgeraet Cockpit Temperatur", "C", "mdi:thermometer"),
    MetricDescription("power_w", "Kuehlgeraet Cockpit Leistung", "W", "mdi:flash"),
    MetricDescription("price", "Kuehlgeraet Cockpit Strompreis", None, "mdi:currency-eur"),
    MetricDescription("price_factor", "Kuehlgeraet Cockpit Preisfaktor", "%", "mdi:chart-bell-curve"),
    MetricDescription("selected_on_temp", "Kuehlgeraet Cockpit Einschaltgrenze", "C", "mdi:thermometer-plus"),
    MetricDescription("selected_off_temp", "Kuehlgeraet Cockpit Ausschaltgrenze", "C", "mdi:thermometer-minus"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,  # noqa: ARG001
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors for a config entry."""
    runtime = await async_get_runtime(hass)
    entities: list[SensorEntity] = [KuehlgeraetCockpitStatusSensor(runtime)]
    entities.extend(
        KuehlgeraetCockpitMetricSensor(runtime, description)
        for description in METRIC_DESCRIPTIONS
    )
    async_add_entities(entities, True)


class KuehlgeraetCockpitStatusSensor(SensorEntity):
    """Expose the latest rule-engine status."""

    _attr_name = STATUS_SENSOR_NAME
    _attr_unique_id = STATUS_SENSOR_UNIQUE_ID
    _attr_icon = "mdi:fridge-outline"
    _attr_should_poll = False

    def __init__(self, runtime: KuehlgeraetCockpitRuntime) -> None:
        self._runtime = runtime

    @property
    def native_value(self) -> str:
        """Return the primary status."""
        return str(self._runtime.status.get("mode") or "Bereit")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the full status payload as attributes."""
        return dict(self._runtime.status)

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        self.async_write_ha_state()


class KuehlgeraetCockpitMetricSensor(SensorEntity):
    """Expose a numeric status field as a regular Home Assistant sensor."""

    _attr_should_poll = False

    def __init__(
        self,
        runtime: KuehlgeraetCockpitRuntime,
        description: MetricDescription,
    ) -> None:
        self._runtime = runtime
        self._description = description
        self._attr_name = description.name
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_icon = description.icon
        self._attr_native_unit_of_measurement = description.unit
        self._attr_suggested_display_precision = 2

    @property
    def native_value(self) -> float | None:
        """Return the numeric metric value."""
        value = self._runtime.status.get(self._description.key)
        if value is None:
            return None
        if self._description.key == "price_factor":
            return round(float(value) * 100, 1)
        return float(value)

    @property
    def available(self) -> bool:
        """Return whether the metric is available."""
        return self._runtime.status.get(self._description.key) is not None

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime updates."""
        self.async_on_remove(self._runtime.async_listen(self._handle_status_updated))

    @callback
    def _handle_status_updated(self) -> None:
        self.async_write_ha_state()
