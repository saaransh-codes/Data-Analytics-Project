"""
app.py  –  Employee Data Analytics Dashboard
=============================================
Run with:
    streamlit run app.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from backend.data_loader import load_raw, load_clean
from backend import analysis as an
from backend import predictions as pred
from backend.chart_builder import (
    build_chart, CHART_TYPES, AGG_FUNCTIONS, COLOR_PALETTES
)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Employee Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f8f9fb; }

    /* KPI cards */
    .kpi-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 18px 20px;
        border-left: 5px solid #4f8ef7;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        margin-bottom: 10px;
    }
    .kpi-label {
        font-size: 12px;
        color: #888;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a2e;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 11px;
        color: #aaa;
        margin-top: 2px;
    }

    /* Section headers */
    .section-header {
        font-size: 20px;
        font-weight: 700;
        color: #1a1a2e;
        border-bottom: 2px solid #4f8ef7;
        padding-bottom: 6px;
        margin: 20px 0 16px 0;
    }

    /* Sidebar */
    .css-1d391kg { background-color: #1a1a2e; }

    /* Insight box */
    .insight-box {
        background: #eef4ff;
        border-left: 4px solid #4f8ef7;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 14px;
        color: #333;
    }

    /* Warning box */
    .warn-box {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 10px 0;
        font-size: 14px;
        color: #555;
    }

    /* Apply Filters button — blue */
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"] {
        background-color: #4f8ef7 !important;
        border-color: #4f8ef7 !important;
        color: #ffffff !important;
    }
    div[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {
        background-color: #3a7be0 !important;
        border-color: #3a7be0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOAD (cached)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def get_data():
    raw   = load_raw()
    clean = load_clean()
    return raw, clean

raw_df, df = get_data()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION & FILTERS
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
    st.markdown("## 👥 Employee Analytics")
    st.markdown("---")

    page = st.radio(
        "📌 Navigate",
        ["🏠 Overview",
         "🔍 Data Quality",
         "📊 Department Analysis",
         "🏙️ City Analysis",
         "💰 Salary Analysis",
         "⭐ Performance Analysis",
         "🏡 Remote Work",
         "📅 Tenure & Age",
         "📈 Correlations",
         "🔎 Employee Explorer",
         "🤖 Predictions",
         "🎨 Chart Builder"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # ── Global filters ──────────────────────────────────────────────────────
    st.markdown("### 🔧 Filters")
    dept_opts = ["All"] + sorted(df["department"].unique().tolist())
    sel_dept  = st.selectbox("Department", dept_opts)

    city_opts = ["All"] + sorted(df["city"].unique().tolist())
    sel_city  = st.selectbox("City", city_opts)

    rating_range = st.slider("Performance Rating", 1, 5, (1, 5))

    salary_range = st.slider(
        "Salary Range (₹)",
        int(df["salary"].min()),
        int(df["salary"].max()),
        (int(df["salary"].min()), int(df["salary"].max())),
        step=1000,
    )

    apply_filters = st.button("✅ Apply Filters", use_container_width=True, type="primary")
    if st.button("🔄 Reset Filters", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("<small style='color:#aaa'>Data: Employees_raw_Data.csv</small>",
                unsafe_allow_html=True)


# ── Apply filters (persisted in session state) ───────────────────────────────
if "fdf" not in st.session_state or apply_filters:
    _fdf = df.copy()
    if sel_dept != "All":
        _fdf = _fdf[_fdf["department"] == sel_dept]
    if sel_city != "All":
        _fdf = _fdf[_fdf["city"] == sel_city]
    _fdf = _fdf[
        (_fdf["performance_rating"] >= rating_range[0]) &
        (_fdf["performance_rating"] <= rating_range[1]) &
        (_fdf["salary"] >= salary_range[0]) &
        (_fdf["salary"] <= salary_range[1])
    ]
    st.session_state["fdf"] = _fdf

fdf = st.session_state["fdf"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPER: KPI card
# ══════════════════════════════════════════════════════════════════════════════

def kpi_card(label: str, value: str, sub: str = "", color: str = "#4f8ef7"):
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)


def section(title: str):
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def insight(text: str):
    st.markdown(f'<div class="insight-box">💡 {text}</div>', unsafe_allow_html=True)


def warn(text: str):
    st.markdown(f'<div class="warn-box">⚠️ {text}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════

if page == "🏠 Overview":
    st.title("🏠 Employee Analytics Dashboard")
    st.markdown("An interactive overview of the workforce — salary, performance, demographics, and more.")
    st.markdown("---")

    kpis = an.kpi_summary(fdf)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card("Total Employees", f"{kpis['total_employees']:,}", color="#4f8ef7")
    with col2:
        kpi_card("Avg Salary", f"₹{kpis['avg_salary']:,.0f}", color="#22c55e")
    with col3:
        kpi_card("Avg Performance", f"{kpis['avg_performance']}/5", color="#f59e0b")
    with col4:
        kpi_card("Remote Workers", f"{kpis['remote_pct']}%", color="#8b5cf6")
    with col5:
        kpi_card("Avg Tenure", f"{kpis['avg_tenure']} yrs", color="#ef4444")

    col6, col7, col8, col9, col10 = st.columns(5)
    with col6:
        kpi_card("Departments", f"{kpis['departments']}", color="#06b6d4")
    with col7:
        kpi_card("Cities", f"{kpis['cities']}", color="#10b981")
    with col8:
        kpi_card("Total Salary Spend", f"₹{kpis['total_salary_spend']:,.0f}", color="#f97316")
    with col9:
        kpi_card("Median Salary", f"₹{kpis['median_salary']:,.0f}", color="#84cc16")
    with col10:
        kpi_card("Avg Age", f"{kpis['avg_age']} yrs", color="#ec4899")

    st.markdown("---")

    # Row: dept headcount + salary band donut
    col_a, col_b = st.columns(2)

    with col_a:
        section("👥 Headcount by Department")
        dc = fdf["department"].value_counts().reset_index()
        dc.columns = ["Department", "Count"]
        fig = px.bar(dc, x="Department", y="Count",
                     color="Department",
                     text="Count",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, height=350,
                          plot_bgcolor="white", paper_bgcolor="white",
                          xaxis_title="", yaxis_title="Employees")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("💰 Salary Band Distribution")
        sbd = an.salary_band_dist(fdf)
        fig2 = px.pie(sbd, names="band", values="count",
                      hole=0.45,
                      color_discrete_sequence=["#ef4444", "#f59e0b", "#22c55e"])
        fig2.update_traces(textinfo="percent+label", pull=[0.03, 0.03, 0.03])
        fig2.update_layout(height=350, paper_bgcolor="white",
                           legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig2, use_container_width=True)

    # Row: performance dist + age groups
    col_c, col_d = st.columns(2)
    with col_c:
        section("⭐ Performance Rating Distribution")
        pd_data = an.performance_dist(fdf)
        fig3 = px.bar(pd_data, x="label", y="count",
                      color="label", text="count",
                      color_discrete_sequence=["#ef4444","#f97316","#f59e0b","#86efac","#22c55e"])
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False, height=320,
                           plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Rating", yaxis_title="Employees")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        section("🎂 Age Group Distribution")
        ag_data = an.age_group_dist(fdf)
        fig4 = px.bar(ag_data, x="age_group", y="count",
                      color="age_group", text="count",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_traces(textposition="outside")
        fig4.update_layout(showlegend=False, height=320,
                           plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Age Group", yaxis_title="Employees")
        st.plotly_chart(fig4, use_container_width=True)

    insight(f"The workforce is {kpis['total_employees']} employees across "
            f"{kpis['departments']} departments and {kpis['cities']} cities. "
            f"Average salary is ₹{kpis['avg_salary']:,.0f} with a "
            f"{kpis['remote_pct']}% remote work rate.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — DATA QUALITY
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔍 Data Quality":
    st.title("🔍 Data Quality Report")
    st.markdown("Audit of the raw dataset: missing values, inconsistencies, and cleaning summary.")
    st.markdown("---")

    section("📂 Raw Dataset (First 20 Rows)")
    st.dataframe(raw_df.head(20), use_container_width=True)

    st.markdown("---")
    section("🚨 Missing Value Analysis")

    missing = raw_df.isnull().sum().reset_index()
    missing.columns = ["Column", "Missing Count"]
    missing["Missing %"] = (missing["Missing Count"] / len(raw_df) * 100).round(2)
    missing["Status"] = missing["Missing Count"].apply(
        lambda x: "✅ Clean" if x == 0 else ("⚠️ Low" if x < 10 else "❌ High")
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(missing, use_container_width=True, hide_index=True)
    with col2:
        fig = px.bar(missing[missing["Missing Count"] > 0],
                     x="Column", y="Missing Count",
                     color="Missing %",
                     text="Missing %",
                     color_continuous_scale="Reds",
                     title="Missing Values per Column")
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    section("🔀 remote_work Unique Values (Before Cleaning)")
    rv = raw_df["remote_work"].value_counts(dropna=False).reset_index()
    rv.columns = ["Value", "Count"]
    st.dataframe(rv, use_container_width=True, hide_index=True)
    warn("remote_work has mixed case (yes/Yes/YES/NO/No) and 'nan' strings — all normalised to True/False.")

    st.markdown("---")
    section("✅ Cleaned Dataset (First 20 Rows)")
    display_cols = ["emp_name", "department", "join_date", "salary", "age",
                    "performance_rating", "city", "remote_work",
                    "tenure_years", "age_group", "salary_band"]
    st.dataframe(df[display_cols].head(20), use_container_width=True)

    st.markdown("---")
    section("📋 Cleaning Summary")
    summary = {
        "Action": [
            "Normalised remote_work values",
            "Imputed missing department",
            "Imputed missing salary",
            "Imputed missing age",
            "Imputed missing performance_rating",
            "Derived tenure_years",
            "Derived age_group",
            "Derived salary_band",
        ],
        "Detail": [
            "yes/Yes/YES/NO/nan → True/False boolean",
            "Blank → 'Unknown'",
            "Department median (fallback: overall median)",
            "Overall median",
            "Department median rounded to nearest int",
            "(Today − join_date) / 365.25",
            "20–29 / 30–39 / 40–49 / 50+",
            "Low <40k / Mid 40k–75k / High >75k",
        ],
    }
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — DEPARTMENT ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📊 Department Analysis":
    st.title("📊 Department Analysis")
    st.markdown("Headcount, salary, performance and remote work — broken down by department.")
    st.markdown("---")

    ds = an.dept_summary(fdf)

    section("📋 Department Summary Table")
    display = ds[["department", "headcount", "avg_salary", "total_salary",
                  "avg_age", "avg_tenure", "avg_rating", "remote_pct"]].copy()
    display.columns = ["Department", "Headcount", "Avg Salary (₹)",
                       "Total Salary Spend (₹)", "Avg Age",
                       "Avg Tenure (yrs)", "Avg Rating", "Remote %"]
    st.dataframe(
        display.style
               .format({"Avg Salary (₹)": "₹{:,.0f}",
                        "Total Salary Spend (₹)": "₹{:,.0f}",
                        "Avg Rating": "{:.2f}",
                        "Remote %": "{:.1f}%"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        section("👥 Headcount by Department")
        fig = px.bar(ds, x="department", y="headcount",
                     color="department", text="headcount",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="white",
                          paper_bgcolor="white", xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("💰 Avg Salary by Department")
        fig2 = px.bar(ds.sort_values("avg_salary", ascending=True),
                      x="avg_salary", y="department", orientation="h",
                      color="avg_salary", text="avg_salary",
                      color_continuous_scale="Viridis")
        fig2.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="Avg Salary (₹)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        section("⭐ Avg Performance Rating by Department")
        fig3 = px.bar(ds.sort_values("avg_rating", ascending=False),
                      x="department", y="avg_rating",
                      color="avg_rating", text="avg_rating",
                      color_continuous_scale="RdYlGn",
                      range_y=[0, 5.5])
        fig3.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="", yaxis_title="Avg Rating")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        section("🏡 Remote Work % by Department")
        fig4 = px.bar(ds.sort_values("remote_pct", ascending=False),
                      x="department", y="remote_pct",
                      color="remote_pct", text="remote_pct",
                      color_continuous_scale="Purples")
        fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="", yaxis_title="Remote %")
        st.plotly_chart(fig4, use_container_width=True)

    top_dept = ds.loc[ds["headcount"].idxmax(), "department"]
    best_pay = ds.loc[ds["avg_salary"].idxmax(), "department"]
    insight(f"**{top_dept}** has the most employees. "
            f"**{best_pay}** pays the highest average salary.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — CITY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🏙️ City Analysis":
    st.title("🏙️ City Analysis")
    st.markdown("Distribution of employees, salaries, and performance across Indian cities.")
    st.markdown("---")

    cs = an.city_summary(fdf)

    section("📋 City Summary Table")
    disp = cs.copy()
    disp.columns = ["City", "Headcount", "Avg Salary (₹)", "Avg Rating", "Remote %"]
    st.dataframe(
        disp.style
            .format({"Avg Salary (₹)": "₹{:,.0f}",
                     "Avg Rating": "{:.2f}",
                     "Remote %": "{:.1f}%"}),
        use_container_width=True, hide_index=True,
    )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        section("👥 Headcount by City")
        fig = px.pie(cs, names="city", values="headcount",
                     hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_traces(textinfo="percent+label")
        fig.update_layout(height=380, paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section("💰 Avg Salary by City")
        fig2 = px.bar(cs.sort_values("avg_salary", ascending=True),
                      x="avg_salary", y="city", orientation="h",
                      color="avg_salary", text="avg_salary",
                      color_continuous_scale="teal")
        fig2.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="Avg Salary (₹)", yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    section("🌐 Remote Work % by City")
    fig3 = px.bar(cs.sort_values("remote_pct", ascending=False),
                  x="city", y="remote_pct",
                  color="remote_pct", text="remote_pct",
                  color_continuous_scale="Purples")
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       coloraxis_showscale=False,
                       xaxis_title="City", yaxis_title="Remote %")
    st.plotly_chart(fig3, use_container_width=True)

    top_city = cs.loc[cs["headcount"].idxmax(), "city"]
    insight(f"**{top_city}** has the highest number of employees.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — SALARY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "💰 Salary Analysis":
    st.title("💰 Salary Analysis")
    st.markdown("Deep-dive into salary distributions, bands, and departmental comparison.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Min Salary", f"₹{fdf['salary'].min():,.0f}", color="#ef4444")
    with col2:
        kpi_card("Max Salary", f"₹{fdf['salary'].max():,.0f}", color="#22c55e")
    with col3:
        kpi_card("Mean Salary", f"₹{fdf['salary'].mean():,.0f}", color="#4f8ef7")
    with col4:
        kpi_card("Std Deviation", f"₹{fdf['salary'].std():,.0f}", color="#f59e0b")

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        section("📊 Salary Distribution (Histogram)")
        fig = px.histogram(fdf, x="salary", nbins=30,
                           color_discrete_sequence=["#4f8ef7"],
                           marginal="box")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          xaxis_title="Salary (₹)", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("💰 Salary Band Distribution")
        sbd = an.salary_band_dist(fdf)
        fig2 = px.pie(sbd, names="band", values="count", hole=0.45,
                      color_discrete_sequence=["#ef4444", "#f59e0b", "#22c55e"])
        fig2.update_traces(textinfo="percent+label+value")
        fig2.update_layout(paper_bgcolor="white",
                           legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig2, use_container_width=True)

    section("📦 Salary Box Plot by Department")
    fig3 = px.box(fdf, x="department", y="salary",
                  color="department", points="outliers",
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       showlegend=False, xaxis_title="", yaxis_title="Salary (₹)")
    st.plotly_chart(fig3, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        section("💰 Avg Salary by Salary Band & Department")
        fig4 = px.bar(fdf.groupby(["department", "salary_band"])["salary"]
                      .mean().reset_index(),
                      x="department", y="salary", color="salary_band",
                      barmode="group",
                      color_discrete_sequence=["#ef4444", "#f59e0b", "#22c55e"])
        fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="", yaxis_title="Avg Salary (₹)")
        st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        section("📉 Salary vs Performance Rating")
        fig5 = px.scatter(fdf, x="performance_rating", y="salary",
                          color="department", size="tenure_years",
                          hover_data=["emp_name", "city"],
                          color_discrete_sequence=px.colors.qualitative.Vivid)
        fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Performance Rating", yaxis_title="Salary (₹)")
        st.plotly_chart(fig5, use_container_width=True)

    insight("Most employees fall in the Mid salary band (₹40k–₹75k). "
            "Engineering and HR departments show the highest salary spread.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — PERFORMANCE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "⭐ Performance Analysis":
    st.title("⭐ Performance Analysis")
    st.markdown("Explore performance ratings across departments, cities, age groups and salary bands.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Avg Rating (Overall)", f"{fdf['performance_rating'].mean():.2f} / 5",
                 color="#f59e0b")
    with col2:
        top_pct = (fdf["performance_rating"] == 5).mean() * 100
        kpi_card("Top Performers (5)", f"{top_pct:.1f}%", color="#22c55e")
    with col3:
        low_pct = (fdf["performance_rating"] == 1).mean() * 100
        kpi_card("Low Performers (1)", f"{low_pct:.1f}%", color="#ef4444")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        section("⭐ Rating Distribution")
        pd_data = an.performance_dist(fdf)
        fig = px.bar(pd_data, x="label", y="count", color="label", text="count",
                     color_discrete_sequence=["#ef4444","#f97316","#f59e0b","#86efac","#22c55e"])
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                          xaxis_title="Rating", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("📊 Avg Rating by Department")
        ds = an.dept_summary(fdf)
        fig2 = px.bar(ds.sort_values("avg_rating", ascending=False),
                      x="department", y="avg_rating",
                      color="avg_rating", text="avg_rating",
                      color_continuous_scale="RdYlGn", range_y=[0, 5.5])
        fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="", yaxis_title="Avg Rating")
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        section("🎂 Avg Rating by Age Group")
        ag_r = fdf.groupby("age_group")["performance_rating"].mean().reset_index()
        ag_r.columns = ["age_group", "avg_rating"]
        fig3 = px.bar(ag_r, x="age_group", y="avg_rating",
                      color="avg_rating", text="avg_rating",
                      color_continuous_scale="YlOrRd", range_y=[0, 5.5])
        fig3.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="Age Group", yaxis_title="Avg Rating")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        section("💰 Avg Rating by Salary Band")
        sb_r = fdf.groupby("salary_band")["performance_rating"].mean().reset_index()
        sb_r.columns = ["band", "avg_rating"]
        order = ["Low (<40k)", "Mid (40k–75k)", "High (>75k)"]
        sb_r["band"] = pd.Categorical(sb_r["band"], categories=order, ordered=True)
        sb_r = sb_r.sort_values("band")
        fig4 = px.bar(sb_r, x="band", y="avg_rating",
                      color="avg_rating", text="avg_rating",
                      color_continuous_scale="Greens", range_y=[0, 5.5])
        fig4.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="Salary Band", yaxis_title="Avg Rating")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("---")
    section("🏆 Top Performers (Rating = 5)")
    top = an.top_performers(fdf)
    if not top.empty:
        st.dataframe(top, use_container_width=True, hide_index=True)
    else:
        warn("No employees with rating 5 in current filter selection.")

    section("📉 Low Performers (Rating = 1)")
    low = an.bottom_performers(fdf)
    if not low.empty:
        st.dataframe(low, use_container_width=True, hide_index=True)
    else:
        st.info("No employees with rating 1 in current filter selection.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — REMOTE WORK
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🏡 Remote Work":
    st.title("🏡 Remote Work Analysis")
    st.markdown("How remote work is distributed across departments, cities and salary bands.")
    st.markdown("---")

    total = len(fdf)
    remote_count = fdf["remote_work"].sum()
    onsite_count = total - remote_count

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Remote Employees", f"{int(remote_count)}", color="#8b5cf6")
    with col2:
        kpi_card("On-Site Employees", f"{int(onsite_count)}", color="#4f8ef7")
    with col3:
        kpi_card("Remote Rate", f"{remote_count/total*100:.1f}%", color="#22c55e")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        section("🏠 Remote vs On-Site Overview")
        rw_pie = pd.DataFrame({"Mode": ["Remote", "On-Site"],
                               "Count": [int(remote_count), int(onsite_count)]})
        fig = px.pie(rw_pie, names="Mode", values="Count", hole=0.5,
                     color_discrete_sequence=["#8b5cf6", "#4f8ef7"])
        fig.update_traces(textinfo="percent+label+value")
        fig.update_layout(paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("📊 Remote % by Department")
        rd = an.remote_by_department(fdf)
        fig2 = px.bar(rd, x="department", y="remote_pct",
                      color="remote_pct", text="remote_pct",
                      color_continuous_scale="Purples")
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="", yaxis_title="Remote %")
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        section("🏙️ Remote % by City")
        city_rw = fdf.groupby("city")["remote_work"].mean().mul(100).round(1).reset_index()
        city_rw.columns = ["city", "remote_pct"]
        fig3 = px.bar(city_rw.sort_values("remote_pct", ascending=False),
                      x="city", y="remote_pct",
                      color="remote_pct", text="remote_pct",
                      color_continuous_scale="Teal")
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        section("💰 Avg Salary: Remote vs On-Site")
        rw_sal = fdf.groupby("remote_work")["salary"].mean().reset_index()
        rw_sal["mode"] = rw_sal["remote_work"].map({True: "Remote", False: "On-Site"})
        fig4 = px.bar(rw_sal, x="mode", y="salary",
                      color="mode", text="salary",
                      color_discrete_map={"Remote": "#8b5cf6", "On-Site": "#4f8ef7"})
        fig4.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
        fig4.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="", yaxis_title="Avg Salary (₹)")
        st.plotly_chart(fig4, use_container_width=True)

    insight("Remote work is more common in departments like Engineering and Sales. "
            "Remote and on-site salary averages help benchmark compensation equity.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — TENURE & AGE
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📅 Tenure & Age":
    st.title("📅 Tenure & Age Analysis")
    st.markdown("Employee age distribution, tenure, and how they relate to salary and performance.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Avg Age", f"{fdf['age'].mean():.1f} yrs", color="#ec4899")
    with col2:
        kpi_card("Avg Tenure", f"{fdf['tenure_years'].mean():.1f} yrs", color="#f97316")
    with col3:
        kpi_card("Longest Serving", f"{fdf['tenure_years'].max():.1f} yrs", color="#4f8ef7")

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        section("🎂 Age Distribution")
        fig = px.histogram(fdf, x="age", nbins=20,
                           color_discrete_sequence=["#ec4899"], marginal="violin")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          xaxis_title="Age", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        section("📅 Tenure Distribution")
        fig2 = px.histogram(fdf, x="tenure_years", nbins=20,
                            color_discrete_sequence=["#f97316"], marginal="violin")
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Tenure (Years)", yaxis_title="Count")
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        section("🏢 Avg Tenure by Department")
        tbd = an.tenure_by_department(fdf)
        fig3 = px.bar(tbd, x="department", y="avg_tenure",
                      color="avg_tenure", text="avg_tenure",
                      color_continuous_scale="Oranges")
        fig3.update_traces(texttemplate="%{text:.1f} yrs", textposition="outside")
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           coloraxis_showscale=False,
                           xaxis_title="", yaxis_title="Avg Tenure (yrs)")
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        section("💰 Salary vs Tenure (Scatter)")
        fig4 = px.scatter(fdf, x="tenure_years", y="salary",
                          color="department", size="age",
                          hover_data=["emp_name", "performance_rating"],
                          color_discrete_sequence=px.colors.qualitative.Vivid)
        fig4.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Tenure (Years)", yaxis_title="Salary (₹)")
        st.plotly_chart(fig4, use_container_width=True)

    section("🎂 Age Group vs Avg Salary")
    ag_sal = fdf.groupby("age_group")["salary"].mean().reset_index()
    ag_sal.columns = ["age_group", "avg_salary"]
    order = ["20–29", "30–39", "40–49", "50+"]
    ag_sal["age_group"] = pd.Categorical(ag_sal["age_group"], categories=order, ordered=True)
    ag_sal = ag_sal.sort_values("age_group")
    fig5 = px.bar(ag_sal, x="age_group", y="avg_salary",
                  color="avg_salary", text="avg_salary",
                  color_continuous_scale="Blues")
    fig5.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig5.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                       coloraxis_showscale=False,
                       xaxis_title="Age Group", yaxis_title="Avg Salary (₹)")
    st.plotly_chart(fig5, use_container_width=True)

    insight("Employees in the 40–49 age group tend to have the highest salaries. "
            "Tenure grows steadily with department seniority.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "📈 Correlations":
    st.title("📈 Correlations & Relationships")
    st.markdown("Statistical correlations between numeric workforce metrics.")
    st.markdown("---")

    corr = an.numeric_corr(fdf)

    col1, col2 = st.columns([1, 2])
    with col1:
        section("🔢 Correlation Matrix")
        st.dataframe(corr.style.format("{:.2f}"),
                     use_container_width=True)

    with col2:
        section("🌡️ Heatmap")
        fig = px.imshow(corr, text_auto=True, aspect="auto",
                        color_continuous_scale="RdYlGn",
                        zmin=-1, zmax=1)
        fig.update_layout(paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        section("📊 Age vs Salary")
        fig2 = px.scatter(fdf, x="age", y="salary",
                          color="department", trendline="ols",
                          hover_data=["emp_name"],
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Age", yaxis_title="Salary (₹)")
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        section("📊 Tenure vs Performance Rating")
        fig3 = px.scatter(fdf, x="tenure_years", y="performance_rating",
                          color="department", trendline="ols",
                          hover_data=["emp_name"],
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           xaxis_title="Tenure (yrs)", yaxis_title="Performance Rating")
        st.plotly_chart(fig3, use_container_width=True)

    insight("Correlation analysis helps identify if salary increases with age/tenure "
            "and whether performance is independent of compensation level.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 10 — EMPLOYEE EXPLORER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🔎 Employee Explorer":
    st.title("🔎 Employee Explorer")
    st.markdown("Search, filter, and export individual employee records.")
    st.markdown("---")

    search = st.text_input("🔍 Search employee name", "")
    show_df = fdf.copy()
    if search:
        show_df = show_df[show_df["emp_name"].str.contains(search, case=False, na=False)]

    cols_display = ["emp_name", "department", "city", "join_date", "salary",
                    "age", "performance_rating", "remote_work",
                    "tenure_years", "age_group", "salary_band"]

    st.markdown(f"**{len(show_df)} employee(s) found**")
    st.dataframe(
        show_df[cols_display].style
               .format({"salary": "₹{:,.2f}",
                        "tenure_years": "{:.1f} yrs"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    section("📥 Download Filtered Data")
    csv_out = show_df[cols_display].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv_out,
        file_name="filtered_employees.csv",
        mime="text/csv",
    )

    if len(show_df) > 0:
        st.markdown("---")
        section("📊 Quick Stats on Filtered Set")
        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1:
            kpi_card("Employees", str(len(show_df)), color="#4f8ef7")
        with qc2:
            kpi_card("Avg Salary", f"₹{show_df['salary'].mean():,.0f}", color="#22c55e")
        with qc3:
            kpi_card("Avg Rating",
                     f"{show_df['performance_rating'].mean():.2f}", color="#f59e0b")
        with qc4:
            kpi_card("Remote %",
                     f"{show_df['remote_work'].mean()*100:.1f}%", color="#8b5cf6")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 11 — PREDICTIONS
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🤖 Predictions":
    st.title("🤖 ML Predictions & Attrition Risk")
    st.markdown(
        "Three models trained on your employee data: "
        "**Salary Predictor**, **Performance Classifier**, and **Attrition Risk Scorer**."
    )
    st.markdown("---")

    # ── Train models (cached) ─────────────────────────────────────────────────
    @st.cache_resource
    def get_models(_df):
        sal_pipe,  sal_metrics,  sal_imp  = pred.train_salary_model(_df)
        perf_pipe, perf_metrics, perf_imp = pred.train_performance_model(_df)
        return sal_pipe, sal_metrics, sal_imp, perf_pipe, perf_metrics, perf_imp

    sal_pipe, sal_metrics, sal_imp, perf_pipe, perf_metrics, perf_imp = get_models(df)

    tab1, tab2, tab3 = st.tabs(
        ["💰 Salary Predictor", "⭐ Performance Classifier", "🔴 Attrition Risk"]
    )

    # ── TAB 1: Salary Predictor ───────────────────────────────────────────────
    with tab1:
        st.markdown("### 💰 Predict an Employee's Salary")
        st.markdown("Fill in the employee details and the Ridge Regression model will estimate salary.")
        st.markdown("---")

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            kpi_card("MAE (Mean Abs Error)", f"₹{sal_metrics['mae']:,.0f}", color="#4f8ef7")
        with col_m2:
            kpi_card("R² Score (Training)", f"{sal_metrics['r2']:.4f}", color="#22c55e")
        with col_m3:
            kpi_card("5-Fold CV R²", f"{sal_metrics['cv_r2_mean']:.4f} ± {sal_metrics['cv_r2_std']:.4f}", color="#f59e0b")

        st.markdown("---")
        col_in1, col_in2 = st.columns([1, 1])
        with col_in1:
            st.markdown("#### 🔢 Input Features")
            s_age    = st.slider("Age", 20, 65, 35, key="s_age")
            s_tenure = st.slider("Tenure (years)", 0.0, 10.0, 3.0, step=0.5, key="s_tenure")
            s_rating = st.selectbox("Performance Rating", [1, 2, 3, 4, 5], index=2, key="s_rating")
            s_dept   = st.selectbox("Department", sorted(df["department"].unique()), key="s_dept")
            s_city   = st.selectbox("City", sorted(df["city"].unique()), key="s_city")

            if st.button("🔮 Predict Salary", use_container_width=True, type="primary"):
                predicted = pred.predict_salary(sal_pipe, s_age, s_tenure, s_rating, s_dept, s_city)
                st.markdown(f"""
                <div class="kpi-card" style="border-left-color:#22c55e; margin-top:16px">
                    <div class="kpi-label">Predicted Salary</div>
                    <div class="kpi-value">₹{predicted:,.2f}</div>
                    <div class="kpi-sub">{s_dept} · {s_city} · Rating {s_rating} · Age {s_age}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_in2:
            st.markdown("#### 📊 Top Feature Importances (|Coefficient|)")
            top_feats = sal_imp.head(12).sort_values("abs_coef")
            fig_imp = px.bar(top_feats, x="abs_coef", y="feature", orientation="h",
                             color="abs_coef", color_continuous_scale="Blues",
                             text="abs_coef")
            fig_imp.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            fig_imp.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                  coloraxis_showscale=False, height=420,
                                  xaxis_title="|Coefficient|", yaxis_title="")
            st.plotly_chart(fig_imp, use_container_width=True)

    # ── TAB 2: Performance Classifier ─────────────────────────────────────────
    with tab2:
        st.markdown("### ⭐ Predict Performance Rating")
        st.markdown("Random Forest classifier predicts the performance rating (1–5) from employee profile.")
        st.markdown("---")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            kpi_card("Training Accuracy", f"{perf_metrics['train_accuracy']*100:.1f}%", color="#4f8ef7")
        with col_m2:
            kpi_card("5-Fold CV Accuracy", f"{perf_metrics['cv_accuracy_mean']*100:.1f}% ± {perf_metrics['cv_accuracy_std']*100:.1f}%", color="#22c55e")

        st.markdown("---")
        col_in3, col_in4 = st.columns([1, 1])
        with col_in3:
            st.markdown("#### 🔢 Input Features")
            p_age    = st.slider("Age", 20, 65, 35, key="p_age")
            p_tenure = st.slider("Tenure (years)", 0.0, 10.0, 3.0, step=0.5, key="p_tenure")
            p_salary = st.number_input("Salary (₹)", min_value=10000, max_value=200000,
                                       value=55000, step=1000, key="p_salary")
            p_dept   = st.selectbox("Department", sorted(df["department"].unique()), key="p_dept")
            p_city   = st.selectbox("City", sorted(df["city"].unique()), key="p_city")

            if st.button("🔮 Predict Performance", use_container_width=True, type="primary"):
                result = pred.predict_performance(perf_pipe, p_age, p_tenure, p_salary, p_dept, p_city)
                r = result["predicted_rating"]
                labels = {1: "Poor", 2: "Below Avg", 3: "Average", 4: "Good", 5: "Excellent"}
                colors_map = {1: "#ef4444", 2: "#f97316", 3: "#f59e0b", 4: "#22c55e", 5: "#16a34a"}
                st.markdown(f"""
                <div class="kpi-card" style="border-left-color:{colors_map[r]}; margin-top:16px">
                    <div class="kpi-label">Predicted Performance Rating</div>
                    <div class="kpi-value">{r} – {labels[r]}</div>
                    <div class="kpi-sub">{p_dept} · {p_city} · Salary ₹{p_salary:,}</div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("##### Probability per Rating")
                prob_df = pd.DataFrame({
                    "Rating": [f"{k} – {labels[k]}" for k in sorted(result["probabilities"])],
                    "Probability": [result["probabilities"][k] for k in sorted(result["probabilities"])],
                })
                fig_prob = px.bar(prob_df, x="Rating", y="Probability",
                                  color="Probability",
                                  color_continuous_scale="RdYlGn",
                                  text="Probability",
                                  range_y=[0, 1])
                fig_prob.update_traces(texttemplate="%{text:.1%}", textposition="outside")
                fig_prob.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                       coloraxis_showscale=False, height=300)
                st.plotly_chart(fig_prob, use_container_width=True)

        with col_in4:
            st.markdown("#### 📊 Feature Importances (Random Forest)")
            top_p = perf_imp.head(12).sort_values("importance")
            fig_pimp = px.bar(top_p, x="importance", y="feature", orientation="h",
                              color="importance", color_continuous_scale="Purples",
                              text="importance")
            fig_pimp.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            fig_pimp.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                   coloraxis_showscale=False, height=420,
                                   xaxis_title="Importance", yaxis_title="")
            st.plotly_chart(fig_pimp, use_container_width=True)

    # ── TAB 3: Attrition Risk ─────────────────────────────────────────────────
    with tab3:
        st.markdown("### 🔴 Attrition Risk Scoring")
        st.markdown(
            "A rule-based heuristic scores every employee 0–100 based on "
            "performance, salary, tenure, remote status, and age. "
            "Scores ≥ 60 = High Risk · 35–59 = Medium · < 35 = Low."
        )
        st.markdown("---")

        # Score entire dataset
        risk_df = pred.compute_attrition_for_df(fdf)
        high    = (risk_df["attrition_label"].str.startswith("🔴")).sum()
        medium  = (risk_df["attrition_label"].str.startswith("🟡")).sum()
        low     = (risk_df["attrition_label"].str.startswith("🟢")).sum()

        c1, c2, c3 = st.columns(3)
        with c1: kpi_card("🔴 High Risk",   str(high),   color="#ef4444")
        with c2: kpi_card("🟡 Medium Risk", str(medium), color="#f59e0b")
        with c3: kpi_card("🟢 Low Risk",    str(low),    color="#22c55e")

        st.markdown("---")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            section("🔴 Risk Distribution")
            risk_counts = risk_df["attrition_label"].value_counts().reset_index()
            risk_counts.columns = ["Risk", "Count"]
            fig_risk = px.pie(risk_counts, names="Risk", values="Count", hole=0.45,
                              color_discrete_sequence=["#ef4444", "#f59e0b", "#22c55e"])
            fig_risk.update_traces(textinfo="percent+label+value")
            fig_risk.update_layout(paper_bgcolor="white", height=340)
            st.plotly_chart(fig_risk, use_container_width=True)

        with col_r2:
            section("📊 Avg Risk Score by Department")
            dept_risk = risk_df.groupby("department")["attrition_score"].mean().round(1).reset_index()
            fig_dr = px.bar(dept_risk.sort_values("attrition_score", ascending=True),
                            x="attrition_score", y="department", orientation="h",
                            color="attrition_score",
                            color_continuous_scale="RdYlGn_r", text="attrition_score")
            fig_dr.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig_dr.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                 coloraxis_showscale=False, height=340,
                                 xaxis_title="Avg Risk Score", yaxis_title="")
            st.plotly_chart(fig_dr, use_container_width=True)

        section("📋 Full Attrition Risk Table")
        risk_display = risk_df[["emp_name", "department", "city", "salary",
                                 "age", "tenure_years", "performance_rating",
                                 "remote_work", "attrition_score", "attrition_label"]]
        st.dataframe(
            risk_display.sort_values("attrition_score", ascending=False)
                        .reset_index(drop=True),
            use_container_width=True, hide_index=True,
        )

        st.markdown("---")
        section("🔮 Score a Single Employee")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            a_age    = st.slider("Age",              20, 65, 32, key="a_age")
            a_tenure = st.slider("Tenure (yrs)",     0.0, 10.0, 1.5, step=0.5, key="a_tenure")
        with sc2:
            a_salary = st.number_input("Salary (₹)", 10000, 200000, 35000, step=1000, key="a_salary")
            a_rating = st.selectbox("Performance Rating", [1, 2, 3, 4, 5], index=1, key="a_rating")
        with sc3:
            a_remote = st.checkbox("Remote Worker?", value=False, key="a_remote")
            st.markdown("")

        if st.button("🔮 Compute Risk", use_container_width=True, type="primary"):
            risk = pred.attrition_risk_score(a_age, a_tenure, a_salary, a_rating, a_remote)
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color:{risk['color']}; margin-top:12px">
                <div class="kpi-label">Attrition Risk Score</div>
                <div class="kpi-value">{risk['score']} / 100 &nbsp; {risk['label']}</div>
                <div class="kpi-sub">Age {a_age} · Tenure {a_tenure} yrs · ₹{a_salary:,} · Rating {a_rating} · {'Remote' if a_remote else 'On-Site'}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 12 — CHART BUILDER
# ══════════════════════════════════════════════════════════════════════════════

elif page == "🎨 Chart Builder":
    st.title("🎨 Custom Chart Builder")
    st.markdown(
        "Build any chart from the employee dataset — pick your axes, "
        "aggregation, chart type, and colour palette. No code needed."
    )
    st.markdown("---")

    all_cols     = df.columns.tolist()
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols     = df.select_dtypes(exclude="number").columns.tolist()

    with st.expander("⚙️ Chart Configuration", expanded=True):
        cfg1, cfg2, cfg3 = st.columns(3)
        with cfg1:
            cb_type    = st.selectbox("Chart Type",  CHART_TYPES, key="cb_type")
            cb_palette = st.selectbox("Colour Palette", list(COLOR_PALETTES.keys()), key="cb_palette")
        with cfg2:
            cb_x       = st.selectbox("X-Axis / Category", all_cols, key="cb_x")
            cb_y_opts  = [None] + numeric_cols
            cb_y       = st.selectbox("Y-Axis / Value", cb_y_opts,
                                      index=cb_y_opts.index("salary") if "salary" in cb_y_opts else 0,
                                      key="cb_y")
        with cfg3:
            cb_color   = st.selectbox("Colour Group (optional)", [None] + cat_cols, key="cb_color")
            cb_agg     = st.selectbox("Aggregation",  list(AGG_FUNCTIONS.keys()), key="cb_agg")

        cfg4, cfg5 = st.columns(2)
        with cfg4:
            cb_title   = st.text_input("Chart Title (leave blank for auto)", "", key="cb_title")
        with cfg5:
            cb_height  = st.slider("Chart Height (px)", 300, 800, 450, step=50, key="cb_height")
        cb_labels  = st.checkbox("Show value labels", value=True, key="cb_labels")

    if st.button("🎨 Generate Chart", type="primary", use_container_width=True):
        with st.spinner("Building chart…"):
            try:
                fig = build_chart(
                    df=fdf,
                    chart_type=cb_type,
                    x_col=cb_x,
                    y_col=cb_y,
                    color_col=cb_color,
                    agg_func=AGG_FUNCTIONS[cb_agg],
                    palette=cb_palette,
                    title=cb_title or "",
                    show_labels=cb_labels,
                    height=cb_height,
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Could not build chart: {e}")

    st.markdown("---")
    section("💡 Chart Type Guide")
    guide = pd.DataFrame({
        "Chart Type": ["Bar", "Line", "Area", "Scatter", "Pie / Donut",
                       "Box", "Histogram", "Treemap"],
        "Best For": [
            "Comparing categories (dept, city, age group)",
            "Trends over a sorted/numeric axis",
            "Cumulative trends with filled area",
            "Relationship between two numeric columns",
            "Part-to-whole breakdown of a category",
            "Distribution spread & outliers per group",
            "Frequency distribution of a single numeric column",
            "Hierarchical proportions across two categories",
        ],
        "Needs Y-Axis?": ["Yes", "Yes", "Yes", "Yes", "Optional", "Yes", "No", "Optional"],
    })
    st.dataframe(guide, use_container_width=True, hide_index=True)

    section("📊 Quick Presets")
    preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)

    with preset_col1:
        if st.button("Salary by Department (Bar)", use_container_width=True):
            fig = build_chart(fdf, "Bar", "department", "salary", None, "mean",
                              "Pastel", "Avg Salary by Department")
            st.plotly_chart(fig, use_container_width=True)

    with preset_col2:
        if st.button("Age vs Salary (Scatter)", use_container_width=True):
            fig = build_chart(fdf, "Scatter", "age", "salary", "department", "mean",
                              "Vivid", "Age vs Salary")
            st.plotly_chart(fig, use_container_width=True)

    with preset_col3:
        if st.button("Department Headcount (Pie)", use_container_width=True):
            fig = build_chart(fdf, "Pie / Donut", "department", None, None, "count",
                              "Set2", "Headcount by Department")
            st.plotly_chart(fig, use_container_width=True)

    with preset_col4:
        if st.button("Rating Distribution (Box)", use_container_width=True):
            fig = build_chart(fdf, "Box", "department", "performance_rating", None, "mean",
                              "Bold", "Performance Rating by Department")
            st.plotly_chart(fig, use_container_width=True)
