"""Config flow for Kuehlgeraet Cockpit."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    ActionSelector,
    EntitySelector,
    EntitySelectorConfig,
)

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
)


def _entity_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list | tuple | set):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _entity_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _action_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


def _defaults(source: dict[str, Any]) -> dict[str, Any]:
    target_entities = _entity_list(
        source.get(CONF_TARGET_ENTITY, DEFAULT_TARGET_ENTITIES)
    )
    if not target_entities:
        target_entities = _entity_list(
            source.get(CONF_TARGET_ENTITY, DEFAULT_TARGET_ENTITY)
        )

    return {
        CONF_TARGET_ENTITY: target_entities,
        CONF_TURN_ON_SERVICE: source.get(
            CONF_TURN_ON_SERVICE,
            DEFAULT_TURN_ON_SERVICE,
        ),
        CONF_TURN_OFF_SERVICE: source.get(
            CONF_TURN_OFF_SERVICE,
            DEFAULT_TURN_OFF_SERVICE,
        ),
        CONF_TURN_ON_ACTION_ENTITIES: _entity_list(
            source.get(
                CONF_TURN_ON_ACTION_ENTITIES,
                DEFAULT_TURN_ON_ACTION_ENTITIES,
            )
        ),
        CONF_TURN_OFF_ACTION_ENTITIES: _entity_list(
            source.get(
                CONF_TURN_OFF_ACTION_ENTITIES,
                DEFAULT_TURN_OFF_ACTION_ENTITIES,
            )
        ),
        CONF_TURN_ON_ACTIONS: _action_list(
            source.get(CONF_TURN_ON_ACTIONS, DEFAULT_TURN_ON_ACTIONS)
        ),
        CONF_TURN_OFF_ACTIONS: _action_list(
            source.get(CONF_TURN_OFF_ACTIONS, DEFAULT_TURN_OFF_ACTIONS)
        ),
        CONF_TEMPERATURE_ENTITY: _entity_value(
            source.get(CONF_TEMPERATURE_ENTITY, DEFAULT_TEMPERATURE_ENTITY)
        ),
        CONF_POWER_ENTITY: _entity_value(
            source.get(CONF_POWER_ENTITY, DEFAULT_POWER_ENTITY)
        ),
        CONF_PRICE_ENTITY: _entity_value(
            source.get(CONF_PRICE_ENTITY, DEFAULT_PRICE_ENTITY)
        ),
        CONF_PRICE_MIN_ENTITY: _entity_value(
            source.get(CONF_PRICE_MIN_ENTITY, DEFAULT_PRICE_MIN_ENTITY)
        ),
        CONF_PRICE_MAX_ENTITY: _entity_value(
            source.get(CONF_PRICE_MAX_ENTITY, DEFAULT_PRICE_MAX_ENTITY)
        ),
        CONF_CHEAP_ENTITY: _entity_value(
            source.get(CONF_CHEAP_ENTITY, DEFAULT_CHEAP_ENTITY)
        ),
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


def _optional_entity_selector(
    field: str,
    default: str,
) -> tuple[vol.Optional, EntitySelector]:
    marker = vol.Optional(field, default=default) if default else vol.Optional(field)
    return marker, EntitySelector()


def _normalize_input(user_input: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(user_input)
    normalized[CONF_TARGET_ENTITY] = _entity_list(user_input.get(CONF_TARGET_ENTITY))
    normalized[CONF_TURN_ON_ACTION_ENTITIES] = _entity_list(
        user_input.get(CONF_TURN_ON_ACTION_ENTITIES)
    )
    normalized[CONF_TURN_OFF_ACTION_ENTITIES] = _entity_list(
        user_input.get(CONF_TURN_OFF_ACTION_ENTITIES)
    )
    normalized[CONF_TURN_ON_ACTIONS] = _action_list(
        user_input.get(CONF_TURN_ON_ACTIONS)
    )
    normalized[CONF_TURN_OFF_ACTIONS] = _action_list(
        user_input.get(CONF_TURN_OFF_ACTIONS)
    )
    for key in (
        CONF_TEMPERATURE_ENTITY,
        CONF_POWER_ENTITY,
        CONF_PRICE_ENTITY,
        CONF_PRICE_MIN_ENTITY,
        CONF_PRICE_MAX_ENTITY,
        CONF_CHEAP_ENTITY,
        CONF_TURN_ON_SERVICE,
        CONF_TURN_OFF_SERVICE,
    ):
        normalized[key] = _entity_value(user_input.get(key))
    return normalized


def _service_valid(service_name: str) -> bool:
    domain, separator, service = service_name.partition(".")
    return bool(domain and separator and service)


def _build_schema(defaults: dict[str, Any]) -> vol.Schema:
    temperature_selector = _optional_entity_selector(
        CONF_TEMPERATURE_ENTITY,
        defaults[CONF_TEMPERATURE_ENTITY],
    )
    power_selector = _optional_entity_selector(
        CONF_POWER_ENTITY,
        defaults[CONF_POWER_ENTITY],
    )
    price_selector = _optional_entity_selector(
        CONF_PRICE_ENTITY,
        defaults[CONF_PRICE_ENTITY],
    )
    price_min_selector = _optional_entity_selector(
        CONF_PRICE_MIN_ENTITY,
        defaults[CONF_PRICE_MIN_ENTITY],
    )
    price_max_selector = _optional_entity_selector(
        CONF_PRICE_MAX_ENTITY,
        defaults[CONF_PRICE_MAX_ENTITY],
    )
    cheap_selector = _optional_entity_selector(
        CONF_CHEAP_ENTITY,
        defaults[CONF_CHEAP_ENTITY],
    )

    return vol.Schema(
        {
            vol.Required(
                CONF_TARGET_ENTITY,
                default=defaults[CONF_TARGET_ENTITY],
            ): EntitySelector(EntitySelectorConfig(multiple=True, reorder=True)),
            vol.Required(
                CONF_TURN_ON_SERVICE,
                default=defaults[CONF_TURN_ON_SERVICE],
            ): str,
            vol.Required(
                CONF_TURN_OFF_SERVICE,
                default=defaults[CONF_TURN_OFF_SERVICE],
            ): str,
            vol.Optional(
                CONF_TURN_ON_ACTION_ENTITIES,
                default=defaults[CONF_TURN_ON_ACTION_ENTITIES],
            ): EntitySelector(EntitySelectorConfig(multiple=True, reorder=True)),
            vol.Optional(
                CONF_TURN_OFF_ACTION_ENTITIES,
                default=defaults[CONF_TURN_OFF_ACTION_ENTITIES],
            ): EntitySelector(EntitySelectorConfig(multiple=True, reorder=True)),
            vol.Optional(
                CONF_TURN_ON_ACTIONS,
                default=defaults[CONF_TURN_ON_ACTIONS],
            ): ActionSelector(),
            vol.Optional(
                CONF_TURN_OFF_ACTIONS,
                default=defaults[CONF_TURN_OFF_ACTIONS],
            ): ActionSelector(),
            temperature_selector[0]: temperature_selector[1],
            power_selector[0]: power_selector[1],
            price_selector[0]: price_selector[1],
            price_min_selector[0]: price_min_selector[1],
            price_max_selector[0]: price_max_selector[1],
            cheap_selector[0]: cheap_selector[1],
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
            user_input = _normalize_input(user_input)
            if not user_input[CONF_TARGET_ENTITY]:
                errors[CONF_TARGET_ENTITY] = "required"
            elif not _service_valid(user_input[CONF_TURN_ON_SERVICE]):
                errors[CONF_TURN_ON_SERVICE] = "invalid_service"
            elif not _service_valid(user_input[CONF_TURN_OFF_SERVICE]):
                errors[CONF_TURN_OFF_SERVICE] = "invalid_service"
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
            user_input = _normalize_input(user_input)
            if not user_input[CONF_TARGET_ENTITY]:
                errors[CONF_TARGET_ENTITY] = "required"
            elif not _service_valid(user_input[CONF_TURN_ON_SERVICE]):
                errors[CONF_TURN_ON_SERVICE] = "invalid_service"
            elif not _service_valid(user_input[CONF_TURN_OFF_SERVICE]):
                errors[CONF_TURN_OFF_SERVICE] = "invalid_service"
            else:
                return self.async_create_entry(title="", data=user_input)

        defaults = _defaults({**self.config_entry.data, **self.config_entry.options})
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(defaults),
            errors=errors,
        )
