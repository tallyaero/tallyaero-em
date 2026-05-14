"""
TallyAero EM Diagram — mobile layout.

Builds the mobile DOM tree (<768px). Companion to layouts/desktop.py.
Phase 5 collapses both into a single responsive layout.

Pure function: no callbacks, no side effects.
"""

from __future__ import annotations

from dash import dcc, html
import dash_bootstrap_components as dbc

from core import AIRPORT_OPTIONS


def mobile_layout():
    return html.Div([
        # Single Column Layout
        html.Div([
            # Phase 5d: removed the banner header (broken logo). Legal links
            # remain in the modal and the legal-links row below the chart.

            # Quick links row
            html.Div([
                html.Span("Quick Start", id="open-readme", className="quick-link link-blue", style={"cursor": "pointer"}),
                html.Span("|", className="separator"),
                html.A("Contact", href="mailto:info@tallyaero.com", className="quick-link link-blue"),
            ], className="quick-links-bar-slim"),

            # Configuration toggle bar
            html.Div([
                html.Span("Configuration"),
                html.Button("▼", id="mobile-settings-toggle", className="mobile-config-btn"),
            ], className="mobile-config-bar"),

            # Collapsible Settings Content
            dbc.Collapse([
                html.Div([
                    # Action buttons
                    html.Div([
                        dbc.Button("Edit/Create Aircraft", id="edit-aircraft-button", className="btn-sm btn-primary-orange", size="sm"),
                        dcc.Upload(id="upload-aircraft", children=dbc.Button("Load Aircraft File", className="btn-sm btn-primary-orange", size="sm"), multiple=False, accept=".json"),
                    ], className="mobile-action-btns"),

                    # Aircraft Selection
                    html.Div([
                        html.Label("Aircraft", className="input-label-sm"),
                        dcc.Dropdown(id="aircraft-select", options=[], placeholder="Select Aircraft...", className="dropdown")
                    ], className="mb-2"),

                    # Compact config section
                    html.Div([
                        html.Div([
                            html.Label("Engine", className="input-label-sm"),
                            dcc.Dropdown(id="engine-select", className="dropdown"),
                        ], className="mb-2"),
                        html.Div([
                            html.Label("Category", className="input-label-sm"),
                            dcc.Dropdown(id="category-select", className="dropdown")
                        ], className="mb-2"),
                        html.Div([
                            html.Label("Flaps", className="input-label-sm"),
                            dcc.Dropdown(id="config-select", className="dropdown")
                        ], className="mb-2"),
                        html.Div([
                            html.Label("Gear", className="input-label-sm"),
                            dcc.Dropdown(id="gear-select", className="dropdown")
                        ], id="gear-select-container", className="mb-2", style={"display": "none"}),
                        html.Div([
                            html.Label("Weight", className="input-label-sm"),
                            html.Div(id="total-weight-display", className="weight-box-sm")
                        ], className="mb-2"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Pax", className="input-label-sm"),
                                dcc.Dropdown(id="occupants-select", className="dropdown-small")
                            ], width=6),
                            dbc.Col([
                                html.Label("Pax Wt", className="input-label-sm"),
                                dcc.Input(id="passenger-weight-input", type="number", value=180, min=50, max=400, step=1, className="input-small")
                            ], width=6)
                        ], className="mb-2"),
                        html.Div([
                            html.Label("Fuel (gal)", className="input-label-sm"),
                            dcc.Slider(id="fuel-slider", min=0, max=50, step=1, value=20, marks={}, tooltip={"always_visible": True})
                        ], className="mb-2"),
                        html.Div([
                            html.Label("Power", className="input-label-sm"),
                            dcc.Slider(id="power-setting", min=0.05, max=1.0, step=0.05, value=0.50,
                                marks={0.05: "IDLE", 0.5: "50%", 1: "100%"}, tooltip={"always_visible": True})
                        ], className="mb-2"),
                        html.Div([
                            dcc.Slider(id="cg-slider", min=0, max=1, value=0.5, step=0.01)
                        ], id="cg-slider-container", className="mb-2"),
                        html.Div([
                            html.Label("FPA (deg)", className="input-label-sm"),
                            dcc.Slider(id="pitch-angle", min=-15, max=25, step=1, value=0,
                                marks={-15: "-15", 0: "0", 25: "25"}, tooltip={"always_visible": True})
                        ], className="mb-2"),
                    ], id="config-details"),

                    # Environment (compact)
                    html.Div([
                        html.Label("Airport", className="input-label-sm"),
                        dcc.Dropdown(id="airport-select", options=AIRPORT_OPTIONS, placeholder="Search...", searchable=True, clearable=True)
                    ], className="mb-2"),
                    html.Div(id="weather-panel", className="weather-panel weather-panel-mobile"),
                    html.Div([
                        html.Label("Altitude (ft)", className="input-label-sm"),
                        dcc.Slider(id="altitude-slider", min=0, max=35000, step=500, value=0, marks={}, tooltip={"always_visible": True})
                    ], className="mb-2"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("OAT °C", className="input-label-sm"),
                            dcc.Input(id="oat-input", type="number", value=15, min=-50, max=50, step=1, className="input-small", style={"width": "100%"})
                        ], width=4),
                        dbc.Col([
                            html.Label("°F", className="input-label-sm"),
                            dcc.Input(id="oat-fahrenheit-display", type="text", value="59", disabled=True, className="input-small", style={"width": "100%", "backgroundColor": "#eee"})
                        ], width=4),
                        dbc.Col([
                            html.Label("Altim", className="input-label-sm"),
                            dcc.Input(id="altimeter-input", type="number", value=29.92, min=28.0, max=31.0, step=0.01, className="input-small", style={"width": "100%"})
                        ], width=4)
                    ], className="mb-2"),
                    html.Div(id="pa-da-display", className="pa-da-box-sm", children=[
                        html.Span("PA: 0 ft | DA: 0 ft", style={"fontSize": "10px", "color": "#666"})
                    ]),

                    # Overlays (compact)
                    html.Div([
                        html.Label("Units", className="input-label-sm", style={"marginRight": "8px"}),
                        dbc.RadioItems(id="unit-select", options=[{"label": "KIAS", "value": "KIAS"}, {"label": "MPH", "value": "MPH"}],
                            value="KIAS", inline=True, className="radio-sm")
                    ], className="mb-2 d-flex align-items-center"),
                    dcc.Checklist(id="mobile-overlay-checklist",
                        options=[
                            {"label": "Ps", "value": "ps"},
                            {"label": "G Lines", "value": "g"},
                            {"label": "Radius", "value": "radius"},
                            {"label": "AoB", "value": "aob"},
                            {"label": "Neg G", "value": "negative_g"}
                        ],
                        value=["g", "radius", "aob"],
                        inline=True, className="checklist-compact mb-2"
                    ),
                    dcc.Store(id="overlay-toggle", data=["g", "radius", "aob"]),
                    html.Div([
                        dcc.Checklist(id="oei-toggle", options=[{"label": "OEI Sim", "value": "enabled"}], value=[], inline=True)
                    ], id="oei-container", className="mb-2"),
                    html.Div([
                        dcc.Checklist(id="multi-engine-toggle-options",
                            options=[{"label": "Dyn Vmc", "value": "vmca"}, {"label": "Dyn Vyse", "value": "dynamic_vyse"}],
                            value=[], inline=True)
                    ], id="multi-engine-toggles", style={"display": "none"}),
                    html.Div([
                        dcc.RadioItems(id="prop-condition",
                            options=[{"label": "Feath", "value": "feathered"}, {"label": "Stat", "value": "stationary"}, {"label": "Wmill", "value": "windmilling"}],
                            value="feathered", inline=True, className="radio-sm")
                    ], id="prop-condition-container", style={"display": "none"}),

                    # Maneuver
                    html.Div([
                        html.Label("Maneuver", className="input-label-sm"),
                        dcc.Dropdown(id="maneuver-select", options=[{"label": "Steep Turn", "value": "steep_turn"}, {"label": "Chandelle", "value": "chandelle"}], placeholder="Select...")
                    ], className="mb-2"),
                    html.Div(id="maneuver-options-container"),
                ], className="mobile-settings-content")
            ], id="mobile-settings-collapse", is_open=False),

            # Graph (always visible)
            html.Div([
                html.Div([
                    html.Button("PNG", id="png-button", className="btn-export-sm"),
                    html.Button("PDF", id="pdf-button", className="btn-export-sm"),
                    dcc.Download(id="png-download"),
                    dcc.Download(id="pdf-download"),
                ], className="export-toolbar-mobile"),
                dcc.Graph(
                    id="em-graph",
                    config={
                        "staticPlot": False,
                        "displaylogo": False,
                        "displayModeBar": False,
                        "responsive": True,
                        "scrollZoom": False,
                        "doubleClick": False,
                    },
                    figure={"layout": {
                        # Theme-aware colors are set per-render by update_graph.
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "autosize": True,
                        "hovermode": "closest",
                        "dragmode": False,
                        "xaxis": {"fixedrange": True},
                        "yaxis": {"fixedrange": True},
                    }},
                    className="dash-graph",
                    style={"height": "60vh", "width": "100%"}
                )
            ], className="mobile-graph-container"),

            # Legal footer
            html.Div([
                html.Span("Disclaimer", id="open-disclaimer", className="legal-link-sm"),
                html.Span(" | ", style={"color": "#999"}),
                html.Span("Terms", id="open-terms-policy", className="legal-link-sm"),
                html.Span(" | © 2025 TallyAero", style={"color": "#999", "fontSize": "9px"})
            ], className="mobile-legal"),

            # Hidden placeholders for desktop-only components (prevents callback errors)
            html.Div([
                # Desktop toggle switches - use hidden switches
                dbc.Switch(id="toggle-ps", value=False, style={"display": "none"}),
                dbc.Switch(id="toggle-g", value=True, style={"display": "none"}),
                dbc.Switch(id="toggle-radius", value=True, style={"display": "none"}),
                dbc.Switch(id="toggle-aob", value=True, style={"display": "none"}),
                dbc.Switch(id="toggle-negative-g", value=False, style={"display": "none"}),
                dbc.Switch(id="toggle-vmca", value=False, style={"display": "none"}),
                dbc.Switch(id="toggle-vyse", value=False, style={"display": "none"}),
                # Desktop unit buttons
                html.Button("KIAS", id="btn-kias", style={"display": "none"}),
                html.Button("MPH", id="btn-mph", style={"display": "none"}),
                # Desktop prop condition buttons
                html.Button("Feathered", id="btn-feathered", style={"display": "none"}),
                html.Button("Stationary", id="btn-stationary", style={"display": "none"}),
                html.Button("Windmilling", id="btn-windmilling", style={"display": "none"}),
                # Desktop help icons
                html.Span(id="help-fpa", style={"display": "none"}),
                html.Span(id="help-ps", style={"display": "none"}),
                html.Span(id="help-g", style={"display": "none"}),
                html.Span(id="help-radius", style={"display": "none"}),
                html.Span(id="help-aob", style={"display": "none"}),
                html.Span(id="help-negative-g", style={"display": "none"}),
                html.Span(id="help-dvmc", style={"display": "none"}),
                html.Span(id="help-dvyse", style={"display": "none"}),
                html.Span(id="help-maneuver", style={"display": "none"}),
                html.Span(id="help-ghost", style={"display": "none"}),
                # Desktop sidebar elements
                html.Button("«", id="sidebar-collapse-btn", style={"display": "none"}),
                html.Div(id="sidebar-container", className="resizable-sidebar", style={"display": "none"}),
                dbc.Accordion(id="sidebar-accordion", style={"display": "none"}),
            ], style={"display": "none"}),
        ], className="mobile-main"),
    ], className="mobile-container")
