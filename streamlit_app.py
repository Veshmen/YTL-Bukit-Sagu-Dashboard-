"""YTL Bukit Sagu | USM EKC 503 interactive CO2 decision-support dashboard.

Streamlit Community Cloud entrypoint: streamlit_app.py
Core calculation module: model.py (adapted from the team's Week 5-7 models).
This dashboard is an educational scenario model, not a validated plant investment study.
"""
from dataclasses import replace
from html import escape
from pathlib import Path
import base64

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from model import Inputs, TECH, compare, dashboard_summary, right_sized_fraction

st.set_page_config(
    page_title="YTL Bukit Sagu | CCUS Decision Support",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
:root { --ink:#0c2637; --teal:#078f88; --muted:#577080; --border:#dbe7e9; }
html,body,[class*="css"],[data-testid="stAppViewContainer"] { font-family:'DM Sans',system-ui,sans-serif; }
[data-testid="stAppViewContainer"] { background:linear-gradient(180deg,#f6fafb 0%,#f8fbfc 100%); color:var(--ink); }
[data-testid="stHeader"] { background:transparent; height:2.25rem; }
#MainMenu,footer { visibility:hidden; }
[data-testid="stMainBlockContainer"] { max-width:1450px; padding:0.4rem 1.9rem 2rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#eaf7f5,#f1f8fa 70%,#eef6f7); border-right:1px solid #d4e7e7; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding:1.25rem 1.1rem 1.7rem; }
[data-testid="stSidebar"] label { color:#15374a; font-size:.9rem; font-weight:680; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#324f5d; }
.stSlider [data-baseweb="slider"] [role="slider"] { background:#fff !important; border:2px solid #078f88 !important; }
.stSelectbox [data-baseweb="select"]>div { border-color:#cfdee3; border-radius:10px; }
.stApp a { color:#007f79; }
h1,h2,h3,h4 { color:var(--ink); }
.brand { display:flex; align-items:center; gap:11px; margin:4px 0 25px; }
.logo-chip { background:#f4eefe; border:1px solid #dfd2f1; color:#692a8a; padding:9px 10px; font-size:22px; font-weight:800; border-radius:9px; letter-spacing:-1.5px; }
.brand-words { color:#5b3075; font-size:11px; line-height:1.35; text-transform:uppercase; font-weight:800; letter-spacing:.6px; }
.sidebar-title { color:#0f3e4d; font-size:19px; font-weight:800; margin:0 0 14px; }
.hero { position:relative; height:267px; border-radius:17px; border:1px solid #c9d9df; background-position:center 48%; background-size:cover; overflow:hidden; margin-bottom:20px; box-shadow:0 10px 24px rgba(11,38,55,.13); }
.hero-overlay { position:absolute; inset:0; background:linear-gradient(90deg,rgba(8,24,36,.84),rgba(8,24,36,.41) 51%,rgba(8,24,36,.10)); }
.hero-content { position:absolute; inset:auto 24px 27px 30px; color:#fff; text-shadow:0 2px 12px #0009; max-width:800px; }
.hero-kicker { font-size:11px; font-weight:700; letter-spacing:1.7px; text-transform:uppercase; color:#8de3d3; margin-bottom:8px; }
.hero h1 { font-size:clamp(24px,2.45vw,35px); letter-spacing:-.9px; line-height:1.15; color:#fff; margin:0 0 8px; font-weight:800; }
.hero-subtitle { color:#e5eff3; font-size:13px; font-weight:600; }
.section-title { color:#153345; font-size:17px; font-weight:800; margin:8px 0 15px; }
.kpi { height:136px; display:flex; flex-direction:column; justify-content:space-between; padding:18px 19px 16px; border:1px solid rgba(95,145,155,.10); border-radius:15px; box-shadow:0 5px 17px rgba(25,67,78,.035); margin-bottom:8px; }
.kpi.teal { background:linear-gradient(125deg,#e3f5f2,#d7eeec); }
.kpi.blue { background:linear-gradient(125deg,#eaf7fd,#dceefa); }
.kpi.green { background:linear-gradient(125deg,#edf7ed,#def1e5); }
.kpi.orange { background:linear-gradient(125deg,#fff4e6,#faead9); }
.kpi.purple { background:linear-gradient(125deg,#f4efff,#ebe7f8); }
.kpi.slate { background:linear-gradient(125deg,#eff6f9,#e6f1f5); }
.kpi-top { display:flex; align-items:center; gap:9px; font-size:13px; color:#274758; font-weight:750; line-height:1.35; }
.kpi-icon { font-size:22px; line-height:1; }
.kpi-value { color:#10364b; font-size:clamp(22px,2.1vw,32px); font-weight:800; line-height:1.1; letter-spacing:-.9px; white-space:nowrap; }
.kpi-value.positive { color:#146b35; }
.kpi-value.negative { color:#b53c37; }
.kpi-unit { font-size:11px; font-weight:700; color:#68818e; margin-top:1px; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { background:#eaf2f5; border-radius:12px 12px 0 0; gap:4px; padding:5px 6px 0; }
[data-testid="stTabs"] [data-baseweb="tab"] { font-size:13px; font-weight:750; padding:11px 14px; border-radius:9px 9px 0 0; color:#375463; }
[data-testid="stTabs"] [aria-selected="true"] { background:#068a82; color:#fff; }
[data-testid="stTabs"] [data-baseweb="tab-highlight"],[data-testid="stTabs"] [data-baseweb="tab-border"] { display:none; }
.styled-table { overflow:auto; border:1px solid #c7ddde; border-radius:11px; margin-top:6px; background:white; }
.styled-table table { border-collapse:collapse; width:100%; white-space:nowrap; font-size:13px; color:#163243; }
.styled-table th { background:#077f77; color:#fff; text-align:left; padding:13px 12px; font-weight:750; }
.styled-table th:not(:first-child),.styled-table td:not(:first-child) { text-align:right; }
.styled-table td { padding:11px 12px; border-top:1px solid #d9e8e9; }
.styled-table tr:nth-child(even) { background:#f2faf9; }
.styled-table tr.selected { background:#d7f2ee; font-weight:800; }
.good { color:#16803f; font-weight:800; }
.bad { color:#c13b3b; font-weight:800; }
.chart-title { margin:24px 0 7px; color:#173b4c; font-weight:800; font-size:17px; }
.balance-card { background:#fff; border:1px solid #d9e6e9; padding:17px 19px; border-radius:13px; margin:4px 0 14px; }
.balance-title { color:#1e495b; font-size:15px; font-weight:800; margin-bottom:10px; }
.balance-line { display:flex; justify-content:space-between; gap:12px; border-bottom:1px solid #e7eff0; padding:9px 0; font-size:13px; color:#44616d; }
.balance-line:last-child { border-bottom:none; }
.balance-line strong { color:#18394d; }
.small-note { color:#6c8390; font-size:12px; line-height:1.6; }
.footer-note { color:#758e97; font-size:11px; text-align:right; margin-top:24px; }
@media(max-width:1000px) { [data-testid="stMainBlockContainer"] {padding-left:1rem;padding-right:1rem;} .hero{height:215px;} .hero h1{font-size:24px;} .kpi{height:118px;padding:14px;} .kpi-value{font-size:23px;} }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --- Only the five user-requested controls. ---
if 'capture_technology' not in st.session_state:
    st.session_state.capture_technology = 'Solid adsorption'
if 'capture_efficiency_pct' not in st.session_state:
    st.session_state.capture_efficiency_pct = 85

def reset_efficiency_on_technology_change():
    st.session_state.capture_efficiency_pct = round(
        100.0 * TECH[st.session_state.capture_technology]['eta']
    )

with st.sidebar:
    st.markdown('<div class="brand"><span class="logo-chip">USM</span><span class="brand-words">Universiti Sains Malaysia<br>EKC 503 · Group 2</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">⚙ &nbsp; Change assumptions</div>', unsafe_allow_html=True)
    selected_technology = st.selectbox(
        'Capture technology', ['MEA absorption', 'Solid adsorption'],
        key='capture_technology', on_change=reset_efficiency_on_technology_change,
    )
    selected_efficiency = st.slider('Capture efficiency (%)', 65, 95,
                                    key='capture_efficiency_pct', step=1)
    carbon_price = st.slider('Carbon price (USD/net tCO₂e)', 0, 100, 25, 5,
                             help='Illustrative economic assumption; not guaranteed carbon-credit revenue.')
    aggregate_price = st.slider('Aggregate sale price (USD/t)', 0, 50, 26, 1)
    utility_multiplier = st.slider('Utility price multiplier', 0.5, 2.0, 1.0, 0.05)

x = replace(
    Inputs(),
    carbon_price_usd_per_net_t=float(carbon_price),
    aggregate_price_usd_per_t=float(aggregate_price),
    utility_price_multiplier=float(utility_multiplier),
    capture_efficiency_override=float(selected_efficiency)/100.0,
)

BANNER = Path(__file__).resolve().parent / 'title_banner.jpg'
if BANNER.is_file():
    banner_b64 = base64.b64encode(BANNER.read_bytes()).decode('ascii')
    st.markdown(
        '<div class="hero" style="background-image:url(data:image/jpeg;base64,' + banner_b64 + ')">'
        '<div class="hero-overlay"></div><div class="hero-content">'
        '<div class="hero-kicker">USM EKC 503 · Group 2</div>'
        '<h1>YTL Bukit Sagu | Decarbonization Decision-Support Tool</h1>'
        '<div class="hero-subtitle">CO₂ capture · Ready-mix injection · Steel-slag mineralization</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
else:
    st.title('YTL Bukit Sagu | Decarbonization Decision-Support Tool')

try:
    summary = dashboard_summary(x, selected_technology)
    selected = summary['integrated']
    ready = summary['injection']
    slag = summary['slag']
    alternatives = compare(x)
except ValueError as exc:
    st.error(f'This scenario cannot be calculated: {exc}')
    st.stop()


def money(value: float) -> str:
    return f"{'+' if value >= 0 else '−'}${abs(value) / 1e6:,.2f}m"


def card(color: str, symbol: str, heading: str, value: str, unit: str = '', financial: float = None) -> str:
    value_class = '' if financial is None else ('positive' if financial >= 0 else 'negative')
    return (f'<div class="kpi {color}"><div class="kpi-top"><span class="kpi-icon">{symbol}</span>'
            f'<span>{escape(heading)}</span></div>'
            f'<div><div class="kpi-value {value_class}">{escape(value)}</div>'
            f'<div class="kpi-unit">{escape(unit)}</div></div></div>')

st.markdown('<div class="section-title">CO₂ utilization & integrated project KPIs</div>', unsafe_allow_html=True)
for row in [
    [
        ('teal', '◈', 'NPV · CO₂ injection', money(ready['npv_usd']), '25-year incremental ready-mix project', ready['npv_usd']),
        ('blue', '◉', 'NPV · Slag mineralization', money(slag['npv_usd']), '25-year stand-alone slag + capture', slag['npv_usd']),
        ('green', '▥', 'NPV · Integrated project', money(selected['npv_usd']), '25-year capture + both utilization paths', selected['npv_usd']),
    ],
    [
        ('orange', '♧', 'CO₂ injected into concrete', f"{selected['injected_t']:,.1f} t", 'per year · injected amount', None),
        ('purple', '◇', 'CO₂ mineralized in slag', f"{selected['slag_fixed_t']:,.0f} t", 'per year · retained in slag', None),
        ('slate', '✦', 'Integrated net CO₂e avoided', f"{selected['net_avoided_t']:,.0f} t", 'CO₂e per year · includes energy and logistics', None),
    ],
]:
    columns = st.columns(3, gap='small')
    for c, args in zip(columns, row):
        with c:
            st.markdown(card(*args), unsafe_allow_html=True)


def choice_table(rows, selected_case):
    th = ('<div class="styled-table"><table><thead><tr><th>Capture technology</th>'
          '<th>System size</th><th>Flue gas treated</th><th>Captured CO₂ (t/y)</th>'
          '<th>Net avoided (tCO₂e/y)</th><th>Integrated NPV</th></tr></thead><tbody>')
    body = []
    for r in rows:
        is_selected = (r['technology'] == selected_case['technology'] and
                       abs(r['treated_fraction']-selected_case['treated_fraction']) < 1e-6)
        klass = ' class="selected"' if is_selected else ''
        design = 'Full-size' if r['treated_fraction'] > .999999 else 'Right-sized'
        npv_class = 'good' if r['npv_usd'] >= 0 else 'bad'
        body.append(
            f'<tr{klass}><td>{escape(r["technology"])}</td><td>{design}</td>'
            f'<td>{100*r["treated_fraction"]:.1f}%</td><td>{r["captured_t"]:,.0f}</td>'
            f'<td>{r["net_avoided_t"]:,.0f}</td>'
            f'<td class="{npv_class}">{money(r["npv_usd"])}</td></tr>'
        )
    return th + ''.join(body) + '</tbody></table></div>'


def line_chart(grid, npv_m, x_title, marker_x=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grid, y=npv_m, mode='lines+markers',
                             line=dict(color='#008c84', width=3.2),
                             marker=dict(color='#078f88', size=7),
                             fill='tozeroy', fillcolor='rgba(6,147,137,.09)',
                             hovertemplate='%{x}<br>NPV: $%{y:,.2f}m<extra></extra>'))
    fig.add_hline(y=0, line_color='#97aeb5', line_width=1)
    if marker_x is not None:
        fig.add_vline(x=marker_x, line_color='#71b8b1', line_dash='dot')
    fig.update_layout(height=335, margin=dict(l=8,r=8,t=16,b=6),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#ffffff',
                      showlegend=False, font=dict(family='DM Sans',color='#365564',size=12),
                      xaxis=dict(title=x_title, gridcolor='#e6eff1', zeroline=False),
                      yaxis=dict(title='25-year integrated NPV (USD million)',gridcolor='#e6eff1',zeroline=False))
    return fig


def balance_card(title, fields):
    lines = ''.join(f'<div class="balance-line"><span>{escape(label)}</span><strong>{escape(value)}</strong></div>'
                    for label,value in fields)
    return f'<div class="balance-card"><div class="balance-title">{escape(title)}</div>{lines}</div>'


def sensitivity_scenario(input_data):
    return dashboard_summary(input_data, selected_technology)['integrated']

tab_compare, tab_balance, tab_sensitivity = st.tabs([
    '▦  Capture technology comparison',
    '▥  Carbon & financial balance',
    '⌁  Sensitivity analysis',
])

with tab_compare:
    st.markdown(choice_table(alternatives, selected), unsafe_allow_html=True)
    st.caption(f'Highlighted: selected {selected_technology.lower()} at {selected_efficiency}% capture efficiency; right-sized flue-gas treatment = {selected["treated_fraction"]*100:.2f}%. All comparison rows use the selected efficiency.')
    st.markdown('<div class="chart-title">Integrated project NPV sensitivity to carbon price</div>',unsafe_allow_html=True)
    carbon_grid = list(range(0,101,5))
    carbon_npv = [sensitivity_scenario(replace(x,carbon_price_usd_per_net_t=float(p)))['npv_usd']/1e6
                  for p in carbon_grid]
    st.plotly_chart(line_chart(carbon_grid,carbon_npv,'Carbon price (USD/net tCO₂e)',carbon_price),
                    use_container_width=True,config={'displayModeBar':False})

with tab_balance:
    col1,col2 = st.columns(2, gap='medium')
    with col1:
        st.markdown(balance_card('Integrated annual carbon balance', [
            ('Baseline direct CO₂', f'{x.baseline_tco2:,.0f} t/y'),
            ('Flue gas treated', f'{selected["treated_fraction"]*100:.2f}%'),
            ('Captured CO₂', f'{selected["captured_t"]:,.0f} t/y'),
            ('CO₂ injected into concrete', f'{selected["injected_t"]:,.1f} t/y'),
            ('Concrete CO₂ permanently fixed', f'{selected["ready_fixed_t"]:,.1f} t/y'),
            ('Slag CO₂ permanently mineralized', f'{selected["slag_fixed_t"]:,.0f} t/y'),
            ('Avoided cement emissions', f'{selected["avoided_cement_t"]:,.0f} tCO₂e/y'),
            ('Capture heat emissions', f'{selected["emissions_heat_t"]:,.0f} tCO₂e/y'),
            ('Power emissions', f'{selected["emissions_electric_t"]:,.0f} tCO₂e/y'),
            ('Slag transport emissions', f'{selected["emissions_logistics_t"]:,.0f} tCO₂e/y'),
            ('Net CO₂e avoided', f'{selected["net_avoided_t"]:,.0f} t/y'),
        ]), unsafe_allow_html=True)
    with col2:
        st.markdown(balance_card('Financial summary', [
            ('CO₂ injection NPV',money(ready['npv_usd'])),
            ('Slag mineralization NPV',money(slag['npv_usd'])),
            ('Integrated project NPV',money(selected['npv_usd'])),
            ('Integrated installed CAPEX',money(selected['capex_usd'])),
            ('Annual operating expenses',f'${selected["annual_opex_usd"]/1e6:,.2f}m/y'),
            ('Aggregate sales',f'${selected["aggregate_revenue_usd"]/1e6:,.2f}m/y'),
            ('Avoided cement purchase value',f'${selected["cement_savings_usd"]:,.0f}/y'),
            ('Scenario carbon benefit',f'${selected["carbon_scenario_revenue_usd"]/1e6:,.2f}m/y'),
            ('Net annual cash flow',f'${selected["annual_net_usd"]/1e6:,.2f}m/y'),
            ('Levelized capture cost',f'${selected["lcoc_usd_per_captured_t"]:,.2f}/t captured'),
        ]), unsafe_allow_html=True)
    with st.expander('How the three NPV figures are calculated'):
        st.markdown(
            '**CO₂ injection NPV** follows the Week 6 ready-mix module: 25-year incremental investment '
            'in injection equipment, with only its allocated captured CO₂ charged at LCOC. '
            '**Slag mineralization NPV** models a right-sized capture-and-slag installation '
            'without ready-mix. **Integrated NPV** includes the capture unit and both utilization '
            'routes. **Do not add the three NPVs together** because their investment boundaries differ. '
            'These are estimated financial scenarios, not independently verified plant returns.'
        )

with tab_sensitivity:
    st.markdown('### Integrated project sensitivity')
    st.caption('Each point recalculates the right-sized design for the currently selected capture technology.')
    variable = st.selectbox('Select variable to test', [
        'Carbon price', 'Utility price multiplier', 'Capture efficiency', 'Aggregate sale price',
    ])
    if variable == 'Carbon price':
        grid = [float(i) for i in range(0,101,5)]
        sims = [replace(x,carbon_price_usd_per_net_t=value) for value in grid]
        xlabel='Carbon price (USD/net tCO₂e)'; current=float(carbon_price)
    elif variable == 'Utility price multiplier':
        grid = [round(.5+i*.1,2) for i in range(16)]
        sims = [replace(x,utility_price_multiplier=value) for value in grid]
        xlabel='Utility price multiplier'; current=float(utility_multiplier)
    elif variable == 'Capture efficiency':
        grid = list(range(65,96,5))
        sims = [replace(x,capture_efficiency_override=value/100) for value in grid]
        xlabel='Capture efficiency (%)'; current=float(selected_efficiency)
    else:
        grid = [float(i) for i in range(0,51,5)]
        sims = [replace(x,aggregate_price_usd_per_t=value) for value in grid]
        xlabel='Aggregate sale price (USD/t)'; current=float(aggregate_price)
    scenario_rows=[sensitivity_scenario(xx) for xx in sims]
    st.plotly_chart(line_chart(grid,[r['npv_usd']/1e6 for r in scenario_rows],xlabel,current),
                    use_container_width=True,config={'displayModeBar':False})
    with st.expander('View sensitivity table'):
        st.dataframe(pd.DataFrame({
            xlabel: grid,
            'Integrated NPV (USD million)': [round(r['npv_usd']/1e6,3) for r in scenario_rows],
            'Net CO₂e avoided (t/year)': [round(r['net_avoided_t']) for r in scenario_rows],
            'Flue gas treated (%)': [round(r['treated_fraction']*100,2) for r in scenario_rows],
        }),hide_index=True,use_container_width=True)

    export_data = pd.DataFrame([{
        'Capture technology':selected_technology,
        'Capture efficiency (%)':selected_efficiency,
        'Carbon price (USD/t)':carbon_price,
        'Aggregate sale price (USD/t)':aggregate_price,
        'Utility price multiplier':utility_multiplier,
        'CO2 injection NPV (USD)':ready['npv_usd'],
        'Slag mineralization NPV (USD)':slag['npv_usd'],
        'Integrated NPV (USD)':selected['npv_usd'],
        'CO2 injected into concrete (t/y)':selected['injected_t'],
        'CO2 mineralized in slag (t/y)':selected['slag_fixed_t'],
        'Integrated net CO2e avoided (t/y)':selected['net_avoided_t'],
    }])
    st.download_button('Download the current scenario (CSV)',
                       data=export_data.to_csv(index=False).encode('utf-8'),
                       file_name='YTL_Bukit_Sagu_Scenario.csv',mime='text/csv')

st.markdown('<div class="footer-note">USM EKC 503 · Group 2 | YTL Bukit Sagu decision-support model</div>', unsafe_allow_html=True)
