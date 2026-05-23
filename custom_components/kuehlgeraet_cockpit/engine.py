"""Pure rule engine for Kuehlgeraet Cockpit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ACTION_NONE = "none"
ACTION_TURN_OFF = "turn_off"
ACTION_TURN_ON = "turn_on"

MODE_DISABLED = "Deaktiviert"
MODE_FAILSAFE = "Failsafe"
MODE_HOLD = "Halten"
MODE_MISSING_TARGET = "Ziel fehlt"
MODE_PROTECT = "Schutzzeit"
MODE_READY = "Bereit"
MODE_TURN_OFF = "Ausschalten"
MODE_TURN_ON = "Einschalten"


@dataclass(frozen=True, slots=True)
class RuleSettings:
    """Settings used by the rule engine."""

    enabled: bool
    simulation: bool
    failsafe_on: bool
    target_entity: str
    target_entity_configured: bool
    power_entity_configured: bool
    compressor_running_watts: float
    min_on_seconds: int
    min_off_seconds: int
    cheap_on_temp: float
    cheap_off_temp: float
    expensive_on_temp: float
    expensive_off_temp: float


@dataclass(frozen=True, slots=True)
class RuleSnapshot:
    """Current values read from Home Assistant."""

    target_state: str | None
    target_age_seconds: int | None
    temperature_c: float | None
    power_w: float | None
    price: float | None
    price_min: float | None
    price_max: float | None
    cheap_slot: bool | None


def as_float(value: Any) -> float | None:
    """Parse a Home Assistant state value as float."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)

    text = str(value).strip().replace(",", ".")
    if not text or text.lower() in {"unknown", "unavailable", "none", "null"}:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def as_bool(value: Any) -> bool | None:
    """Parse common Home Assistant boolean state values."""
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"on", "true", "yes", "1", "open", "home"}:
        return True
    if text in {"off", "false", "no", "0", "closed", "not_home"}:
        return False
    return None


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _price_position(snapshot: RuleSnapshot) -> tuple[float, bool, str]:
    """Return price position from cheap (0.0) to expensive (1.0)."""
    if (
        snapshot.price is not None
        and snapshot.price_min is not None
        and snapshot.price_max is not None
        and snapshot.price_max > snapshot.price_min
    ):
        position = (snapshot.price - snapshot.price_min) / (
            snapshot.price_max - snapshot.price_min
        )
        return _clamp(position), True, "price_range"

    if snapshot.cheap_slot is not None:
        return (0.0 if snapshot.cheap_slot else 1.0), True, "cheap_flag"

    return 0.5, False, "fallback_midpoint"


def _interpolate(cheap_value: float, expensive_value: float, position: float) -> float:
    return cheap_value + ((expensive_value - cheap_value) * position)


