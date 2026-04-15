"""Hilfsfunktionen fuer den Dateiexport von Kuehlgeraet Cockpit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import copy2
from typing import Any

from homeassistant.core import HomeAssistant

from .const import DOMAIN

RESOURCE_ROOT = Path(__file__).parent / "resources"
EXPORT_FOLDER = DOMAIN


@dataclass(frozen=True)
class InstallItem:
    """Beschreibt eine einzelne Datei fuer den Export nach Home Assistant."""

    key: str
    source: Path
    target: Path
    description: str


def _build_install_plan(
    hass: HomeAssistant,
    *,
    install_blueprint: bool,
    export_dashboard_snippets: bool,
) -> list[InstallItem]:
    config_root = Path(hass.config.path())
    items: list[InstallItem] = [
        InstallItem(
            key="readme",
            source=RESOURCE_ROOT / "README.txt",
            target=config_root / EXPORT_FOLDER / "README.txt",
            description="Installationshinweise",
        )
    ]

    if install_blueprint:
        items.append(
            InstallItem(
                key="blueprint",
                source=(
                    RESOURCE_ROOT
                    / "blueprints"
                    / "automation"
                    / DOMAIN
                    / "kuehlgeraet_tibber_shelly_kurzfristtrend.yaml"
                ),
                target=(
                    config_root
                    / "blueprints"
                    / "automation"
                    / DOMAIN
                    / "kuehlgeraet_tibber_shelly_kurzfristtrend.yaml"
                ),
                description="Kuehlgeraet-Automations-Blueprint",
            )
        )

    if export_dashboard_snippets:
        dashboard_root = config_root / EXPORT_FOLDER / "dashboard"
        items.extend(
            [
                InstallItem(
                    key="dashboard_markdown",
                    source=RESOURCE_ROOT / "dashboards" / "kuehlgeraet_status_sensor.yaml",
                    target=dashboard_root / "kuehlgeraet_status_sensor.yaml",
                    description="Dashboard-Statuskarte",
                ),
                InstallItem(
                    key="dashboard_cockpit",
                    source=(
                        RESOURCE_ROOT
                        / "dashboards"
                        / "kuehlgeraet_cockpit_visual_button_card_sensor.yaml"
                    ),
                    target=dashboard_root / "kuehlgeraet_cockpit_visual_button_card_sensor.yaml",
                    description="Visuelle Cockpit-Karte",
                ),
                InstallItem(
                    key="dashboard_panel",
                    source=RESOURCE_ROOT / "dashboards" / "kuehlgeraet_technikpanel_sensor.yaml",
                    target=dashboard_root / "kuehlgeraet_technikpanel_sensor.yaml",
                    description="Technikpanel",
                ),
            ]
        )

    return items


def _copy_plan(plan: list[InstallItem], overwrite_existing: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for item in plan:
        item.target.parent.mkdir(parents=True, exist_ok=True)

        if item.target.exists() and not overwrite_existing:
            results.append(
                {
                    "key": item.key,
                    "description": item.description,
                    "status": "skipped",
                    "target": str(item.target),
                }
            )
            continue

        status = "updated" if item.target.exists() else "created"
        copy2(item.source, item.target)
        results.append(
            {
                "key": item.key,
                "description": item.description,
                "status": status,
                "target": str(item.target),
            }
        )

    return results


async def async_install_resources(
    hass: HomeAssistant,
    *,
    install_blueprint: bool,
    export_dashboard_snippets: bool,
    overwrite_existing: bool,
) -> list[dict[str, Any]]:
    """Kopiert mitgelieferte Ressourcen in das Konfigurationsverzeichnis von Home Assistant."""
    plan = _build_install_plan(
        hass,
        install_blueprint=install_blueprint,
        export_dashboard_snippets=export_dashboard_snippets,
    )
    return await hass.async_add_executor_job(_copy_plan, plan, overwrite_existing)