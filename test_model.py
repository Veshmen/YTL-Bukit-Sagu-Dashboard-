"""Quick calculation checks using Week 5 and Week 7 submitted spreadsheet values."""
from dataclasses import replace
from model import Inputs, evaluate, optimize, right_sized_fraction

def close(actual, expected, tolerance=0.02):
    assert abs(actual-expected)<tolerance, (actual,expected)

x=Inputs()
a=evaluate(x,'Solid adsorption',1.0)
r=evaluate(x,'Solid adsorption',right_sized_fraction(x,'Solid adsorption'))
close(a['captured_t'],163171.862979125)
close(a['capture_capex_usd'],31286895.486786533)
close(a['capture_opex_usd'],7043926.974477431)
close(a['npv_usd'],-34790500.42001097)
close(r['treated_fraction'],0.5579350406242951)
close(r['captured_t'],91039.3)
close(r['permanently_fixed_t'],91035.4)
close(r['net_avoided_t'],46062.916544)
close(r['npv_usd'],12206054.985765532)
close(evaluate(replace(x,carbon_price_usd_per_net_t=0),'Solid adsorption',r['treated_fraction'])['npv_usd'],-86728.13175532222)
assert optimize(x,'Max NPV') is not None
assert evaluate(replace(x,saleable_fraction=0.5),'Solid adsorption',r['treated_fraction'])['npv_usd']<r['npv_usd']
assert evaluate(replace(x,utility_price_multiplier=1.3),'Solid adsorption',r['treated_fraction'])['npv_usd']<r['npv_usd']
print('All checks passed; baseline and right-size case reproduce the supplied Week 7 model.')

# Revised dashboard's three distinct financial project boundaries
from model import dashboard_summary, ready_mix_injection_pathway, slag_mineralization_pathway
base = dashboard_summary(Inputs(), 'Solid adsorption')
close(base['injection']['npv_usd'], 835978.9728614117)
close(base['slag']['npv_usd'], 11107771.304854244)
close(base['integrated']['npv_usd'], 12206054.985765532)
close(base['integrated']['injected_t'], 39.3)
close(base['integrated']['slag_fixed_t'], 91000.0)
close(base['integrated']['net_avoided_t'], 46062.916544)
assert dashboard_summary(replace(Inputs(),aggregate_price_usd_per_t=20), 'Solid adsorption')['slag']['npv_usd'] < base['slag']['npv_usd']
assert dashboard_summary(replace(Inputs(),utility_price_multiplier=1.5), 'Solid adsorption')['injection']['npv_usd'] < base['injection']['npv_usd']
assert dashboard_summary(replace(Inputs(),capture_efficiency_override=.65), 'Solid adsorption')['integrated']['treated_fraction'] > base['integrated']['treated_fraction']
print('Updated dashboard KPIs and input sensitivities: all checks passed.')
