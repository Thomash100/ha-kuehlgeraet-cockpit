const STATUS_ENTITY = "sensor.kuehlgeraet_cockpit_status";
const ENGINE_SWITCH = "switch.kuehlgeraet_cockpit_regel_engine";
const SIMULATION_SWITCH = "switch.kuehlgeraet_cockpit_simulation";

class KuehlgeraetCockpitPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._busy = false;
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  set panel(panel) {
    this._panel = panel;
  }

  connectedCallback() {
    this._render();
  }

  _state(entityId, friendlyNames) {
    if (!this._hass) {
      return undefined;
    }
    if (entityId && this._hass.states[entityId]) {
      return this._hass.states[entityId];
    }
    if (!friendlyNames) {
      return undefined;
    }
    const names = Array.isArray(friendlyNames) ? friendlyNames : [friendlyNames];
    return Object.values(this._hass.states).find(
      (state) => names.includes(state.attributes?.friendly_name),
    );
  }

  _status() {
    return this._state(STATUS_ENTITY, [
      "Kuehlgeraet Cockpit Regelentscheidung Status",
      "Kuehlgeraet Cockpit Status",
    ]);
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _format(value, suffix = "", digits = 1) {
    if (value === null || value === undefined || value === "") {
      return "--";
    }
    const number = Number(value);
    if (Number.isFinite(number)) {
      return `${number.toFixed(digits)}${suffix}`;
    }
    return `${this._escape(value)}${suffix}`;
  }

  _list(value) {
    if (Array.isArray(value)) {
      return value.join(", ");
    }
    return value || "";
  }

  _metric(icon, label, value, sub = "") {
    return `
      <section class="metric">
        <ha-icon icon="${icon}"></ha-icon>
        <span>${this._escape(label)}</span>
        <strong>${value}</strong>
        <small>${this._escape(sub)}</small>
      </section>
    `;
  }

  _row(label, value, icon = "mdi:circle-small") {
    const display = value === null || value === undefined || value === "" ? "--" : value;
    return `
      <div class="row">
        <ha-icon icon="${icon}"></ha-icon>
        <span>${this._escape(label)}</span>
        <strong>${this._escape(display)}</strong>
      </div>
    `;
  }

  async _action(action) {
    if (!this._hass || this._busy) {
      return;
    }
    this._busy = true;
    this._render();

    try {
      if (action === "evaluate") {
        await this._hass.callService("kuehlgeraet_cockpit", "evaluate_now", {
          apply: true,
        });
      }
      if (action === "toggle-engine") {
        const entity = this._state(ENGINE_SWITCH, [
          "Kuehlgeraet Cockpit Steuerung Regel-Engine aktiv",
          "Kuehlgeraet Cockpit Regel-Engine",
        ]);
        if (entity) {
          await this._hass.callService("homeassistant", "toggle", {
            entity_id: entity.entity_id,
          });
        }
      }
      if (action === "toggle-simulation") {
        const entity = this._state(SIMULATION_SWITCH, [
          "Kuehlgeraet Cockpit Steuerung Simulationsmodus aktiv",
          "Kuehlgeraet Cockpit Simulation",
        ]);
        if (entity) {
          await this._hass.callService("homeassistant", "toggle", {
            entity_id: entity.entity_id,
          });
        }
      }
    } finally {
      this._busy = false;
      this._render();
    }
  }

  _bind() {
    this.shadowRoot.querySelectorAll("button[data-action]").forEach((button) => {
      button.addEventListener("click", () => this._action(button.dataset.action));
    });
  }

  _render() {
    if (!this.shadowRoot) {
      return;
    }

    const status = this._status();
    const attrs = status?.attributes ?? {};
    const engine = this._state(ENGINE_SWITCH, [
      "Kuehlgeraet Cockpit Steuerung Regel-Engine aktiv",
      "Kuehlgeraet Cockpit Regel-Engine",
    ]);
    const simulation = this._state(SIMULATION_SWITCH, [
      "Kuehlgeraet Cockpit Steuerung Simulationsmodus aktiv",
      "Kuehlgeraet Cockpit Simulation",
    ]);
    const mode = status?.state || attrs.mode || "Bereit";
    const priceFactor = attrs.price_factor !== undefined
      ? `${Math.round(Number(attrs.price_factor) * 100)}%`
      : "--";
    const engineOn = engine?.state === "on";
    const simulationOn = simulation?.state === "on";

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          color: var(--primary-text-color, #1d1f23);
          display: block;
          min-height: 100vh;
          background:
            linear-gradient(180deg, rgba(245, 248, 250, 0.96), rgba(235, 239, 242, 0.96));
          font-family: var(--primary-font-family, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
        }
        * { box-sizing: border-box; }
        .shell {
          width: min(1180px, calc(100vw - 32px));
          margin: 0 auto;
          padding: 28px 0 36px;
        }
        header {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 18px;
          align-items: center;
          margin-bottom: 22px;
        }
        h1 {
          margin: 0;
          font-size: 38px;
          font-weight: 760;
          letter-spacing: 0;
        }
        .subline {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 8px;
          color: var(--secondary-text-color, #5b636a);
          font-size: 14px;
        }
        .badge {
          align-items: center;
          background: #f2f7f5;
          border: 1px solid #bad7ca;
          border-radius: 999px;
          color: #164b36;
          display: inline-flex;
          gap: 6px;
          min-height: 32px;
          padding: 0 12px;
          white-space: nowrap;
        }
        .toolbar {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          justify-content: flex-end;
        }
        button {
          align-items: center;
          border: 1px solid #c6ced6;
          border-radius: 8px;
          background: #ffffff;
          color: #17202a;
          cursor: pointer;
          display: inline-flex;
          font: inherit;
          font-weight: 650;
          gap: 8px;
          min-height: 42px;
          padding: 0 14px;
          transition: background 120ms ease, border-color 120ms ease, transform 120ms ease;
        }
        button:hover { background: #eef4f2; border-color: #8fb8a5; }
        button:active { transform: translateY(1px); }
        button[disabled] { cursor: default; opacity: 0.52; }
        .primary {
          background: #123c69;
          border-color: #123c69;
          color: #ffffff;
        }
        .primary:hover { background: #174d86; border-color: #174d86; }
        .active {
          border-color: #478565;
          background: #e8f4ec;
        }
        .danger {
          border-color: #c68b3d;
          background: #fff5e6;
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(6, minmax(120px, 1fr));
          gap: 12px;
        }
        .metric {
          background: #ffffff;
          border: 1px solid #d9e1e7;
          border-radius: 8px;
          display: grid;
          gap: 8px;
          min-height: 136px;
          padding: 16px;
        }
        .metric ha-icon { color: #526d82; }
        .metric span {
          color: #5d6870;
          font-size: 13px;
          line-height: 1.25;
        }
        .metric strong {
          align-self: end;
          font-size: 27px;
          font-weight: 760;
          line-height: 1;
        }
        .metric small {
          color: #77818a;
          min-height: 18px;
        }
        .band {
          background: #ffffff;
          border: 1px solid #d9e1e7;
          border-radius: 8px;
          margin-top: 12px;
          padding: 18px;
        }
        .decision {
          display: grid;
          grid-template-columns: minmax(0, 1fr) minmax(260px, 0.52fr);
          gap: 18px;
        }
        h2 {
          font-size: 17px;
          letter-spacing: 0;
          margin: 0 0 10px;
        }
        .reason {
          color: #3e4850;
          line-height: 1.45;
          margin: 0;
        }
        .rows {
          display: grid;
          gap: 8px;
        }
        .row {
          align-items: center;
          border-top: 1px solid #edf1f3;
          display: grid;
          gap: 10px;
          grid-template-columns: 24px minmax(0, 1fr) minmax(90px, auto);
          min-height: 38px;
        }
        .row:first-child { border-top: 0; }
        .row span {
          color: #5d6870;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .row strong {
          font-size: 13px;
          overflow: hidden;
          text-align: right;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .sources {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 12px;
        }
        @media (max-width: 980px) {
          .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
          .decision { grid-template-columns: 1fr; }
        }
        @media (max-width: 680px) {
          .shell { width: min(100vw - 20px, 1180px); padding-top: 18px; }
          header { grid-template-columns: 1fr; }
          .toolbar { justify-content: stretch; }
          button { flex: 1 1 100%; justify-content: center; }
          .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .sources { grid-template-columns: 1fr; }
          .metric { min-height: 126px; padding: 14px; }
          .metric strong { font-size: 23px; }
          h1 { font-size: 28px; }
        }
      </style>
      <main class="shell">
        <header>
          <div>
            <h1>Kuehlgeraet Cockpit</h1>
            <div class="subline">
              <span class="badge"><ha-icon icon="mdi:state-machine"></ha-icon>${this._escape(mode)}</span>
              <span>${this._escape(this._list(attrs.target_entities) || attrs.target_entity || "kein Ziel")}</span>
              <span>${this._escape(attrs.updated_at || "")}</span>
            </div>
          </div>
          <div class="toolbar">
            <button class="primary" data-action="evaluate" ${this._busy ? "disabled" : ""}>
              <ha-icon icon="mdi:play-circle-outline"></ha-icon>
              <span>${this._busy ? "Pruefe..." : "Jetzt auswerten"}</span>
            </button>
            <button class="${engineOn ? "active" : ""}" data-action="toggle-engine" ${engine ? "" : "disabled"}>
              <ha-icon icon="mdi:power-cycle"></ha-icon>
              <span>${engineOn ? "Engine an" : "Engine aus"}</span>
            </button>
            <button class="${simulationOn ? "danger" : ""}" data-action="toggle-simulation" ${simulation ? "" : "disabled"}>
              <ha-icon icon="mdi:flask-outline"></ha-icon>
              <span>${simulationOn ? "Simulation" : "Live"}</span>
            </button>
          </div>
        </header>

        <section class="grid">
          ${this._metric("mdi:thermometer", "Temperatur", this._format(attrs.temperature_c, " C"), "Istwert")}
          ${this._metric("mdi:flash", "Leistung", this._format(attrs.power_w, " W", 0), "Kompressor")}
          ${this._metric("mdi:currency-eur", "Preis", this._format(attrs.price, "", 3), attrs.price_source || "Preisquelle")}
          ${this._metric("mdi:chart-bell-curve", "Preisfaktor", priceFactor, attrs.price_data_valid ? "aktiv" : "Fallback")}
          ${this._metric("mdi:thermometer-plus", "Ein ab", this._format(attrs.selected_on_temp, " C"), "preisabhaengig")}
          ${this._metric("mdi:thermometer-minus", "Aus bei", this._format(attrs.selected_off_temp, " C"), "preisabhaengig")}
        </section>

        <section class="band decision">
          <div>
            <h2>${this._escape(attrs.planned_action || "Keine Aktion")}</h2>
            <p class="reason">${this._escape(attrs.reason || "Noch keine Bewertung vorhanden.")}</p>
          </div>
          <div class="rows">
            ${this._row("Primaeres Ziel", attrs.target_entity, "mdi:toggle-switch-outline")}
            ${this._row("Zielzustand", attrs.target_state, "mdi:toggle-switch-outline")}
            ${this._row("Letzte Aktion", attrs.applied_action, "mdi:send-check-outline")}
            ${this._row("Blockiert durch", attrs.apply_blocked_by, "mdi:shield-alert-outline")}
          </div>
        </section>

        <section class="band sources">
          <div class="rows">
            ${this._row("Temperatur", attrs.temperature_entity, "mdi:thermometer")}
            ${this._row("Leistung", attrs.power_entity, "mdi:flash")}
            ${this._row("Strompreis", attrs.price_entity, "mdi:currency-eur")}
            ${this._row("Einschalt-Dienst", attrs.turn_on_service, "mdi:play")}
            ${this._row("Einschalt-Aktionen", this._list(attrs.turn_on_action_entities), "mdi:script-text-play-outline")}
            ${this._row("Einschalt-Sequenz", attrs.turn_on_actions_count, "mdi:playlist-play")}
          </div>
          <div class="rows">
            ${this._row("Preis Minimum", attrs.price_min_entity, "mdi:arrow-down-bold")}
            ${this._row("Preis Maximum", attrs.price_max_entity, "mdi:arrow-up-bold")}
            ${this._row("Guenstig-Sensor", attrs.cheap_entity, "mdi:cash-check")}
            ${this._row("Ausschalt-Dienst", attrs.turn_off_service, "mdi:stop")}
            ${this._row("Ausschalt-Aktionen", this._list(attrs.turn_off_action_entities), "mdi:script-text-outline")}
            ${this._row("Ausschalt-Sequenz", attrs.turn_off_actions_count, "mdi:playlist-remove")}
          </div>
        </section>
      </main>
    `;
    this._bind();
  }
}

customElements.define("kuehlgeraet-cockpit-panel", KuehlgeraetCockpitPanel);
