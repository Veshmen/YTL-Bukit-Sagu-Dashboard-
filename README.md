# YTL Bukit Sagu | Updated Streamlit Decision-Support Dashboard

This version incorporates your supplied title image and the requested simplified interface. It uses the same Week 5–7 calculation engine, with additional functions for **three different NPV boundaries**.

## What's on the dashboard?

**Five sidebar controls only**

1. Capture technology — MEA absorption or Solid adsorption
2. Capture efficiency — continuous integer slider from **65% to 95%** (defaults to 90% for MEA and 85% for Solid; changes when switching technology)
3. Carbon price — USD per net tCO₂e
4. Aggregate sale price — USD per tonne
5. Utility price multiplier — applied to electricity and heat cost assumptions

**Six KPI tiles**

- NPV — CO₂ injection into concrete (25-year incremental ready-mix pathway)
- NPV — CO₂ mineralization in steel slag (25-year stand-alone capture + slag pathway)
- NPV — integrated system (25-year combined capture + concrete + slag project)
- Total CO₂ injected into concrete (t/year)
- Total CO₂ mineralized in slag (t/year)
- Integrated net CO₂e avoided (t/year)

The dashboard keeps technology comparison, a carbon/financial balance, and sensitivity analysis. It removes the decision objective controls, advanced optimization constraint, source crosswalk, assumptions tab, top technology/flue-gas KPI tiles, and unwanted information banners/footers.

## Upload your revised files to GitHub and deploy online

1. Extract the ZIP to a folder on your computer.
2. In GitHub, open your existing Streamlit repository.
3. Replace / upload the **six files** in the same root folder:

   - `streamlit_app.py`
   - `model.py`
   - `title_banner.jpg` ← **important — your uploaded photo is here**
   - `requirements.txt`
   - `test_model.py`
   - `README.md`

4. **Commit changes.** Your Streamlit Community Cloud app should redeploy from GitHub automatically. If not, select **Reboot / Reboot app** in Streamlit's app management menu.
5. If creating a new app, choose your GitHub repository, branch `main`, and main file path `streamlit_app.py` at [share.streamlit.io](https://share.streamlit.io/).

The app works on Streamlit Community Cloud. No local Python installation is needed.

## Modelling boundaries — IMPORTANT for your A-grade technical explanation

The values are adapted from your group's Week 5–7 submissions, rather than measured full-scale plant performance.

The first two NPV figures **do not add up to the integrated NPV**, because they are different investment cases:

- **Concrete CO₂-injection NPV**: Week 6 methodology; an **incremental** ready-mix equipment investment. It includes capture cost allocated at an existing/reference levelized capture cost (LCOC) rather than full capture-plant CAPEX. At the baseline assumptions, its NPV is **USD 835,979** for solid adsorption.
- **Slag mineralization NPV**: stand-alone slag operation with capture plant sized for steel-slag uptake. No concrete facility/cement savings are included. Under default solid adsorption assumptions, the scenario gives about **USD 11.11 million** NPV.
- **Integrated NPV**: full right-sized capture plant plus concrete injection plus slag mineralization. Under default solid-adsorption assumptions, NPV is approximately **USD 12.21 million**.

At default solid adsorption / 85% capture: **39.3 t/year CO₂ injected into concrete; 91,000 t/year CO₂ fixed in slag; 46,063 tCO₂e/year integrated net avoided**. Concrete injection **is not the same as carbon fixation**: 35.4 t/year is fixed in concrete at default settings.

The integrated model sizes flue-gas treatment so the captured CO₂ approximately matches both pathway demands, avoiding unnecessary capture of unused CO₂. It is an **engineering scenario calculation**, not a validated plant design. Slag supply, slag uptake, saleable aggregate demand, operating costs, energy emissions factors, and carbon revenue all need third-party or facility validation before commercial decisions.

## Calculation checks (optional, locally)

```bash
python -m pip install -r requirements.txt
python test_model.py
python -m streamlit run streamlit_app.py
```

### If your Streamlit app has an error

- `FileNotFoundError: title_banner.jpg`: upload `title_banner.jpg` to the same repository folder as `streamlit_app.py`.
- `ModuleNotFoundError: model`: upload `model.py` next to the app script.
- Missing plotly or pandas: make sure `requirements.txt` is in that folder.
