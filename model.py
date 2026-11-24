"""EKC 503 | Transparent, educational CCS + concrete/steel-slag scenario model.

Source defaults: supplied Week 5, Week 6 and Week 7 workbooks.
This is a screening-level model with illustrative values, NOT a verified plant design.
Right-sizing and sensitivity calculations recompute mass and energy flows.
"""
from dataclasses import dataclass, replace
from typing import Optional

@dataclass(frozen=True)
class Inputs:
    # Project baseline and process parameters from submitted workbooks
    baseline_tco2: float = 191966.8976225
    life_years: int = 25
    discount_rate: float = 0.08
    capex_exponent: float = 0.60
    grid_factor_t_per_mwh: float = 0.74
    heat_factor_t_per_gj: float = 0.0561
    capture_heat_price_usd_per_gj: float = 4.144
    capture_electric_price_usd_per_mwh: float = 64.96

    # Ready-mix pathway: the values below are conditional modelling assumptions
    concrete_m3_per_year: float = 100000
    inject_kg_per_m3: float = 0.393
    fixed_kg_per_m3: float = 0.354
    cement_saved_kg_per_m3: float = 14
    cement_usd_per_t: float = 110
    cement_avoided_tco2e_per_t: float = 0.67925
    injection_kwh_per_kg: float = 0.037
    injection_electric_price_usd_per_kwh: float = 0.124084910510981
    injection_fixed_opex_usd: float = 45000
    injection_capex_usd: float = 300000

    # Mineralization pathway: large-scale assumptions requiring proof
    slag_supply_t_per_year: float = 650000
    slag_uptake_tco2_per_t: float = 0.14
    aggregate_price_usd_per_t: float = 26
    saleable_fraction: float = 1.0
    slag_purchase_usd_per_t: float = 5
    slag_processing_usd_per_t: float = 5
    slag_logistics_usd_per_t: float = 4
    slag_kwh_per_tco2: float = 300  # converts 0.3 MWh/tCO2 to kWh
    slag_fixed_opex_usd: float = 800000
    slag_capex_usd: float = 18000000
    slag_logistics_tco2e_per_t: float = 60 * 0.000112

    # Scenario-only revenues; NOT verified carbon credits or real tariffs
    carbon_price_usd_per_net_t: float = 25
    utility_price_multiplier: float = 1.0
    capture_efficiency_override: Optional[float] = None

TECH = {
    "MEA absorption": dict(eta=0.90, capex=85120000.0, opex=39200000.0,
                           reference_t=765000.0, heat=3.78, elec_gj=0.535),
    "Solid adsorption": dict(eta=0.85, capex=84896000.0, opex=37184000.0,
                             reference_t=861363.636363636, heat=2.40, elec_gj=0.486),
}

def present_value_factor(rate: float, years: int) -> float:
    if years <= 0 or rate < 0: raise ValueError("Years must be >0 and discount >=0")
    return years if rate == 0 else (1-(1+rate)**(-years))/rate

def check_inputs(x: Inputs):
    if x.baseline_tco2 <= 0 or x.concrete_m3_per_year < 0 or x.slag_supply_t_per_year < 0:
        raise ValueError("Emission baseline must be positive; plant throughputs cannot be negative")
    if x.slag_uptake_tco2_per_t <= 0: raise ValueError("Slag CO2 uptake must be positive")
    if not 0 <= x.saleable_fraction <= 1: raise ValueError("Saleable fraction outside 0..1")
    if x.inject_kg_per_m3 < x.fixed_kg_per_m3 or x.fixed_kg_per_m3 < 0:
        raise ValueError("Mineralized CO2 cannot exceed injected CO2")
    if x.utility_price_multiplier < 0 or x.aggregate_price_usd_per_t < 0 or x.carbon_price_usd_per_net_t < 0:
        raise ValueError("Scenario multipliers/prices must be non-negative")
    if x.capture_efficiency_override is not None and not 0 < x.capture_efficiency_override <= 1:
        raise ValueError("Capture efficiency must be >0 and <=1")
    present_value_factor(x.discount_rate, x.life_years)

def right_sized_fraction(x: Inputs, tech: str) -> float:
    """Treat just enough flue gas to feed modeled ready-mix injection and slag uptake."""
    check_inputs(x)
    eta = x.capture_efficiency_override or TECH[tech]['eta']
    demand = (x.concrete_m3_per_year*x.inject_kg_per_m3/1000
              + x.slag_supply_t_per_year*x.slag_uptake_tco2_per_t)
    return min(1.0, demand/(x.baseline_tco2*eta))

