"""Runtime control loop for Kuehlgeraet Cockpit."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta, timezone
from inspect import isawaitable
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Context, HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.script import Script, async_validate_actions_config
from homeassistant.helpers.storage import Store
import homeassistant.util.dt as dt_util

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
    CONF_TURN_OFF_ACTION_ENTITIES,
    CONF_TURN_OFF_ACTIONS,
    CONF_TURN_OFF_SERVICE,
    CONF_TURN_ON_ACTION_ENTITIES,
    CONF_TURN_ON_ACTIONS,
    CONF_TURN_ON_SERVICE,
    DATA_RUNTIME,
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
    DEFAULT_TARGET_ENTITIES,
    DEFAULT_TEMPERATURE_ENTITY,
    DEFAULT_TURN_OFF_ACTION_ENTITIES,
    DEFAULT_TURN_OFF_ACTIONS,
    DEFAULT_TURN_OFF_SERVICE,
    DEFAULT_TURN_ON_ACTION_ENTITIES,
    DEFAULT_TURN_ON_ACTIONS,
    DEFAULT_TURN_ON_SERVICE,
    DOMAIN,
    NUMERIC_SETTING_DEFAULTS,
    RUNTIME_SETTING_KEYS,
    STORAGE_KEY,
    STORAGE_VERSION,
)
from .engine import (
    ACTION_NONE,
    ACTION_TURN_OFF,
    ACTION_TURN_ON,
    RuleSettings,
    RuleSnapshot,
    as_bool,
    as_float,
    evaluate_rules,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_SETTINGS: dict[str, Any] = {
    CONF_TARGET_ENTITY: DEFAULT_TARGET_ENTITIES,
    CONF_TURN_ON_SERVICE: DEFAULT_TURN_ON_SERVICE,
    CONF_TURN_OFF_SERVICE: DEFAULT_TURN_OFF_SERVICE,
    CONF_TURN_ON_ACTION_ENTITIES: DEFAULT_TURN_ON_ACTION_ENTITIES,
    CONF_TURN_OFF_ACTION_ENTITIES: DEFAULT_TURN_OFF_ACTION_ENTITIES,
    CONF_TURN_ON_ACTIONS: DEFAULT_TURN_ON_ACTIONS,
    CONF_TURN_OFF_ACTIONS: DEFAULT_TURN_OFF_ACTIONS,
    CONF_TEMPERATURE_ENTITY: DEFAULT_TEMPERATURE_ENTITY,
    CONF_POWER_ENTITY: DEFAULT_POWER_ENTITY,
    CONF_PRICE_ENTITY: DEFAULT_PRICE_ENTITY,
    CONF_PRICE_MIN_ENTITY: DEFAULT_PRICE_MIN_ENTITY,
    CONF_PRICE_MAX_ENTITY: DEFAULT_PRICE_MAX_ENTITY,
    CONF_CHEAP_ENTITY: DEFAULT_CHEAP_ENTITY,
    CONF_AUTO_APPLY: DEFAULT_AUTO_APPLY,
    CONF_FAILSAFE_ON: DEFAULT_FAILSAFE_ON,
    CONF_EVALUATION_INTERVAL: DEFAULT_EVALUATION_INTERVAL,
    CONF_COMPRESSOR_RUNNING_WATTS: DEFAULT_COMPRESSOR_RUNNING_WATTS,
    CONF_MIN_ON_SECONDS: DEFAULT_MIN_ON_SECONDS,
    CONF_MIN_OFF_SECONDS: DEFAULT_MIN_OFF_SECONDS,
    CONF_CHEAP_ON_TEMP: DEFAULT_CHEAP_ON_TEMP,
    CONF_CHEAP_OFF_TEMP: DEFAULT_CHEAP_OFF_TEMP,
    CONF_EXPENSIVE_ON_TEMP: DEFAULT_EXPENSIVE_ON_TEMP,
    CONF_EXPENSIVE_OFF_TEMP: DEFAULT_EXPENSIVE_OFF_TEMP,
}

ENTITY_SETTING_KEYS = (
    CONF_TEMPERATURE_ENTITY,
    CONF_POWER_ENTITY,
    CONF_PRICE_ENTITY,
    CONF_PRICE_MIN_ENTITY,
    CONF_PRICE_MAX_ENTITY,
    CONF_CHEAP_ENTITY,
)

LIST_ENTITY_SETTING_KEYS = (
    CONF_TARGET_ENTITY,
    CONF_TURN_ON_ACTION_ENTITIES,
    CONF_TURN_OFF_ACTION_ENTITIES,
)

ACTION_SETTING_KEYS = (
    CONF_TURN_ON_ACTIONS,
    CONF_TURN_OFF_ACTIONS,
)


def _entity_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list | tuple | set):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _action_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _primary_entity(value: Any) -> str:
    entities = _entity_list(value)
    return entities[0] if entities else DEFAULT_TARGET_ENTITY


class KuehlgeraetCockpitRuntime:
    """Keep rule-engine state, settings, and Home Assistant listeners."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._entry: ConfigEntry | None = None
        self._status: dict[str, Any] = {}
        self._settings: dict[str, Any] = {}
        self._enabled = True
        self._simulation = False
        self._listeners: list[Callable[[], None]] = []
        self._unsubscribers: list[Callable[[], None]] = []
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)

    @property
    def status(self) -> dict[str, Any]:
        """Return the latest rule-engine status."""
        return self._status

    @property
    def enabled(self) -> bool:
        """Return whether automatic decisions are enabled."""
        return self._enabled

    @property
    def simulation(self) -> bool:
        """Return whether actions are simulated instead of sent."""
        return self._simulation

    def setting_value(self, key: str) -> Any:
        """Return a merged setting value."""
        return self.settings.get(key)

    @property
    def settings(self) -> dict[str, Any]:
        """Return entry defaults merged with runtime overrides."""
        merged = dict(DEFAULT_SETTINGS)
        if self._entry is not None:
            merged.update(self._entry.data)
            merged.update(self._entry.options)
        merged.update(self._settings)

        for key in LIST_ENTITY_SETTING_KEYS:
            merged[key] = _entity_list(merged.get(key))

        for key in ACTION_SETTING_KEYS:
            merged[key] = _action_list(merged.get(key))

        for key in ENTITY_SETTING_KEYS:
            merged[key] = str(merged.get(key) or "").strip()

        merged[CONF_TURN_ON_SERVICE] = str(
            merged.get(CONF_TURN_ON_SERVICE) or DEFAULT_TURN_ON_SERVICE
        ).strip()
        merged[CONF_TURN_OFF_SERVICE] = str(
            merged.get(CONF_TURN_OFF_SERVICE) or DEFAULT_TURN_OFF_SERVICE
        ).strip()

        merged[CONF_AUTO_APPLY] = bool(merged.get(CONF_AUTO_APPLY, DEFAULT_AUTO_APPLY))
        merged[CONF_FAILSAFE_ON] = bool(
            merged.get(CONF_FAILSAFE_ON, DEFAULT_FAILSAFE_ON)
        )
        merged[CONF_EVALUATION_INTERVAL] = max(
            30,
            int(merged.get(CONF_EVALUATION_INTERVAL, DEFAULT_EVALUATION_INTERVAL)),
        )
        merged[CONF_MIN_ON_SECONDS] = max(
            0,
            int(merged.get(CONF_MIN_ON_SECONDS, DEFAULT_MIN_ON_SECONDS)),
        )
        merged[CONF_MIN_OFF_SECONDS] = max(
            0,
            int(merged.get(CONF_MIN_OFF_SECONDS, DEFAULT_MIN_OFF_SECONDS)),
        )

        for key, default in NUMERIC_SETTING_DEFAULTS.items():
            if key not in {CONF_MIN_ON_SECONDS, CONF_MIN_OFF_SECONDS}:
                merged[key] = float(merged.get(key, default))

        return merged

    async def async_load(self) -> None:
        """Load the last stored runtime payload from disk."""
        stored = await self._store.async_load()
        if not isinstance(stored, dict):
            return

        if "status" not in stored:
            self._status = stored
            return

        self._status = dict(stored.get("status") or {})
        self._settings = {
            key: value
            for key, value in dict(stored.get("settings") or {}).items()
            if key in RUNTIME_SETTING_KEYS
        }
        self._enabled = bool(stored.get("enabled", True))
        self._simulation = bool(stored.get("simulation", False))

    async def async_save(self) -> None:
        """Persist runtime state."""
        await self._store.async_save(
            {
                "status": self._status,
                "settings": self._settings,
                "enabled": self._enabled,
                "simulation": self._simulation,
            }
        )

    async def async_setup_entry(self, entry: ConfigEntry) -> None:
        """Attach a config entry and start tracking configured entities."""
        self._entry = entry
        self._reset_tracking()
        await self.async_evaluate(apply_decision=False, reason="startup")

    async def async_unload_entry(self, entry: ConfigEntry) -> None:
        """Detach a config entry and stop listeners."""
        if self._entry is entry:
            self._entry = None
        self._clear_unsubscribers()

    async def async_set_enabled(self, enabled: bool) -> None:
        """Enable or disable the rule engine."""
        self._enabled = bool(enabled)
        await self.async_evaluate(apply_decision=False, reason="set_enabled")

    async def async_set_simulation(self, enabled: bool) -> None:
        """Enable or disable simulation mode."""
        self._simulation = bool(enabled)
        await self.async_evaluate(apply_decision=False, reason="set_simulation")

    async def async_set_setting(self, key: str, value: Any) -> None:
        """Update a runtime numeric setting."""
        if key not in RUNTIME_SETTING_KEYS:
            raise HomeAssistantError(f"Unbekannte Einstellung: {key}")

        numeric_value = as_float(value)
        if numeric_value is None:
            raise HomeAssistantError(f"Einstellung {key} muss numerisch sein.")

        if key in {CONF_MIN_ON_SECONDS, CONF_MIN_OFF_SECONDS}:
            self._settings[key] = max(0, int(numeric_value))
        elif key == CONF_COMPRESSOR_RUNNING_WATTS:
            self._settings[key] = max(0.0, float(numeric_value))
        else:
            self._settings[key] = float(numeric_value)

        await self.async_evaluate(apply_decision=False, reason="set_setting")

    async def async_set_status(self, status: dict[str, Any]) -> None:
        """Legacy helper to overwrite the exposed status payload."""
        self._status = dict(status)
        await self.async_save()
        self._notify()

    async def async_evaluate(
        self,
        *,
        apply_decision: bool,
        reason: str = "manual",
    ) -> dict[str, Any]:
        """Evaluate rules and optionally apply the planned decision."""
        settings = self.settings
        rule_settings = self._build_rule_settings(settings)
        snapshot = self._build_snapshot(settings)
        status = evaluate_rules(rule_settings, snapshot)
        status.update(
            {
                "auto_apply": settings[CONF_AUTO_APPLY],
                "evaluation_interval": settings[CONF_EVALUATION_INTERVAL],
                "target_entities": settings[CONF_TARGET_ENTITY],
                "turn_on_service": settings[CONF_TURN_ON_SERVICE],
                "turn_off_service": settings[CONF_TURN_OFF_SERVICE],
                "turn_on_action_entities": settings[CONF_TURN_ON_ACTION_ENTITIES],
                "turn_off_action_entities": settings[CONF_TURN_OFF_ACTION_ENTITIES],
                "turn_on_actions_count": len(settings[CONF_TURN_ON_ACTIONS]),
                "turn_off_actions_count": len(settings[CONF_TURN_OFF_ACTIONS]),
                "temperature_entity": settings[CONF_TEMPERATURE_ENTITY],
                "power_entity": settings[CONF_POWER_ENTITY],
                "price_entity": settings[CONF_PRICE_ENTITY],
                "price_min_entity": settings[CONF_PRICE_MIN_ENTITY],
                "price_max_entity": settings[CONF_PRICE_MAX_ENTITY],
                "cheap_entity": settings[CONF_CHEAP_ENTITY],
                "trigger": reason,
                "updated_at": dt_util.utcnow().isoformat(),
                "applied_action_key": ACTION_NONE,
                "applied_action": "Keine Aktion",
                "apply_blocked_by": None,
            }
        )

        planned_action = status.get("planned_action_key")
        can_apply = planned_action in {ACTION_TURN_ON, ACTION_TURN_OFF}

        if apply_decision and can_apply:
            if not self._enabled:
                status["apply_blocked_by"] = "disabled"
            elif self._simulation:
                status["apply_blocked_by"] = "simulation"
            else:
                await self._async_apply_action(planned_action, settings, status)

        self._status = status
        await self.async_save()
        self._notify()
        return status

    def async_listen(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register a callback for status updates."""
        self._listeners.append(listener)

        def _unsubscribe() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _unsubscribe

    def _build_rule_settings(self, settings: dict[str, Any]) -> RuleSettings:
        target_entity = _primary_entity(settings[CONF_TARGET_ENTITY])
        return RuleSettings(
            enabled=self._enabled,
            simulation=self._simulation,
            failsafe_on=settings[CONF_FAILSAFE_ON],
            target_entity=target_entity,
            target_entity_configured=bool(target_entity),
            power_entity_configured=bool(settings[CONF_POWER_ENTITY]),
            compressor_running_watts=settings[CONF_COMPRESSOR_RUNNING_WATTS],
            min_on_seconds=settings[CONF_MIN_ON_SECONDS],
            min_off_seconds=settings[CONF_MIN_OFF_SECONDS],
            cheap_on_temp=settings[CONF_CHEAP_ON_TEMP],
            cheap_off_temp=settings[CONF_CHEAP_OFF_TEMP],
            expensive_on_temp=settings[CONF_EXPENSIVE_ON_TEMP],
            expensive_off_temp=settings[CONF_EXPENSIVE_OFF_TEMP],
        )

    def _build_snapshot(self, settings: dict[str, Any]) -> RuleSnapshot:
        target = self._state(_primary_entity(settings[CONF_TARGET_ENTITY]))
        price_state = self._state(settings[CONF_PRICE_ENTITY])

        return RuleSnapshot(
            target_state=(target.state if target is not None else None),
            target_age_seconds=self._state_age_seconds(target),
            temperature_c=self._float_state(settings[CONF_TEMPERATURE_ENTITY]),
            power_w=self._float_state(settings[CONF_POWER_ENTITY]),
            price=as_float(price_state.state) if price_state is not None else None,
            price_min=self._price_boundary(
                settings[CONF_PRICE_MIN_ENTITY],
                price_state,
                ("min_price", "today_min", "min"),
            ),
            price_max=self._price_boundary(
                settings[CONF_PRICE_MAX_ENTITY],
                price_state,
                ("max_price", "today_max", "max"),
            ),
            cheap_slot=self._bool_state(settings[CONF_CHEAP_ENTITY]),
        )

    async def _async_apply_action(
        self,
        action: str,
        settings: dict[str, Any],
        status: dict[str, Any],
    ) -> None:
        service_name = (
            settings[CONF_TURN_ON_SERVICE]
            if action == ACTION_TURN_ON
            else settings[CONF_TURN_OFF_SERVICE]
        )
        target_entities = settings[CONF_TARGET_ENTITY]
        action_entities = (
            settings[CONF_TURN_ON_ACTION_ENTITIES]
            if action == ACTION_TURN_ON
            else settings[CONF_TURN_OFF_ACTION_ENTITIES]
        )
        actions = (
            settings[CONF_TURN_ON_ACTIONS]
            if action == ACTION_TURN_ON
            else settings[CONF_TURN_OFF_ACTIONS]
        )
        service_calls: list[str] = []

        try:
            if target_entities:
                domain, service = self._split_service(service_name)
                await self.hass.services.async_call(
                    domain,
                    service,
                    {"entity_id": target_entities},
                    blocking=True,
                )
                service_calls.append(f"{domain}.{service}")

            if action_entities:
                await self.hass.services.async_call(
                    "homeassistant",
                    "turn_on",
                    {"entity_id": action_entities},
                    blocking=True,
                )
                service_calls.append("homeassistant.turn_on")

            if actions:
                await self._async_run_actions(action, actions)
                service_calls.append(f"action_sequence:{len(actions)}")
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Kuehlgeraet Cockpit konnte %s nicht ausfuehren", action)
            status["apply_blocked_by"] = "service_error"
            status["error"] = str(err)
            return

        status["applied_action_key"] = action
        status["applied_action"] = {
            ACTION_TURN_ON: "Einschalten gesendet",
            ACTION_TURN_OFF: "Ausschalten gesendet",
        }[action]
        status["applied_services"] = service_calls
        status["last_action_at"] = dt_util.utcnow().isoformat()

    async def _async_run_actions(
        self,
        action: str,
        actions: list[dict[str, Any]],
    ) -> None:
        validated_actions = await async_validate_actions_config(self.hass, actions)
        script = Script(
            self.hass,
            validated_actions,
            f"Kuehlgeraet Cockpit {action}",
            DOMAIN,
            top_level=False,
        )
        try:
            await script.async_run(context=Context())
        finally:
            unload = getattr(script, "async_unload", None)
            if unload is not None:
                unload_result = unload()
                if isawaitable(unload_result):
                    await unload_result

    def _split_service(self, service_name: str) -> tuple[str, str]:
        if "." not in service_name:
            raise HomeAssistantError(
                f"Dienst muss als domain.service angegeben werden: {service_name}"
            )
        domain, service = service_name.split(".", 1)
        if not domain or not service:
            raise HomeAssistantError(
                f"Dienst muss als domain.service angegeben werden: {service_name}"
            )
        return domain, service

    def _state(self, entity_id: str) -> State | None:
        if not entity_id:
            return None
        return self.hass.states.get(entity_id)

    def _float_state(self, entity_id: str) -> float | None:
        state = self._state(entity_id)
        return as_float(state.state) if state is not None else None

    def _bool_state(self, entity_id: str) -> bool | None:
        state = self._state(entity_id)
        return as_bool(state.state) if state is not None else None

    def _price_boundary(
        self,
        entity_id: str,
        price_state: State | None,
        attribute_names: tuple[str, ...],
    ) -> float | None:
        explicit_value = self._float_state(entity_id)
        if explicit_value is not None:
            return explicit_value

        if price_state is None:
            return None

        for attribute_name in attribute_names:
            value = as_float(price_state.attributes.get(attribute_name))
            if value is not None:
                return value
        return None

    def _state_age_seconds(self, state: State | None) -> int | None:
        if state is None:
            return None
        now = dt_util.utcnow()
        last_changed = state.last_changed
        if now.tzinfo is None and last_changed.tzinfo is not None:
            now = now.replace(tzinfo=timezone.utc)
        if now.tzinfo is not None and last_changed.tzinfo is None:
            last_changed = last_changed.replace(tzinfo=timezone.utc)
        age = now - last_changed
        return max(0, int(age.total_seconds()))

    def _reset_tracking(self) -> None:
        self._clear_unsubscribers()
        settings = self.settings
        entities = [
            entity_id
            for entity_id in dict.fromkeys(
                [
                    *settings[CONF_TARGET_ENTITY],
                    *(
                        str(settings.get(key) or "").strip()
                        for key in ENTITY_SETTING_KEYS
                    ),
                ]
            )
            if entity_id
        ]

        if entities:
            self._unsubscribers.append(
                async_track_state_change_event(
                    self.hass,
                    entities,
                    self._handle_state_change,
                )
            )

        interval = timedelta(seconds=settings[CONF_EVALUATION_INTERVAL])
        self._unsubscribers.append(
            async_track_time_interval(self.hass, self._handle_interval, interval)
        )

    def _clear_unsubscribers(self) -> None:
        for unsubscribe in self._unsubscribers:
            unsubscribe()
        self._unsubscribers.clear()

    @callback
    def _handle_state_change(self, event: Any) -> None:  # noqa: ARG002
        settings = self.settings
        self.hass.async_create_task(
            self.async_evaluate(
                apply_decision=settings[CONF_AUTO_APPLY],
                reason="state_change",
            )
        )

    @callback
    def _handle_interval(self, now: Any) -> None:  # noqa: ARG002
        settings = self.settings
        self.hass.async_create_task(
            self.async_evaluate(
                apply_decision=settings[CONF_AUTO_APPLY],
                reason="interval",
            )
        )

    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()


async def async_get_runtime(hass: HomeAssistant) -> KuehlgeraetCockpitRuntime:
    """Return the shared integration runtime."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    runtime = domain_data.get(DATA_RUNTIME)
    if runtime is None:
        runtime = KuehlgeraetCockpitRuntime(hass)
        await runtime.async_load()
        domain_data[DATA_RUNTIME] = runtime
    return runtime