def evaluate_rules(
    settings: RuleSettings,
    snapshot: RuleSnapshot,
) -> dict[str, Any]:
    """Evaluate the refrigerator rules and return a serializable status."""
    position, price_data_valid, price_source = _price_position(snapshot)
    price_factor = round(1.0 - position, 3)
    on_temp = round(
        _interpolate(settings.cheap_on_temp, settings.expensive_on_temp, position),
        2,
    )
    off_temp = round(
        _interpolate(settings.cheap_off_temp, settings.expensive_off_temp, position),
        2,
    )
    compressor_running = (
        snapshot.power_w is not None
        and snapshot.power_w >= settings.compressor_running_watts
    )
    target_is_on = snapshot.target_state == "on"
    target_is_off = snapshot.target_state == "off"
    target_age = snapshot.target_age_seconds
    min_on_reached = target_age is not None and target_age >= settings.min_on_seconds
    min_off_reached = target_age is not None and target_age >= settings.min_off_seconds

    status: dict[str, Any] = {
        "mode": MODE_READY,
        "mode_key": "ready",
        "planned_action_key": ACTION_NONE,
        "planned_action": "Keine Aktion",
        "reason": "Regelgrenzen sind eingehalten.",
        "target_entity": settings.target_entity,
        "target_state": snapshot.target_state,
        "target_age_seconds": target_age,
        "temperature_c": snapshot.temperature_c,
        "power_w": snapshot.power_w,
        "price": snapshot.price,
        "price_min": snapshot.price_min,
        "price_max": snapshot.price_max,
        "cheap_slot": snapshot.cheap_slot,
        "price_data_valid": price_data_valid,
        "price_source": price_source,
        "price_position": round(position, 3),
        "price_factor": price_factor,
        "selected_on_temp": on_temp,
        "selected_off_temp": off_temp,
        "cheap_on_temp": settings.cheap_on_temp,
        "cheap_off_temp": settings.cheap_off_temp,
        "expensive_on_temp": settings.expensive_on_temp,
        "expensive_off_temp": settings.expensive_off_temp,
        "compressor_running": compressor_running,
        "compressor_running_watts": settings.compressor_running_watts,
        "min_on_seconds": settings.min_on_seconds,
        "min_off_seconds": settings.min_off_seconds,
        "enabled": settings.enabled,
        "simulation": settings.simulation,
    }

    def decide(mode: str, mode_key: str, action: str, reason: str) -> dict[str, Any]:
        planned_action = {
            ACTION_NONE: "Keine Aktion",
            ACTION_TURN_ON: "Einschalten",
            ACTION_TURN_OFF: "Ausschalten",
        }[action]
        status.update(
            {
                "mode": mode,
                "mode_key": mode_key,
                "planned_action_key": action,
                "planned_action": planned_action,
                "reason": reason,
            }
        )
        return status

    if not settings.enabled:
        return decide(
            MODE_DISABLED,
            "disabled",
            ACTION_NONE,
            "Die Regel-Engine ist deaktiviert.",
        )

    if not settings.target_entity_configured:
        return decide(
            MODE_MISSING_TARGET,
            "target_not_configured",
            ACTION_NONE,
            "Es ist keine Ziel-Entitaet konfiguriert.",
        )

    if snapshot.target_state is None:
        return decide(
            MODE_MISSING_TARGET,
            "target_missing",
            ACTION_NONE,
            "Die Ziel-Entitaet ist in Home Assistant nicht verfuegbar.",
        )

    if not target_is_on and not target_is_off:
        return decide(
            MODE_HOLD,
            "target_state_unsupported",
            ACTION_NONE,
            "Die Ziel-Entitaet ist weder on noch off.",
        )

    if snapshot.temperature_c is None:
        if settings.failsafe_on and target_is_off and min_off_reached:
            return decide(
                MODE_FAILSAFE,
                "failsafe_turn_on",
                ACTION_TURN_ON,
                "Keine Temperaturdaten: Failsafe schaltet die Kuehlung ein.",
            )
        return decide(
            MODE_FAILSAFE,
            "temperature_missing",
            ACTION_NONE,
            "Keine Temperaturdaten; ohne Schaltbedarf bleibt der aktuelle Zustand.",
        )

    if target_is_off and not min_off_reached:
        return decide(
            MODE_PROTECT,
            "min_off_time",
            ACTION_NONE,
            "Mindest-Aus-Zeit ist noch nicht erreicht.",
        )

    if target_is_on and not min_on_reached:
        return decide(
            MODE_PROTECT,
            "min_on_time",
            ACTION_NONE,
            "Mindest-Ein-Zeit ist noch nicht erreicht.",
        )

    if target_is_off and snapshot.temperature_c >= on_temp:
        return decide(
            MODE_TURN_ON,
            ACTION_TURN_ON,
            ACTION_TURN_ON,
            (
                "Temperatur liegt ueber der preisabhaengigen "
                f"Einschaltschwelle von {on_temp} C."
            ),
        )

    if target_is_on and snapshot.temperature_c <= off_temp:
        if settings.power_entity_configured and snapshot.power_w is None:
            return decide(
                MODE_HOLD,
                "power_missing",
                ACTION_NONE,
                "Leistungsdaten fehlen; Ausschalten wird vorsichtshalber blockiert.",
            )
        if compressor_running:
            return decide(
                MODE_HOLD,
                "compressor_running",
                ACTION_NONE,
                "Kompressor laeuft laut Leistungsdaten; Ausschalten wird blockiert.",
            )
        return decide(
            MODE_TURN_OFF,
            ACTION_TURN_OFF,
            ACTION_TURN_OFF,
            (
                "Temperatur liegt unter der preisabhaengigen "
                f"Ausschaltschwelle von {off_temp} C."
            ),
        )

    return status