def evaluate(x: Inputs, tech: str, fraction: float) -> dict:
    """Compute consistent annual flow, economic NPV and net avoided for one candidate.

    Slag processed is limited by the CO2 actually available for full per-tonne uptake,
    unlike the supplied Week 7 sensitivity table, which held slag production fixed.
    """
    check_inputs(x)
    if tech not in TECH: raise ValueError('Unknown capture technology')
    if not 0 < fraction <= 1: raise ValueError('Treated fraction must be >0 and <=1')
    t = TECH[tech]; eta = x.capture_efficiency_override or t['eta']
    captured = x.baseline_tco2 * fraction * eta
    demand_ready = x.concrete_m3_per_year * x.inject_kg_per_m3 / 1000
    injected = min(captured, demand_ready)
    treated_mix_ratio = injected / demand_ready if demand_ready else 0.0
    fixed_ready = injected*(x.fixed_kg_per_m3/x.inject_kg_per_m3) if x.inject_kg_per_m3 else 0.0
    cement_t_saved = x.concrete_m3_per_year*x.cement_saved_kg_per_m3/1000*treated_mix_ratio

    available_for_slag = max(0, captured-injected)
    slag_t = min(x.slag_supply_t_per_year, available_for_slag/x.slag_uptake_tco2_per_t)
    slag_fixed = slag_t*x.slag_uptake_tco2_per_t
    aggregate_t = slag_t+slag_fixed
    aggregate_sold_t = aggregate_t*x.saleable_fraction
    permanently_fixed = fixed_ready+slag_fixed
    vented = max(0,captured-injected-slag_fixed)

    heat_gj = captured*t['heat']
    capture_mwh = captured*t['elec_gj']/3.6
    slag_mwh = slag_fixed*x.slag_kwh_per_tco2/1000
    injection_mwh = injected*x.injection_kwh_per_kg
    heat_em = heat_gj*x.heat_factor_t_per_gj
    elec_em = (capture_mwh+slag_mwh+injection_mwh)*x.grid_factor_t_per_mwh
    logistics_em = slag_t*x.slag_logistics_tco2e_per_t
    avoided_cement = cement_t_saved*x.cement_avoided_tco2e_per_t
    net_avoided = permanently_fixed+avoided_cement-heat_em-elec_em-logistics_em

    ratio = captured/t['reference_t']
    capture_capex=t['capex']*ratio**x.capex_exponent
    original_opex=t['opex']*ratio
    energy_base=heat_gj*x.capture_heat_price_usd_per_gj+capture_mwh*x.capture_electric_price_usd_per_mwh
    other_opex=original_opex-energy_base
    capture_opex=other_opex+energy_base*x.utility_price_multiplier
    if other_opex < -0.01:
        raise ValueError('Capture energy price exceeds base OPEX; review reference assumptions')
    capture_crf=1/present_value_factor(x.discount_rate, x.life_years)
    lcoc=(capture_capex*capture_crf+capture_opex)/captured

    variable_slag_opex = slag_t*(x.slag_purchase_usd_per_t+x.slag_processing_usd_per_t+x.slag_logistics_usd_per_t)
    slag_energy_opex=slag_mwh*x.capture_electric_price_usd_per_mwh*x.utility_price_multiplier
    injection_opex=x.injection_fixed_opex_usd+injection_mwh*1000*x.injection_electric_price_usd_per_kwh*x.utility_price_multiplier
    total_opex=capture_opex+variable_slag_opex+slag_energy_opex+x.slag_fixed_opex_usd+injection_opex
    capex=capture_capex+x.slag_capex_usd+x.injection_capex_usd
    aggregate_revenue=aggregate_sold_t*x.aggregate_price_usd_per_t
    cement_revenue=cement_t_saved*x.cement_usd_per_t
    carbon_revenue=max(0,net_avoided)*x.carbon_price_usd_per_net_t
    noncarbon_revenue=aggregate_revenue+cement_revenue
    cashflow=noncarbon_revenue+carbon_revenue-total_opex
    pv=present_value_factor(x.discount_rate,x.life_years)
    npv=-capex+cashflow*pv
    net_cost_annual=capex/pv+total_opex-noncarbon_revenue
    return dict(technology=tech, treated_fraction=fraction, efficiency=eta,
                captured_t=captured, injected_t=injected, ready_fixed_t=fixed_ready,
                slag_processed_t=slag_t, slag_fixed_t=slag_fixed,
                permanently_fixed_t=permanently_fixed, vented_t=vented,
                unretained_site_t=x.baseline_tco2-permanently_fixed,
                aggregate_produced_t=aggregate_t, aggregate_sold_t=aggregate_sold_t,
                cement_saved_t=cement_t_saved, capture_heat_gj=heat_gj,
                capture_electric_mwh=capture_mwh, slag_electric_mwh=slag_mwh,
                injection_electric_mwh=injection_mwh, emissions_heat_t=heat_em,
                emissions_electric_t=elec_em, emissions_logistics_t=logistics_em,
                avoided_cement_t=avoided_cement, net_avoided_t=net_avoided,
                capture_capex_usd=capture_capex, capture_opex_usd=capture_opex,
                lcoc_usd_per_captured_t=lcoc, capex_usd=capex, annual_opex_usd=total_opex,
                aggregate_revenue_usd=aggregate_revenue, cement_savings_usd=cement_revenue,
                carbon_scenario_revenue_usd=carbon_revenue,
                annual_net_usd=cashflow, npv_usd=npv,
                abatement_cost_usd_per_net_t=net_cost_annual/net_avoided if net_avoided>0 else None,
                break_even_carbon_usd_per_t=max(0,net_cost_annual/net_avoided) if net_avoided>0 else None)

