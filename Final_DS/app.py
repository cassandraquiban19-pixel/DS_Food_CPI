import json
import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import requests
import folium
from branca.colormap import LinearColormap
from streamlit_folium import st_folium

st.set_page_config(page_title="Food Prices Across the Philippines", page_icon="🌿", layout="wide")

# ------------------------------------------------------------
# FOREST & HARVEST DASHBOARD THEME
# ------------------------------------------------------------
st.markdown("""
<style>
:root {
    --forest: #24563A;
    --forest-deep: #183F2B;
    --sage: #79966D;
    --sage-light: #DCE7D1;
    --cream: #F6F8F1;
    --cream-warm: #FBF7ED;
    --harvest: #D9B86C;
    --border: #DDE6D5;
    --muted: #617363;
}
.main, .stApp { background:var(--cream); }
.block-container { max-width:1480px; padding-top:1.25rem; padding-bottom:2rem; }

/* Header */
.hero {
    padding: 24px 28px 22px;
    margin-bottom: 22px;
    border: 1px solid var(--border);
    border-left: 5px solid var(--harvest);
    border-radius: 18px;
    background: linear-gradient(125deg, #FFFFFF 0%, var(--cream-warm) 58%, #EEF3E8 100%);
    box-shadow: 0 6px 22px rgba(36,86,58,.07);
}
.hero-eyebrow {
    color:var(--sage); font-size:12px; font-weight:800;
    letter-spacing:1.8px; text-transform:uppercase; margin-bottom:7px;
}
.hero-title { color:var(--forest); font-size:38px; line-height:1.08; font-weight:800; margin:0; letter-spacing:-.6px; }
.hero-subtitle { color:var(--muted); font-size:15px; margin-top:8px; }
.view-strip {
    display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
    margin:0 0 22px; padding:13px 14px; background:#FFFFFF;
    border:1px solid var(--border); border-radius:14px;
    box-shadow:0 3px 12px rgba(36,86,58,.04);
}
.view-strip > div { padding:3px 12px; border-right:1px solid var(--border); }
.view-strip > div:last-child { border-right:none; }
.view-label { display:block; color:#9B8145; font-size:10px; font-weight:800; letter-spacing:1.25px; margin-bottom:3px; }
.view-strip strong { color:var(--forest); font-size:13px; font-weight:700; }
@media (max-width: 900px) { .view-strip { grid-template-columns:repeat(2,1fr); } .view-strip > div:nth-child(2) { border-right:none; } }

/* Sidebar */
[data-testid="stSidebar"] { background:#EEF3E8; border-right:1px solid var(--border); }
[data-testid="stSidebar"] h2 { color:var(--forest) !important; font-size:20px; }
[data-testid="stSidebar"] label { color:#365A40 !important; font-weight:600; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { border-radius:10px; border-color:#CFDCC9; }

/* KPI cards */
.kpi-card {
    box-sizing:border-box; width:100%; min-height:136px; height:100%;
    background:#FFFFFF; border:1px solid var(--border); border-top:4px solid var(--sage);
    padding:16px 17px 14px; border-radius:15px;
    box-shadow:0 5px 16px rgba(36,86,58,.055);
    display:flex; flex-direction:column; align-items:flex-start; gap:8px;
}
.kpi-card.harvest-kpi { border-top-color:var(--harvest); }
.kpi-label {
    color:var(--muted); font-size:13px; line-height:1.35; font-weight:600;
    white-space:normal; overflow-wrap:break-word; word-break:normal;
}
.kpi-value {
    color:var(--forest); font-weight:800; font-size:clamp(1.15rem, 1.65vw, 1.9rem);
    line-height:1.15; width:100%; white-space:normal; overflow:visible;
    overflow-wrap:anywhere; word-break:normal; text-overflow:clip;
}
.kpi-value.numeric { font-size:clamp(1.55rem, 1.9vw, 2.05rem); }
.kpi-note { color:#788578; font-size:12px; line-height:1.35; margin-top:auto; }

/* Controls */
.stButton > button {
    background:var(--forest); color:#FFFFFF; border:1px solid var(--forest);
    border-radius:10px; font-weight:700; transition:all .15s ease-in-out;
}
.stButton > button:hover { background:var(--forest-deep); color:#FFFFFF; border-color:var(--harvest); }

/* Section headings */
h1,h2,h3,h4 { color:var(--forest) !important; }
.section-title {
    color:var(--forest); font-size:21px; font-weight:800;
    margin: 24px 0 10px; letter-spacing:-.15px;
}
.section-number { color:#B08D43; font-size:12px; font-weight:800; letter-spacing:1.2px; margin-right:7px; }
.story-title {
    color:var(--forest); font-size:22px; font-weight:800;
    line-height:1.2; margin:24px 0 2px; letter-spacing:-.2px;
}
.story-subtitle { color:#657767; font-size:13px; margin:0 0 8px; }

/* Chart containers and data explorer */
[data-testid="stVerticalBlockBorderWrapper"] {
    border:1px solid var(--border) !important;
    border-radius:16px !important;
    box-shadow:0 4px 16px rgba(36,86,58,.045);
    background:#FFFFFF;
}
[data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:12px; overflow:hidden; }
[data-testid="stDownloadButton"] button { border-radius:10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">UN SDG 2 • ZERO HUNGER</div>
    <div class="hero-title">Food Prices Across the Philippines</div>
    <div class="hero-subtitle">Regional food CPI patterns and changes from 2018 to 2025</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------
DATA_FILE = Path(__file__).resolve().parent / "MLDST_Final_Cleaned.csv"
if not DATA_FILE.exists():
    st.error("MLDST_Final_Cleaned.csv was not found beside app.py.")
    st.stop()

df = pd.read_csv(DATA_FILE)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["CPI"] = pd.to_numeric(df["CPI"], errors="coerce")
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
df = df.dropna(subset=["Date", "CPI", "Year", "Month", "Geolocation", "Commodity_Name"])
df["Year"] = df["Year"].astype(int)
df["Month"] = df["Month"].astype(int)

# ------------------------------------------------------------
# FILTERS
# ------------------------------------------------------------
years = sorted(df["Year"].unique())
regions = sorted([x for x in df["Geolocation"].unique() if x != "PHILIPPINES"])
categories = sorted([x for x in df["Commodity_Name"].unique() if x != "Food"])

def reset_filters():
    st.session_state["year_filter"] = "All Years"
    st.session_state["region_filter"] = "All Regions"
    st.session_state["category_filter"] = "All Categories"

with st.sidebar:
    st.markdown("## Explore the Data")
    selected_year = st.selectbox(
        "Year", ["All Years"] + years, index=0, key="year_filter"
    )
    selected_region = st.selectbox(
        "Region / Geolocation", ["All Regions"] + regions, index=0, key="region_filter"
    )
    selected_category = st.selectbox(
        "Food Category", ["All Categories"] + categories, index=0, key="category_filter"
    )
    st.button("Reset Filters", use_container_width=True, on_click=reset_filters)

# ------------------------------------------------------------
# ACTIVE FILTER DATA
# ------------------------------------------------------------
filtered_df = df.copy()
if selected_year != "All Years":
    filtered_df = filtered_df[filtered_df["Year"] == int(selected_year)]
if selected_region != "All Regions":
    filtered_df = filtered_df[filtered_df["Geolocation"] == selected_region]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["Commodity_Name"] == selected_category]

kpi_location = "PHILIPPINES" if selected_region == "All Regions" else selected_region
kpi_category = "Food" if selected_category == "All Categories" else selected_category

series = df[(df["Geolocation"] == kpi_location) & (df["Commodity_Name"] == kpi_category)].copy()

base_cpi = series.loc[series["Year"] == 2018, "CPI"].mean()
if selected_year == "All Years":
    end_year = 2025
    current_cpi = series.loc[series["Year"] == 2025, "CPI"].mean()
else:
    end_year = int(selected_year)
    current_cpi = series.loc[series["Year"] == end_year, "CPI"].mean()

cpi_change = current_cpi - base_cpi if pd.notna(base_cpi) and pd.notna(current_cpi) else None

# ------------------------------------------------------------
# COMPARISON PERIODS
# ------------------------------------------------------------
y_start, y_end = 2018, end_year
period_label = f"({y_start}–{y_end})"

# ------------------------------------------------------------
# CURRENT VIEW SUMMARY
# ------------------------------------------------------------
view_label = "2018–2025" if selected_year == "All Years" else str(selected_year)
comparison_label = "2018 → 2025" if selected_year == "All Years" else ("Baseline year" if int(selected_year) == 2018 else f"2018 → {selected_year}")
region_label = "All Philippine regions" if selected_region == "All Regions" else selected_region
category_label = "All food categories" if selected_category == "All Categories" else selected_category
st.markdown(f"""
<div class="view-strip">
  <div><span class="view-label">VIEWING</span><strong>{view_label}</strong></div>
  <div><span class="view-label">COMPARISON</span><strong>{comparison_label}</strong></div>
  <div><span class="view-label">REGION</span><strong>{region_label}</strong></div>
  <div><span class="view-label">CATEGORY</span><strong>{category_label}</strong></div>
</div>
""", unsafe_allow_html=True)

# Category ranking
category_base = df[df["Geolocation"] == kpi_location].copy()
if selected_category != "All Categories":
    category_base = category_base[category_base["Commodity_Name"] == selected_category]
cat_pivot = category_base[category_base["Year"].isin([y_start, y_end])].groupby(["Commodity_Name", "Year"])["CPI"].mean().unstack()
if y_start != y_end and y_start in cat_pivot.columns and y_end in cat_pivot.columns:
    cat_pivot["Change"] = cat_pivot[y_end] - cat_pivot[y_start]
    cat_pivot = cat_pivot.drop(index="Food", errors="ignore")
    category_rank = cat_pivot["Change"].dropna().sort_values(ascending=False)
else:
    category_rank = pd.Series(dtype=float)

# Regional ranking
regional_base = df[(df["Geolocation"] != "PHILIPPINES") & (df["Commodity_Name"] == kpi_category)]
reg_pivot = regional_base[regional_base["Year"].isin([y_start, y_end])].groupby(["Geolocation", "Year"])["CPI"].mean().unstack()
if y_start != y_end and y_start in reg_pivot.columns and y_end in reg_pivot.columns:
    reg_pivot["Change"] = reg_pivot[y_end] - reg_pivot[y_start]
    regional_rank = reg_pivot["Change"].dropna().sort_values(ascending=False)
else:
    regional_rank = pd.Series(dtype=float)

# ------------------------------------------------------------
# KPI CARDS — responsive labels and complete, wrapping values
# ------------------------------------------------------------
if selected_region == "All Regions" and selected_category == "All Categories":
    cpi_metric_label = "National Food CPI"
elif selected_region != "All Regions" and selected_category == "All Categories":
    cpi_metric_label = "Regional Food CPI"
elif selected_region == "All Regions" and selected_category != "All Categories":
    cpi_metric_label = "National Category CPI"
else:
    cpi_metric_label = "Selected Food CPI"

# KPI 3 and 4 use the same selected geography/category series as the trend chart.
# With All Years selected, calculate across the dashboard's 2018–2025 study period.
# With a specific year selected, calculate within that calendar year.
monthly_kpi = series.groupby("Date", as_index=False)["CPI"].mean().sort_values("Date")
if selected_year == "All Years":
    monthly_kpi = monthly_kpi[
        monthly_kpi["Date"].dt.year.between(2018, 2025)
    ].copy()
else:
    monthly_kpi = monthly_kpi[
        monthly_kpi["Date"].dt.year == int(selected_year)
    ].copy()

# KPI 3: highest monthly CPI and the month when it occurred.
if not monthly_kpi.empty:
    peak_row = monthly_kpi.loc[monthly_kpi["CPI"].idxmax()]
    peak_cpi_value = f"{float(peak_row['CPI']):.2f}"
    peak_cpi_note = f"Peak month: {pd.Timestamp(peak_row['Date']).strftime('%b %Y')}"
else:
    peak_cpi_value = "—"
    peak_cpi_note = "No monthly observations available"

# KPI 4: greatest positive change between consecutive calendar months.
# Do not compare across a missing month if the selected series has a gap.
if not monthly_kpi.empty:
    monthly_kpi["Month ID"] = monthly_kpi["Date"].dt.year * 12 + monthly_kpi["Date"].dt.month
    monthly_kpi["Monthly Change"] = monthly_kpi["CPI"].diff()
    consecutive_month = monthly_kpi["Month ID"].diff().eq(1)
    positive_increases = monthly_kpi.loc[
        consecutive_month & monthly_kpi["Monthly Change"].gt(0)
    ].copy()
else:
    positive_increases = pd.DataFrame(columns=["Date", "Monthly Change"])

if not positive_increases.empty:
    increase_row = positive_increases.loc[positive_increases["Monthly Change"].idxmax()]
    increase_value = f"{float(increase_row['Monthly Change']):+.2f}"
    end_date = pd.Timestamp(increase_row["Date"])
    start_date = end_date - pd.offsets.MonthBegin(1)
    increase_note = f"{start_date.strftime('%b %Y')} → {end_date.strftime('%b %Y')}"
else:
    increase_value = "—"
    increase_note = "No positive consecutive-month increase"

kpi_items = [
    (cpi_metric_label, "—" if pd.isna(current_cpi) else f"{current_cpi:.2f}", "CPI (2018 = 100)", True),
    ("Change vs. 2018", "—" if cpi_change is None else f"{cpi_change:+.2f}", "index points", True),
    ("Peak Monthly CPI", peak_cpi_value, peak_cpi_note, True),
    ("Largest Monthly Increase", increase_value, increase_note, True),
]
cols = st.columns(4, gap="medium")
for col, (label, value, note, numeric) in zip(cols, kpi_items):
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    safe_note = html.escape(str(note))
    value_class = "kpi-value numeric" if numeric else "kpi-value"
    card_class = "kpi-card harvest-kpi" if label == "Largest Monthly Increase" else "kpi-card"
    with col:
        st.markdown(
            f'<div class="{card_class}">'
            f'<div class="kpi-label">{safe_label}</div>'
            f'<div class="{value_class}">{safe_value}</div>'
            f'<div class="kpi-note">{safe_note}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# CHART STYLE
# ------------------------------------------------------------
def style_chart(fig, height=400):
    fig.update_layout(
        height=height,
        paper_bgcolor="#F6F8F1",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#3D5745", family="Arial"),
        margin=dict(l=60, r=30, t=25, b=55),
        hoverlabel=dict(bgcolor="#FBF7ED", bordercolor="#D9B86C", font_color="#183F2B"),
    )
    fig.update_xaxes(gridcolor="#E6EDE1", zerolinecolor="#D4DFCC")
    fig.update_yaxes(gridcolor="#E6EDE1", zerolinecolor="#D4DFCC")
    return fig

# ------------------------------------------------------------
# 1. FOOD CPI TREND
# ------------------------------------------------------------
trend_subject = (
    "Food" if selected_category == "All Categories" else selected_category
)
trend_location = (
    "the Philippines" if selected_region == "All Regions" else selected_region
)
if selected_year == "All Years":
    trend_title = "Food CPI Increased Steadily Across 2018–2025" if selected_category == "All Categories" else f"{trend_subject} CPI trend, 2018–2025"
else:
    trend_title = f"{trend_subject} CPI trend, 2018–{end_year}"
trend_subtitle = f"How did {trend_subject} CPI in {trend_location} change over time?"
st.markdown(f"""
<div class="story-title">{trend_title}</div>
<div class="story-subtitle">{trend_subtitle}</div>
""", unsafe_allow_html=True)

trend = series.groupby("Year", as_index=False)["CPI"].mean().sort_values("Year")
trend = trend[trend["Year"] <= end_year]

if not trend.empty:
    fig = px.line(
        trend,
        x="Year",
        y="CPI",
        labels={"Year":"Year", "CPI":"CPI (2018 = 100)"},
        markers=True,
    )
    fig.update_traces(
        line_color="#24563A",
        marker_color="#24563A",
        marker_size=7,
        line_width=3,
        text=trend["CPI"].round(1),
        textposition="top center",
        mode="lines+markers+text",
        hovertemplate="Year: %{x}<br>CPI: %{y:.1f}<extra></extra>",
    )
    fig.update_layout(
        height=410,
        paper_bgcolor="#F6F8F1",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#24563A", family="Arial"),
        margin=dict(l=62, r=25, t=12, b=55),
        showlegend=False,
        hoverlabel=dict(bgcolor="#FBF7ED", bordercolor="#D9B86C", font_color="#183F2B"),
    )
    fig.update_xaxes(
        dtick=1,
        tickmode="linear",
        gridcolor="#E6EDE1",
        zeroline=False,
        title="Year",
        linecolor="#DDE6D5",
    )
    ymin = float(trend["CPI"].min())
    ymax = float(trend["CPI"].max())
    pad = max(2, (ymax - ymin) * 0.18)
    fig.update_yaxes(
        range=[max(0, ymin - pad), ymax + pad],
        gridcolor="#E6EDE1",
        zeroline=False,
        title="CPI (2018 = 100)",
        linecolor="#DDE6D5",
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("No Food CPI observations are available for the selected filters.")

# ------------------------------------------------------------
# 2. CATEGORY CHANGE
# ------------------------------------------------------------
st.markdown(f"""
<div class="section-title"><span class="section-number">02</span>Food Category Change {period_label}</div>
<div class="story-subtitle">Which food categories experienced the largest CPI increases?</div>
""", unsafe_allow_html=True)
if len(category_rank):
    chart = cat_pivot.reset_index().sort_values("Change")
    fig = px.bar(chart, x="Change", y="Commodity_Name", orientation="h", text="Change",
                 labels={"Change":"CPI change (index points)", "Commodity_Name":"Food category"})
    fig.update_traces(marker_color="#79966D", texttemplate="%{text:.2f}", textposition="outside")
    style_chart(fig, max(350, 55 * len(chart)))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Select a comparison period with two different years to show category change.")

# ------------------------------------------------------------
# 3. REGIONAL CHANGE
# ------------------------------------------------------------
st.markdown(f"""
<div class="section-title"><span class="section-number">03</span>Regional Change {period_label}</div>
<div class="story-subtitle">Which Philippine regions recorded the largest CPI increases?</div>
""", unsafe_allow_html=True)
if len(regional_rank):
    chart = reg_pivot.reset_index().sort_values("Change")
    chart["Region"] = chart["Geolocation"]
    fig = px.bar(chart, x="Change", y="Region", orientation="h", text="Change",
                 labels={"Change":"CPI change (index points)", "Region":"Region"})
    fig.update_traces(marker_color="#79966D", texttemplate="%{text:.2f}", textposition="outside")
    style_chart(fig, max(500, 32 * len(chart)))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
else:
    st.info("Select a comparison period with two different years to show regional change.")

# ------------------------------------------------------------
# 4. PHILIPPINE REGIONAL CHOROPLETH
# ------------------------------------------------------------
PSGC_MAP = {
    "Region I (Ilocos Region)": "100000000",
    "Region II (Cagayan Valley)": "200000000",
    "Region III (Central Luzon)": "300000000",
    "Region IV-A (CALABARZON)": "400000000",
    "MIMAROPA Region": "1700000000",
    "Region V (Bicol Region)": "500000000",
    "Region VI (Western Visayas)": "600000000",
    "Region VII (Central Visayas)": "700000000",
    "Region VIII (Eastern Visayas)": "800000000",
    "Region IX (Zamboanga Peninsula)": "900000000",
    "Region X (Northern Mindanao)": "1000000000",
    "Region XI (Davao Region)": "1100000000",
    "Region XII (SOCCSKSARGEN)": "1200000000",
    "National Capital Region (NCR)": "1300000000",
    "Cordillera Administrative Region (CAR)": "1400000000",
    "Region XIII (Caraga)": "1600000000",
    "Negros Island Region (NIR)": "1800000000",
    "Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)": "1900000000",
}
GEOJSON_URL = "https://raw.githubusercontent.com/tordecilla/ph-drilldown-map/refs/heads/main/geo-nir/country.0.001.json"

@st.cache_data(show_spinner=False)
def get_geojson():
    local = Path(__file__).resolve().parent / "philippines_regions.geojson"
    if local.exists():
        with local.open("r", encoding="utf-8") as f:
            return json.load(f)
    r = requests.get(GEOJSON_URL, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_code(props):
    known = set(PSGC_MAP.values())
    for value in props.values():
        text = str(value)
        digits = "".join(ch for ch in text if ch.isdigit())
        if digits in known:
            return digits
        if text.strip() in known:
            return text.strip()
        for code in known:
            if code in text:
                return code
    return None

st.markdown(f"""
<div class="section-title"><span class="section-number">04</span>Regional Food CPI Map {period_label}</div>
<div class="story-subtitle">Where were Food CPI increases highest across the Philippines?</div>
""", unsafe_allow_html=True)
if y_start != y_end:
    map_base = df[(df["Geolocation"] != "PHILIPPINES") & (df["Commodity_Name"] == kpi_category) & (df["Year"].isin([y_start, y_end]))]
    map_pivot = map_base.groupby(["Geolocation", "Year"])["CPI"].mean().unstack()
    if y_start in map_pivot.columns and y_end in map_pivot.columns:
        map_pivot["Change"] = map_pivot[y_end] - map_pivot[y_start]
        map_pivot = map_pivot.dropna(subset=["Change"]).reset_index()
        map_pivot["PSGC"] = map_pivot["Geolocation"].map(PSGC_MAP)
        map_pivot = map_pivot.dropna(subset=["PSGC"])
        values = dict(zip(map_pivot["PSGC"], map_pivot["Change"]))
        try:
            geo = get_geojson()
            matched = []
            reverse = {v:k for k,v in PSGC_MAP.items()}
            for feature in geo.get("features", []):
                props = feature.setdefault("properties", {})
                code = extract_code(props)
                if code in values:
                    props["dashboard_region"] = reverse[code]
                    props["dashboard_change"] = float(values[code])
                    matched.append(feature)
            if len(matched) < 15:
                raise ValueError(f"Only {len(matched)} of 18 Philippine regions matched the GeoJSON.")
            map_geo = {"type":"FeatureCollection", "features":matched}
            vmin, vmax = float(map_pivot["Change"].min()), float(map_pivot["Change"].max())
            if vmin == vmax: vmin -= .01; vmax += .01
            cmap = LinearColormap(["#FBF7ED","#E6EBD8","#B9CBA9","#79966D","#24563A","#D9B86C"], vmin=vmin, vmax=vmax)
            cmap.caption = "CPI change (index points)"
            fmap = folium.Map(location=[12.5,122.0], zoom_start=5, tiles=None, control_scale=False)
            # Plain warm-cream map background: no third-party basemap, API key, or watermark.
            fmap.get_root().header.add_child(folium.Element("""<style>.leaflet-container { background: #F6F8F1 !important; }</style>"""))
            fmap.fit_bounds([[4.5,116.0],[21.5,127.5]])
            def sty(f):
                val = f["properties"]["dashboard_change"]
                return {"fillColor":cmap(val),"color":"#FFFFFF","weight":1.2,"fillOpacity":0.88}
            folium.GeoJson(map_geo, style_function=sty,
                highlight_function=lambda f:{"weight":2.5,"color":"#183F2B","fillOpacity":1},
                tooltip=folium.GeoJsonTooltip(fields=["dashboard_region","dashboard_change"], aliases=["Region","CPI change (index points)"], localize=True, sticky=False)
            ).add_to(fmap)
            cmap.add_to(fmap)
            st_folium(fmap, use_container_width=True, height=520, returned_objects=[])
        except Exception as exc:
            st.error(f"Map could not be loaded: {exc}")
    else:
        st.info("The selected comparison period has incomplete map data.")
else:
    st.info("Select a year after 2018 to display the regional CPI change map.")

# ------------------------------------------------------------
# 5. MONTHLY MOVEMENT
# ------------------------------------------------------------
monthly_subject = "Food" if selected_category == "All Categories" else selected_category
monthly_location = "the Philippines" if selected_region == "All Regions" else selected_region
monthly_title = (
    "Food CPI Movement By Month"
    if selected_year == "All Years"
    else f"Food CPI Movement By Month In {selected_year}"
)
st.markdown(f"""
<div class="story-title">{monthly_title}</div>
<div class="story-subtitle">How did {monthly_subject} CPI in {monthly_location} move from month to month?</div>
""", unsafe_allow_html=True)
monthly = series.groupby("Date", as_index=False)["CPI"].mean().sort_values("Date")
if selected_year != "All Years":
    monthly = monthly[monthly["Date"].dt.year == int(selected_year)]
fig = px.line(monthly, x="Date", y="CPI", labels={"Date":"Month", "CPI":"CPI (2018 = 100)"})
fig.update_traces(line_color="#79966D", line_width=2.5)
style_chart(fig, 400)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ------------------------------------------------------------
# 6. YEAR-ON-YEAR INFLATION / DEFLATION
# ------------------------------------------------------------
st.markdown("""
<div class="section-title"><span class="section-number">06</span>Monthly Inflation vs. Deflation</div>
<div class="story-subtitle">How did the selected Food CPI compare with the same month one year earlier?</div>
""", unsafe_allow_html=True)

# Calculate the year-on-year rate before applying the selected-year filter so
# each month is compared with the same month in the prior calendar year.
inflation_series = (
    series.groupby("Date", as_index=False)["CPI"].mean().sort_values("Date").copy()
)
previous_year = inflation_series[["Date", "CPI"]].copy()
previous_year["Date"] = previous_year["Date"] + pd.DateOffset(years=1)
previous_year = previous_year.rename(columns={"CPI": "CPI_Same_Month_Previous_Year"})
inflation_series = inflation_series.merge(previous_year, on="Date", how="left")
inflation_series["YoY_Inflation_Rate"] = (
    (inflation_series["CPI"] - inflation_series["CPI_Same_Month_Previous_Year"])
    / inflation_series["CPI_Same_Month_Previous_Year"] * 100
)
inflation_series = inflation_series.dropna(subset=["YoY_Inflation_Rate"]).copy()

if selected_year != "All Years":
    inflation_series = inflation_series[
        inflation_series["Date"].dt.year == int(selected_year)
    ].copy()

if not inflation_series.empty:
    inflation_series["Movement"] = inflation_series["YoY_Inflation_Rate"].apply(
        lambda value: "Inflation" if value > 0 else ("Deflation" if value < 0 else "No year-on-year change")
    )
    movement_colors = {
        "Inflation": "#24563A",
        "Deflation": "#C17D45",
        "No year-on-year change": "#D9B86C",
    }
    inflation_fig = px.bar(
        inflation_series,
        x="Date",
        y="YoY_Inflation_Rate",
        color="Movement",
        color_discrete_map=movement_colors,
        labels={
            "Date": "Month",
            "YoY_Inflation_Rate": "Year-on-year change in CPI (%)",
            "Movement": "CPI movement",
        },
        hover_data={
            "CPI": ":.2f",
            "CPI_Same_Month_Previous_Year": ":.2f",
            "YoY_Inflation_Rate": ":+.2f",
            "Movement": True,
            "Date": "|%B %Y",
        },
    )
    inflation_fig.add_hline(y=0, line_color="#8B927E", line_width=1.2)
    inflation_fig.update_traces(
        marker_line_width=0,
        hovertemplate=(
            "Month: %{x|%B %Y}<br>Year-on-year CPI change: %{y:+.2f}%"
            "<extra></extra>"
        ),
    )
    style_chart(inflation_fig, 390)
    inflation_fig.update_layout(
        barmode="overlay",
        legend_title_text="",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    inflation_fig.update_xaxes(
        dtick="M3" if selected_year == "All Years" else "M1",
        tickformat="%b<br>%Y" if selected_year == "All Years" else "%b",
        title="Month",
    )
    inflation_fig.update_yaxes(title="Year-on-year change in CPI (%)", ticksuffix="%", zeroline=False)
    st.plotly_chart(inflation_fig, use_container_width=True, config={"displayModeBar": False})
    st.caption(
        "Method: (CPI this month − CPI in the same month last year) ÷ CPI in the same month last year × 100. "
        "Positive values indicate year-on-year inflation; negative values indicate year-on-year deflation. "
        "The chart begins in 2019 because 2018 is the first year available for this dataset. "
        "This describes CPI movement and does not establish its causes or directly measure household affordability."
    )
else:
    st.info(
        "No year-on-year comparison is available for this selection. Choose a year from 2019 onward "
        "or select All Years to view the full comparison period."
    )

# ------------------------------------------------------------
# DATASET
# ------------------------------------------------------------
st.markdown("<div class='section-title'>Dataset Explorer</div>", unsafe_allow_html=True)
st.dataframe(filtered_df.sort_values(["Date","Geolocation","Commodity_Name"]), use_container_width=True, height=450, hide_index=True)
st.download_button("Download Filtered Data (CSV)", filtered_df.to_csv(index=False).encode("utf-8"), "Food_CPI_Filtered.csv", "text/csv")