def compare(x: Inputs) -> list[dict]:
    return [evaluate(x, name, fraction)
            for name in TECH for fraction in (1.0,right_sized_fraction(x,name))]

def optimize(x: Inputs, criterion: str = 'Max NPV', require_positive_npv: bool = False):
    """Grid search for best capture technology and flue-gas treatment fraction.

    Candidate fraction is variable; all material supply, sale and emissions constraints
    are recalculated at each evaluation. This is an illustrative optimization.
    """
    candidates=[]
    for name in TECH:
        fractions={round(i/200,5) for i in range(1,201)}
        fractions.add(right_sized_fraction(x,name))
        for f in fractions:
            r=evaluate(x,name,f)
            if r['net_avoided_t']<=0: continue
            if require_positive_npv and r['npv_usd']<0: continue
            candidates.append(r)
    if not candidates: return None
    if criterion == 'Max NPV': return max(candidates,key=lambda r:r['npv_usd'])
    if criterion == 'Max net CO2e avoided': return max(candidates,key=lambda r:r['net_avoided_t'])
    if criterion == 'Min cost per net tonne avoided': return min(candidates,key=lambda r:r['abatement_cost_usd_per_net_t'])
    raise ValueError('Unknown optimization objective')

if __name__ == '__main__':
    x=Inputs()
    for r in compare(x):
        print(f"{r['technology']:16s} treated={r['treated_fraction']:.4%} "
              f"NPV=${r['npv_usd']:,.0f} net avoided={r['net_avoided_t']:,.0f} t/y")
    x0=replace(x, carbon_price_usd_per_net_t=0)
    r=evaluate(x0,'Solid adsorption',right_sized_fraction(x0,'Solid adsorption'))
    print(f"Carbon-price-zero optimized-size NPV: ${r['npv_usd']:,.0f}")


def ready_mix_injection_pathway(x: Inputs, technology: str) -> dict:
    """Week 6 incremental ready-mix project NPV with capture allocated at LCOC.

    Only injection hardware CAPEX is charged here, not a new complete capture plant.
    The full-scale capture case supplies the reference levelized cost. This NPV
    cannot simply be added to the stand-alone slag NPV or integrated NPV because
    the project/investment boundaries differ.
    """
    check_inputs(x)
    full_capture = evaluate(x, technology, 1.0)
    demand_t = x.concrete_m3_per_year * x.inject_kg_per_m3 / 1000.0
    injected_t = min(full_capture['captured_t'], demand_t)
    share = injected_t / demand_t if demand_t else 0.0
    cement_saved_t = x.concrete_m3_per_year * x.cement_saved_kg_per_m3 / 1000.0 * share
    injection_electric_kwh = injected_t * 1000.0 * x.injection_kwh_per_kg
    cement_savings_usd = cement_saved_t * x.cement_usd_per_t
    allocated_capture_usd = injected_t * full_capture['lcoc_usd_per_captured_t']
    power_usd = injection_electric_kwh * x.injection_electric_price_usd_per_kwh * x.utility_price_multiplier
    annual_cashflow = (cement_savings_usd - allocated_capture_usd
                       - x.injection_fixed_opex_usd - power_usd)
    npv = -x.injection_capex_usd + annual_cashflow * present_value_factor(x.discount_rate, x.life_years)
    return dict(npv_usd=npv, injected_t=injected_t,
                fixed_t=injected_t*x.fixed_kg_per_m3/x.inject_kg_per_m3 if x.inject_kg_per_m3 else 0,
                cement_saved_t=cement_saved_t, capture_allocated_usd=allocated_capture_usd,
                cement_savings_usd=cement_savings_usd,
                injection_electric_kwh=injection_electric_kwh,
                annual_cashflow_usd=annual_cashflow)


def slag_mineralization_pathway(x: Inputs, technology: str) -> dict:
    """Stand-alone slag mineralization with right-sized capture and no ready-mix line.

    Includes corresponding capture + slag capital and operating expenses; can use
    carbon-benefit scenarios when specified. This is a separate plant-design case.
    """
    slag_x = replace(x, concrete_m3_per_year=0.0,
                     injection_capex_usd=0.0, injection_fixed_opex_usd=0.0)
    return evaluate(slag_x, technology, right_sized_fraction(slag_x, technology))


def dashboard_summary(x: Inputs, technology: str) -> dict:
    """Three distinct financial boundaries and integrated physical CO2 KPIs."""
    if technology not in TECH:
        raise ValueError('Unknown capture technology')
    integrated = evaluate(x, technology, right_sized_fraction(x, technology))
    return dict(injection=ready_mix_injection_pathway(x, technology),
                slag=slag_mineralization_pathway(x, technology),
                integrated=integrated)
