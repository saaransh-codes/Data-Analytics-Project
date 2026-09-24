"""
generate_diagrams.py
====================
Generates all diagram PNG images used in the project report.
Run with:   python generate_diagrams.py
Output:     employee_analytics/report_images/*.png
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as FancyBbox
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.gridspec import GridSpec

OUT = os.path.join(os.path.dirname(__file__), "report_images")
os.makedirs(OUT, exist_ok=True)

# ── colour palette ────────────────────────────────────────────────────────────
C = {
    "blue":    "#4f8ef7",
    "green":   "#22c55e",
    "amber":   "#f59e0b",
    "red":     "#ef4444",
    "purple":  "#8b5cf6",
    "teal":    "#14b8a6",
    "orange":  "#f97316",
    "pink":    "#ec4899",
    "dark":    "#1a1a2e",
    "light":   "#f8f9fb",
    "border":  "#e5e7eb",
    "muted":   "#888888",
    "white":   "#ffffff",
}

def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  saved → {path}")

# ═════════════════════════════════════════════════════════════════════════════
# 1. PROJECT ARCHITECTURE DIAGRAM
# ═════════════════════════════════════════════════════════════════════════════
def fig_architecture():
    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor(C["light"])
    ax.set_facecolor(C["light"])
    ax.set_xlim(0, 13); ax.set_ylim(0, 7)
    ax.axis("off")
    ax.set_title("Project Architecture", fontsize=16, fontweight="bold", color=C["dark"], pad=12)

    def box(x, y, w, h, label, sublabel="", color=C["blue"], fontsize=10):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                              linewidth=1.5, edgecolor=color, facecolor=color+"22")
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2+(0.15 if sublabel else 0), label, ha="center", va="center",
                fontsize=fontsize, fontweight="bold", color=color)
        if sublabel:
            ax.text(x+w/2, y+h/2-0.25, sublabel, ha="center", va="center",
                    fontsize=8, color=C["muted"])

    def arrow(x1, y1, x2, y2, color=C["muted"]):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

    # Layer labels
    for y_pos, label, col in [(5.8, "DATA LAYER", C["teal"]),
                               (3.7, "BACKEND LAYER", C["blue"]),
                               (1.5, "FRONTEND LAYER", C["purple"])]:
        ax.text(0.15, y_pos, label, fontsize=8, fontweight="bold", color=col,
                rotation=90, va="center")

    # Data layer
    box(0.6, 5.2, 2.5, 1.1, "Employees_raw_Data.csv", "Raw CSV Dataset", C["teal"])

    # Backend boxes
    box(0.6, 3.2, 2.5, 1.1, "data_loader.py", "Load · Clean · Engineer", C["blue"])
    box(3.6, 3.2, 2.5, 1.1, "analysis.py", "KPIs · Aggregations · Stats", C["green"])
    box(6.6, 3.2, 2.5, 1.1, "predictions.py", "Ridge · RandomForest · Risk", C["amber"])
    box(9.6, 3.2, 2.5, 1.1, "chart_builder.py", "8 Chart Types · 10 Palettes", C["orange"])

    # Frontend
    box(0.6, 1.0, 11.5, 1.5, "app.py  —  Streamlit Dashboard  (12 Pages)",
        "Overview · Quality · Dept · City · Salary · Performance · Remote · Tenure · Correlations · Explorer · Predictions · Chart Builder",
        C["purple"], fontsize=11)

    # Arrows data → data_loader
    arrow(1.85, 5.2, 1.85, 4.3)
    # Arrows data_loader → others
    for tx in [4.85, 7.85, 10.85]:
        arrow(3.1, 3.75, tx-0.5, 3.75)
    # All backend → frontend
    for bx in [1.85, 4.85, 7.85, 10.85]:
        arrow(bx, 3.2, bx, 2.5)

    save(fig, "01_architecture.png")

# ═════════════════════════════════════════════════════════════════════════════
# 2. DATA PIPELINE / FLOW DIAGRAM
# ═════════════════════════════════════════════════════════════════════════════
def fig_data_pipeline():
    fig, ax = plt.subplots(figsize=(14, 4))
    fig.patch.set_facecolor(C["light"])
    ax.set_facecolor(C["light"])
    ax.set_xlim(0, 14); ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("Data Pipeline — Raw CSV to Analysis-Ready DataFrame", fontsize=14,
                 fontweight="bold", color=C["dark"], pad=10)

    steps = [
        ("Raw CSV\nLoad", C["teal"]),
        ("Normalise\nColumn Names", C["blue"]),
        ("Parse\njoin_date", C["blue"]),
        ("Fix\nremote_work", C["amber"]),
        ("Impute\nMissing", C["orange"]),
        ("Derive\nFeatures", C["green"]),
        ("Analysis\nReady ✓", C["green"]),
    ]
    w, h, gap = 1.6, 1.4, 0.3
    y0 = 1.3
    for i, (label, color) in enumerate(steps):
        x = 0.3 + i * (w + gap)
        rect = FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.1",
                              linewidth=1.5, edgecolor=color, facecolor=color+"33")
        ax.add_patch(rect)
        ax.text(x + w/2, y0 + h/2, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=color)
        if i < len(steps)-1:
            ax.annotate("", xy=(x+w+gap, y0+h/2), xytext=(x+w, y0+h/2),
                        arrowprops=dict(arrowstyle="->", color=C["muted"], lw=2))

    # Sub-labels under Impute and Derive
    ax.text(0.3 + 4*(w+gap) + w/2, y0 - 0.35,
            "salary · age · rating\n(dept median)", ha="center", fontsize=7.5, color=C["muted"])
    ax.text(0.3 + 5*(w+gap) + w/2, y0 - 0.35,
            "tenure_years · age_group\nsalary_band", ha="center", fontsize=7.5, color=C["muted"])

    save(fig, "02_data_pipeline.png")

# ═════════════════════════════════════════════════════════════════════════════
# 3. DASHBOARD NAVIGATION MAP
# ═════════════════════════════════════════════════════════════════════════════
def fig_nav_map():
    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor(C["light"])
    ax.set_facecolor(C["light"])
    ax.set_xlim(0, 13); ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("Dashboard Navigation Map — 12 Pages", fontsize=14,
                 fontweight="bold", color=C["dark"], pad=10)

    pages = [
        (0.3,  4.5, "🏠 Overview",         C["blue"]),
        (3.0,  4.5, "🔍 Data Quality",      C["teal"]),
        (5.7,  4.5, "📊 Department",         C["green"]),
        (8.4,  4.5, "🏙️ City",               C["orange"]),
        (11.1, 4.5, "💰 Salary",             C["amber"]),
        (0.3,  2.7, "⭐ Performance",        C["amber"]),
        (3.0,  2.7, "🏡 Remote Work",        C["purple"]),
        (5.7,  2.7, "📅 Tenure & Age",       C["pink"]),
        (8.4,  2.7, "📈 Correlations",       C["blue"]),
        (11.1, 2.7, "🔎 Explorer",           C["teal"]),
        (3.0,  0.9, "🤖 Predictions",        C["red"]),
        (8.4,  0.9, "🎨 Chart Builder",      C["purple"]),
    ]

    # Sidebar
    rect = FancyBboxPatch((0.0, 0.2), 1.2, 5.5, boxstyle="round,pad=0.08",
                          linewidth=2, edgecolor=C["dark"], facecolor=C["dark"]+"ee")
    ax.add_patch(rect)
    ax.text(0.6, 5.55, "Sidebar", ha="center", fontsize=9, fontweight="bold", color=C["white"])
    for i, label in enumerate(["Filters:", "Dept", "City", "Rating", "Salary"]):
        ax.text(0.6, 4.7 - i*0.75, label, ha="center", fontsize=8,
                color=C["white"] if i > 0 else C["amber"])

    for (x, y, label, color) in pages:
        rect = FancyBboxPatch((x, y), 1.8, 0.9, boxstyle="round,pad=0.07",
                              linewidth=1.5, edgecolor=color, facecolor=color+"25")
        ax.add_patch(rect)
        ax.text(x + 0.9, y + 0.45, label, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color=color)
        ax.annotate("", xy=(x, y+0.45), xytext=(1.2, 3.0),
                    arrowprops=dict(arrowstyle="-", color=C["border"], lw=0.8, alpha=0.5))

    save(fig, "03_nav_map.png")

# ═════════════════════════════════════════════════════════════════════════════
# 4. OVERVIEW PAGE MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_overview_mockup():
    fig = plt.figure(figsize=(14, 9))
    fig.patch.set_facecolor(C["light"])
    ax_main = fig.add_axes([0, 0, 1, 1])
    ax_main.set_xlim(0, 14); ax_main.set_ylim(0, 9)
    ax_main.axis("off")

    # Title bar
    ax_main.add_patch(FancyBboxPatch((0, 8.4), 14, 0.6, boxstyle="square",
                                     facecolor=C["dark"], edgecolor="none"))
    ax_main.text(0.3, 8.7, "🏠 Employee Analytics Dashboard — Overview", fontsize=12,
                 fontweight="bold", color=C["white"], va="center")

    # Sidebar
    ax_main.add_patch(FancyBboxPatch((0, 0), 2.2, 8.4, boxstyle="square",
                                     facecolor="#1e2a3a", edgecolor="none"))
    ax_main.text(1.1, 8.1, "👥 Employee\nAnalytics", ha="center", fontsize=9,
                 color=C["white"], fontweight="bold")
    nav = ["🏠 Overview", "🔍 Data Quality", "📊 Department", "🏙️ City",
           "💰 Salary", "⭐ Performance", "🏡 Remote Work", "📅 Tenure",
           "📈 Correlations", "🔎 Explorer", "🤖 Predictions", "🎨 Chart Builder"]
    for i, n in enumerate(nav):
        bg = C["blue"]+"44" if i == 0 else "none"
        ax_main.add_patch(FancyBboxPatch((0.05, 7.6 - i*0.52), 2.1, 0.44,
                                         boxstyle="round,pad=0.04", facecolor=bg, edgecolor="none"))
        ax_main.text(0.2, 7.82 - i*0.52, n, fontsize=7.5,
                     color=C["white"] if i != 0 else C["blue"], fontweight="bold" if i==0 else "normal")

    # KPI cards row 1
    kpis1 = [("Total Employees", "150", C["blue"]),
             ("Avg Salary", "₹58,420", C["green"]),
             ("Avg Performance", "3.45/5", C["amber"]),
             ("Remote Workers", "38.7%", C["purple"]),
             ("Avg Tenure", "5.2 yrs", C["red"])]
    for i, (label, val, col) in enumerate(kpis1):
        x = 2.4 + i * 2.32
        ax_main.add_patch(FancyBboxPatch((x, 7.3), 2.1, 0.95, boxstyle="round,pad=0.08",
                                          facecolor=C["white"], edgecolor=col, linewidth=2))
        ax_main.add_patch(FancyBboxPatch((x, 7.3), 0.07, 0.95, boxstyle="square",
                                          facecolor=col, edgecolor="none"))
        ax_main.text(x+1.1, 7.89, val, ha="center", fontsize=13, fontweight="bold", color=C["dark"])
        ax_main.text(x+1.1, 7.45, label, ha="center", fontsize=7.5, color=C["muted"])

    # KPI cards row 2
    kpis2 = [("Departments", "5", C["teal"]),
             ("Cities", "5", C["green"]),
             ("Total Spend", "₹87.6L", C["orange"]),
             ("Median Salary", "₹55,450", C["blue"]),
             ("Avg Age", "41.2 yrs", C["pink"])]
    for i, (label, val, col) in enumerate(kpis2):
        x = 2.4 + i * 2.32
        ax_main.add_patch(FancyBboxPatch((x, 6.25), 2.1, 0.95, boxstyle="round,pad=0.08",
                                          facecolor=C["white"], edgecolor=col, linewidth=2))
        ax_main.add_patch(FancyBboxPatch((x, 6.25), 0.07, 0.95, boxstyle="square",
                                          facecolor=col, edgecolor="none"))
        ax_main.text(x+1.1, 6.84, val, ha="center", fontsize=13, fontweight="bold", color=C["dark"])
        ax_main.text(x+1.1, 6.40, label, ha="center", fontsize=7.5, color=C["muted"])

    # Chart 1: Headcount bar
    ax1 = fig.add_axes([0.175, 0.28, 0.36, 0.33])
    depts = ["Eng", "Sales", "HR", "Mkt", "Fin"]
    counts = [42, 38, 24, 27, 19]
    colors_bar = [C["blue"], C["green"], C["amber"], C["orange"], C["teal"]]
    bars = ax1.bar(depts, counts, color=colors_bar, edgecolor="white", linewidth=0.8)
    for bar, v in zip(bars, counts):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.8, str(v),
                 ha="center", fontsize=8, fontweight="bold")
    ax1.set_title("Headcount by Department", fontsize=9, fontweight="bold", color=C["dark"])
    ax1.set_facecolor(C["white"]); ax1.spines[["top","right"]].set_visible(False)
    ax1.tick_params(labelsize=8); ax1.set_ylim(0, 52)

    # Chart 2: Salary band donut
    ax2 = fig.add_axes([0.565, 0.28, 0.22, 0.33])
    sizes = [32, 78, 40]; labels = ["Low\n(<40k)", "Mid\n(40–75k)", "High\n(>75k)"]
    colors_pie = [C["red"], C["amber"], C["green"]]
    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie,
                                        autopct="%1.0f%%", startangle=90,
                                        wedgeprops=dict(width=0.55))
    for t in texts: t.set_fontsize(8)
    for at in autotexts: at.set_fontsize(8); at.set_fontweight("bold")
    ax2.set_title("Salary Bands", fontsize=9, fontweight="bold", color=C["dark"])

    # Chart 3: Rating bar
    ax3 = fig.add_axes([0.175, 0.04, 0.36, 0.22])
    ratings = ["1–Poor", "2–Below", "3–Average", "4–Good", "5–Excellent"]
    rcounts = [12, 18, 45, 52, 23]
    rcolors = [C["red"], C["orange"], C["amber"], "#86efac", C["green"]]
    rbars = ax3.bar(ratings, rcounts, color=rcolors, edgecolor="white")
    for b, v in zip(rbars, rcounts):
        ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, str(v),
                 ha="center", fontsize=7.5, fontweight="bold")
    ax3.set_title("Performance Rating Distribution", fontsize=9, fontweight="bold", color=C["dark"])
    ax3.set_facecolor(C["white"]); ax3.spines[["top","right"]].set_visible(False)
    ax3.tick_params(labelsize=7.5); ax3.set_ylim(0, 62)

    # Chart 4: Age groups
    ax4 = fig.add_axes([0.565, 0.04, 0.22, 0.22])
    ages = ["20–29", "30–39", "40–49", "50+"]
    acounts = [28, 48, 42, 32]
    acolors = [C["blue"], C["teal"], C["green"], C["purple"]]
    abars = ax4.bar(ages, acounts, color=acolors, edgecolor="white")
    for b, v in zip(abars, acounts):
        ax4.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, str(v),
                 ha="center", fontsize=7.5, fontweight="bold")
    ax4.set_title("Age Groups", fontsize=9, fontweight="bold", color=C["dark"])
    ax4.set_facecolor(C["white"]); ax4.spines[["top","right"]].set_visible(False)
    ax4.tick_params(labelsize=7.5); ax4.set_ylim(0, 58)

    save(fig, "04_overview_mockup.png")

# ═════════════════════════════════════════════════════════════════════════════
# 5. DATA QUALITY MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_data_quality():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Data Quality Page — Missing Value Audit", fontsize=13,
                 fontweight="bold", color=C["dark"])

    # Left: missing value table
    ax = axes[0]
    ax.axis("off")
    cols = ["Column", "Missing", "Missing %", "Status"]
    data = [["emp_name",           "0",  "0.00%", "✅ Clean"],
            ["department",         "4",  "2.67%", "⚠️ Low"],
            ["join_date",          "0",  "0.00%", "✅ Clean"],
            ["salary",             "8",  "5.33%", "⚠️ Low"],
            ["age",                "5",  "3.33%", "⚠️ Low"],
            ["performance_rating", "6",  "4.00%", "⚠️ Low"],
            ["city",               "0",  "0.00%", "✅ Clean"],
            ["remote_work",        "12", "8.00%", "⚠️ Low"]]
    tbl = ax.table(cellText=data, colLabels=cols, loc="center",
                   cellLoc="center", bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor(C["dark"]); cell.set_text_props(color="white", fontweight="bold")
        elif r % 2 == 0:
            cell.set_facecolor("#f0f4ff")
        cell.set_edgecolor(C["border"])
    ax.set_title("Missing Value Summary", fontsize=11, fontweight="bold", color=C["dark"], pad=10)

    # Right: bar chart of missing %
    ax2 = axes[1]
    missing_cols = ["department", "salary", "age", "performance_rating", "remote_work"]
    missing_pct  = [2.67, 5.33, 3.33, 4.00, 8.00]
    bar_colors   = [plt.cm.Reds(0.3 + v/20) for v in missing_pct]
    bars = ax2.barh(missing_cols, missing_pct, color=bar_colors, edgecolor="white")
    for bar, v in zip(bars, missing_pct):
        ax2.text(v + 0.1, bar.get_y() + bar.get_height()/2, f"{v:.2f}%",
                 va="center", fontsize=9, fontweight="bold", color=C["dark"])
    ax2.set_xlabel("Missing %", fontsize=10)
    ax2.set_title("Missing Values per Column", fontsize=11, fontweight="bold", color=C["dark"])
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)
    ax2.set_xlim(0, 12)

    plt.tight_layout()
    save(fig, "05_data_quality.png")

# ═════════════════════════════════════════════════════════════════════════════
# 6. DEPARTMENT ANALYSIS MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_dept_analysis():
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Department Analysis Page", fontsize=14, fontweight="bold", color=C["dark"])
    depts = ["Engineering", "Sales", "HR", "Marketing", "Finance"]
    colors5 = [C["blue"], C["green"], C["amber"], C["orange"], C["teal"]]

    # Headcount
    ax = axes[0][0]
    counts = [42, 38, 24, 27, 19]
    bars = ax.bar(depts, counts, color=colors5, edgecolor="white")
    for b, v in zip(bars, counts):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, str(v), ha="center", fontsize=8, fontweight="bold")
    ax.set_title("Headcount by Department", fontsize=10, fontweight="bold")
    ax.set_facecolor(C["white"]); ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8); ax.set_ylim(0, 52)

    # Avg salary
    ax2 = axes[0][1]
    salaries = [68420, 55800, 62100, 63900, 61200]
    bars2 = ax2.barh(depts, salaries, color=colors5, edgecolor="white")
    for b, v in zip(bars2, salaries):
        ax2.text(v+400, b.get_y()+b.get_height()/2, f"₹{v:,}", va="center", fontsize=8, fontweight="bold")
    ax2.set_title("Avg Salary by Department", fontsize=10, fontweight="bold")
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)
    ax2.set_xlim(0, 82000); ax2.tick_params(labelsize=8)

    # Avg rating
    ax3 = axes[1][0]
    ratings = [3.8, 3.5, 3.6, 3.9, 3.4]
    rcolors = [plt.cm.RdYlGn(r/5) for r in ratings]
    bars3 = ax3.bar(depts, ratings, color=rcolors, edgecolor="white")
    for b, v in zip(bars3, ratings):
        ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.02, f"{v:.1f}", ha="center", fontsize=8, fontweight="bold")
    ax3.set_title("Avg Performance Rating", fontsize=10, fontweight="bold")
    ax3.set_facecolor(C["white"]); ax3.spines[["top","right"]].set_visible(False)
    ax3.set_ylim(0, 5.2); ax3.tick_params(axis="x", labelsize=8)
    ax3.axhline(y=3.0, color=C["muted"], linestyle="--", alpha=0.5, linewidth=0.8)

    # Remote %
    ax4 = axes[1][1]
    remote = [42.9, 36.8, 33.3, 37.0, 26.3]
    rcolors4 = [plt.cm.Purples(0.4 + r/200) for r in remote]
    bars4 = ax4.bar(depts, remote, color=rcolors4, edgecolor="white")
    for b, v in zip(bars4, remote):
        ax4.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f"{v:.1f}%", ha="center", fontsize=8, fontweight="bold")
    ax4.set_title("Remote Work % by Department", fontsize=10, fontweight="bold")
    ax4.set_facecolor(C["white"]); ax4.spines[["top","right"]].set_visible(False)
    ax4.set_ylim(0, 55); ax4.tick_params(axis="x", labelsize=8)

    plt.tight_layout()
    save(fig, "06_dept_analysis.png")

# ═════════════════════════════════════════════════════════════════════════════
# 7. SALARY ANALYSIS MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_salary_analysis():
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Salary Analysis Page", fontsize=14, fontweight="bold", color=C["dark"])
    np.random.seed(42)

    # Histogram
    ax = axes[0][0]
    salaries = np.concatenate([np.random.normal(55000,15000,100), np.random.normal(80000,10000,50)])
    ax.hist(salaries, bins=25, color=C["blue"], edgecolor="white", alpha=0.85)
    ax.axvline(salaries.mean(), color=C["red"], linestyle="--", linewidth=1.5, label=f"Mean ₹{salaries.mean():,.0f}")
    ax.axvline(np.median(salaries), color=C["green"], linestyle="--", linewidth=1.5, label=f"Median ₹{np.median(salaries):,.0f}")
    ax.legend(fontsize=8); ax.set_title("Salary Distribution", fontsize=10, fontweight="bold")
    ax.set_xlabel("Salary (₹)", fontsize=9); ax.set_ylabel("Count", fontsize=9)
    ax.set_facecolor(C["white"]); ax.spines[["top","right"]].set_visible(False)

    # Box plot by dept
    ax2 = axes[0][1]
    depts = ["Engineering", "Sales", "HR", "Marketing", "Finance"]
    dept_data = [np.random.normal(68000,12000,42), np.random.normal(56000,18000,38),
                 np.random.normal(62000,10000,24), np.random.normal(64000,14000,27),
                 np.random.normal(61000,16000,19)]
    bp = ax2.boxplot(dept_data, labels=depts, patch_artist=True,
                     boxprops=dict(linewidth=1.5), whiskerprops=dict(linewidth=1.5))
    bcolors = [C["blue"],C["green"],C["amber"],C["orange"],C["teal"]]
    for patch, col in zip(bp["boxes"], bcolors):
        patch.set_facecolor(col+"55"); patch.set_edgecolor(col)
    ax2.set_title("Salary Box Plot by Department", fontsize=10, fontweight="bold")
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)
    ax2.tick_params(axis="x", labelsize=8)

    # Salary band donut
    ax3 = axes[1][0]
    sizes = [32, 78, 40]; slabels = ["Low\n<₹40k", "Mid\n₹40–75k", "High\n>₹75k"]
    wedges, texts, autotexts = ax3.pie(sizes, labels=slabels, autopct="%1.1f%%",
                                        colors=[C["red"],C["amber"],C["green"]],
                                        startangle=90, wedgeprops=dict(width=0.55))
    for t in texts: t.set_fontsize(9)
    for at in autotexts: at.set_fontsize(9); at.set_fontweight("bold")
    ax3.set_title("Salary Band Distribution", fontsize=10, fontweight="bold")

    # Scatter salary vs performance
    ax4 = axes[1][1]
    perf = np.random.randint(1, 6, 150)
    sal = 30000 + perf*8000 + np.random.normal(0, 12000, 150)
    dept_idx = np.random.randint(0, 5, 150)
    dept_colors_sc = [C["blue"],C["green"],C["amber"],C["orange"],C["teal"]]
    for d in range(5):
        mask = dept_idx == d
        ax4.scatter(perf[mask], sal[mask], alpha=0.6, s=40,
                    color=dept_colors_sc[d], label=depts[d])
    ax4.set_xlabel("Performance Rating", fontsize=9)
    ax4.set_ylabel("Salary (₹)", fontsize=9)
    ax4.set_title("Salary vs Performance Rating", fontsize=10, fontweight="bold")
    ax4.legend(fontsize=7, ncol=2)
    ax4.set_facecolor(C["white"]); ax4.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    save(fig, "07_salary_analysis.png")

# ═════════════════════════════════════════════════════════════════════════════
# 8. PERFORMANCE ANALYSIS MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_performance_analysis():
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Performance Analysis Page", fontsize=14, fontweight="bold", color=C["dark"])

    # Rating distribution
    ax = axes[0][0]
    labels = ["1–Poor","2–Below Avg","3–Average","4–Good","5–Excellent"]
    vals = [12, 18, 45, 52, 23]
    rcolors = [C["red"],C["orange"],C["amber"],"#86efac",C["green"]]
    bars = ax.bar(labels, vals, color=rcolors, edgecolor="white")
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, b.get_height()+0.5, str(v),
                ha="center", fontsize=9, fontweight="bold")
    ax.set_title("Performance Rating Distribution", fontsize=10, fontweight="bold")
    ax.set_facecolor(C["white"]); ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8); ax.set_ylim(0, 65)

    # Avg by dept
    ax2 = axes[0][1]
    depts = ["Marketing","Engineering","HR","Sales","Finance"]
    ratings2 = [3.9, 3.8, 3.6, 3.5, 3.4]
    rcolors2 = [plt.cm.RdYlGn(r/5) for r in ratings2]
    bars2 = ax2.bar(depts, ratings2, color=rcolors2, edgecolor="white")
    for b, v in zip(bars2, ratings2):
        ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.02, f"{v:.2f}",
                 ha="center", fontsize=9, fontweight="bold")
    ax2.set_title("Avg Rating by Department", fontsize=10, fontweight="bold")
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)
    ax2.set_ylim(0, 5.2); ax2.tick_params(axis="x", labelsize=8)
    ax2.axhline(3.0, color=C["muted"], linestyle="--", alpha=0.5, linewidth=1)

    # By age group
    ax3 = axes[1][0]
    age_groups = ["20–29","30–39","40–49","50+"]
    age_ratings = [3.4, 3.6, 3.7, 3.5]
    acolors = [C["blue"],C["teal"],C["green"],C["purple"]]
    bars3 = ax3.bar(age_groups, age_ratings, color=acolors, edgecolor="white")
    for b, v in zip(bars3, age_ratings):
        ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.02, f"{v:.2f}",
                 ha="center", fontsize=9, fontweight="bold")
    ax3.set_title("Avg Rating by Age Group", fontsize=10, fontweight="bold")
    ax3.set_facecolor(C["white"]); ax3.spines[["top","right"]].set_visible(False)
    ax3.set_ylim(0, 5.2)

    # By salary band
    ax4 = axes[1][1]
    bands = ["Low (<40k)","Mid (40–75k)","High (>75k)"]
    brand_ratings = [3.2, 3.6, 3.85]
    bcolors = [C["red"], C["amber"], C["green"]]
    bars4 = ax4.bar(bands, brand_ratings, color=bcolors, edgecolor="white")
    for b, v in zip(bars4, brand_ratings):
        ax4.text(b.get_x()+b.get_width()/2, b.get_height()+0.02, f"{v:.2f}",
                 ha="center", fontsize=9, fontweight="bold")
    ax4.set_title("Avg Rating by Salary Band", fontsize=10, fontweight="bold")
    ax4.set_facecolor(C["white"]); ax4.spines[["top","right"]].set_visible(False)
    ax4.set_ylim(0, 5.2)

    plt.tight_layout()
    save(fig, "08_performance_analysis.png")

# ═════════════════════════════════════════════════════════════════════════════
# 9. CORRELATION HEATMAP
# ═════════════════════════════════════════════════════════════════════════════
def fig_correlations():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Correlations Page", fontsize=14, fontweight="bold", color=C["dark"])

    # Heatmap
    ax = axes[0]
    labels = ["salary", "age", "tenure_years", "perf_rating"]
    corr = np.array([[1.00,  0.18,  0.22, 0.15],
                     [0.18,  1.00,  0.68, 0.05],
                     [0.22,  0.68,  1.00, 0.08],
                     [0.15,  0.05,  0.08, 1.00]])
    im = ax.imshow(corr, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(4)); ax.set_yticks(range(4))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{corr[i,j]:.2f}", ha="center", va="center",
                    fontsize=11, fontweight="bold",
                    color="white" if abs(corr[i,j]) > 0.5 else "black")
    plt.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title("Correlation Heatmap", fontsize=11, fontweight="bold")

    # Scatter age vs salary with OLS
    ax2 = axes[1]
    np.random.seed(7)
    age = np.random.randint(22, 62, 150)
    sal = 20000 + age * 900 + np.random.normal(0, 12000, 150)
    dept_idx = np.random.randint(0, 5, 150)
    dept_names = ["Engineering","Sales","HR","Marketing","Finance"]
    dc = [C["blue"],C["green"],C["amber"],C["orange"],C["teal"]]
    for d in range(5):
        mask = dept_idx == d
        ax2.scatter(age[mask], sal[mask], color=dc[d], alpha=0.55, s=35, label=dept_names[d])
    m, b = np.polyfit(age, sal, 1)
    x_line = np.linspace(22, 62, 50)
    ax2.plot(x_line, m*x_line+b, color=C["dark"], linewidth=2, linestyle="--", label="OLS trend")
    ax2.set_xlabel("Age", fontsize=9); ax2.set_ylabel("Salary (₹)", fontsize=9)
    ax2.set_title("Age vs Salary (OLS Trendline)", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=7, ncol=2)
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    save(fig, "09_correlations.png")

# ═════════════════════════════════════════════════════════════════════════════
# 10. ML PREDICTIONS MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_predictions():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("ML Predictions Page — 3 Models", fontsize=14, fontweight="bold", color=C["dark"])

    # Feature importance (salary model)
    ax = axes[0]
    feats = ["city_Delhi","dept_Eng","dept_Sales","age","tenure","rating","dept_HR","city_Pune"]
    importances = [12500, 9800, 8200, 6100, 5400, 4800, 3900, 3200]
    colors_f = [plt.cm.Blues(0.4 + v/30000) for v in importances]
    bars = ax.barh(feats[::-1], importances[::-1], color=colors_f[::-1], edgecolor="white")
    for b, v in zip(bars, importances[::-1]):
        ax.text(v+150, b.get_y()+b.get_height()/2, f"{v:,}", va="center", fontsize=8, fontweight="bold")
    ax.set_title("Salary Model\nFeature Coefficients", fontsize=10, fontweight="bold", color=C["dark"])
    ax.set_xlabel("|Coefficient|", fontsize=9); ax.set_facecolor(C["white"])
    ax.spines[["top","right"]].set_visible(False); ax.set_xlim(0, 16000)

    # Performance probability bars
    ax2 = axes[1]
    rating_labels = ["1–Poor","2–Below","3–Average","4–Good","5–Excellent"]
    probs = [0.04, 0.08, 0.22, 0.46, 0.20]
    prob_colors = [C["red"],C["orange"],C["amber"],"#86efac",C["green"]]
    bars2 = ax2.bar(rating_labels, probs, color=prob_colors, edgecolor="white")
    for b, v in zip(bars2, probs):
        ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.005, f"{v:.0%}",
                 ha="center", fontsize=9, fontweight="bold")
    ax2.set_title("Performance Classifier\nPredicted Probabilities", fontsize=10, fontweight="bold", color=C["dark"])
    ax2.set_ylabel("Probability", fontsize=9); ax2.set_ylim(0, 0.6)
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)
    ax2.tick_params(axis="x", labelsize=8)
    ax2.add_patch(FancyBboxPatch((2.4, 0.5), 1.2, 0.08, boxstyle="round,pad=0.04",
                                  facecolor=C["green"]+"33", edgecolor=C["green"]))
    ax2.text(3.0, 0.54, "Predicted: 4–Good", ha="center", fontsize=8.5,
             fontweight="bold", color=C["green"])

    # Attrition risk pie
    ax3 = axes[2]
    risk_sizes = [28, 52, 70]
    risk_labels = [f"High Risk\n(28)", f"Medium Risk\n(52)", f"Low Risk\n(70)"]
    wedges, texts, autotexts = ax3.pie(risk_sizes, labels=risk_labels, autopct="%1.0f%%",
                                        colors=[C["red"],C["amber"],C["green"]],
                                        startangle=90, wedgeprops=dict(width=0.6))
    for t in texts: t.set_fontsize(8)
    for at in autotexts: at.set_fontsize(9); at.set_fontweight("bold")
    ax3.set_title("Attrition Risk\nDistribution", fontsize=10, fontweight="bold", color=C["dark"])

    plt.tight_layout()
    save(fig, "10_predictions_mockup.png")

# ═════════════════════════════════════════════════════════════════════════════
# 11. ATTRITION RISK TABLE MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_attrition_table():
    fig, ax = plt.subplots(figsize=(13, 5))
    fig.patch.set_facecolor(C["light"])
    ax.axis("off")
    ax.set_title("Attrition Risk Scoring — Full Employee Risk Table", fontsize=13,
                 fontweight="bold", color=C["dark"], pad=10)

    cols = ["Employee", "Dept", "City", "Salary", "Age", "Tenure", "Rating", "Remote", "Risk Score", "Risk Level"]
    data = [
        ["Employee_14", "Sales",       "Delhi",    "₹53,979", "35", "5.9 yrs", "1", "Yes", "65",  "🔴 High"],
        ["Employee_34", "Finance",     "Chennai",  "₹37,540", "58", "6.4 yrs", "1", "No",  "62",  "🔴 High"],
        ["Employee_54", "Finance",     "Delhi",    "₹24,862", "22", "5.8 yrs", "4", "No",  "55",  "🟡 Medium"],
        ["Employee_5",  "Sales",       "Chennai",  "₹23,547", "43", "6.8 yrs", "4", "Yes", "50",  "🟡 Medium"],
        ["Employee_31", "Marketing",   "Mumbai",   "₹1,657",  "59", "6.3 yrs", "5", "Yes", "45",  "🟡 Medium"],
        ["Employee_1",  "Engineering", "Pune",     "₹60,820", "51", "6.9 yrs", "4", "No",  "10",  "🟢 Low"],
        ["Employee_18", "Engineering", "Delhi",    "₹67,290", "30", "5.8 yrs", "5", "Yes", "5",   "🟢 Low"],
        ["Employee_11", "Sales",       "Bangalore","₹69,090", "53", "6.7 yrs", "4", "Yes", "10",  "🟢 Low"],
    ]

    tbl = ax.table(cellText=data, colLabels=cols, loc="center",
                   cellLoc="center", bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False); tbl.set_fontsize(8.5)

    risk_cols = {row: data[row-1][-1] for row in range(1, len(data)+1)}
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor(C["border"])
        if r == 0:
            cell.set_facecolor(C["dark"]); cell.set_text_props(color="white", fontweight="bold")
        else:
            score = data[r-1][8]
            if "High" in data[r-1][-1]:
                cell.set_facecolor("#fee2e2" if c < len(cols)-1 else "#fca5a5")
            elif "Medium" in data[r-1][-1]:
                cell.set_facecolor("#fef9c3" if c < len(cols)-1 else "#fde68a")
            else:
                cell.set_facecolor("#dcfce7" if c < len(cols)-1 else "#86efac")

    save(fig, "11_attrition_table.png")

# ═════════════════════════════════════════════════════════════════════════════
# 12. CHART BUILDER MOCKUP
# ═════════════════════════════════════════════════════════════════════════════
def fig_chart_builder():
    fig = plt.figure(figsize=(14, 7))
    fig.patch.set_facecolor(C["light"])

    # Left: config panel mockup
    ax_cfg = fig.add_axes([0, 0.05, 0.38, 0.9])
    ax_cfg.set_xlim(0, 4); ax_cfg.set_ylim(0, 10)
    ax_cfg.set_facecolor(C["white"])
    ax_cfg.set_title("⚙️  Chart Configuration Panel", fontsize=11, fontweight="bold", color=C["dark"])
    for spine in ax_cfg.spines.values():
        spine.set_edgecolor(C["border"]); spine.set_linewidth(1.5)
    ax_cfg.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    controls = [
        ("Chart Type",      "Bar",              C["blue"]),
        ("X-Axis / Category","department",      C["green"]),
        ("Y-Axis / Value",  "salary",           C["amber"]),
        ("Colour Group",    "city",             C["purple"]),
        ("Aggregation",     "Mean",             C["teal"]),
        ("Colour Palette",  "Pastel",           C["orange"]),
        ("Chart Height",    "450 px",           C["pink"]),
        ("Show Labels",     "✅ Yes",           C["green"]),
    ]
    for i, (label, val, col) in enumerate(controls):
        y = 9.0 - i * 1.05
        ax_cfg.add_patch(FancyBboxPatch((0.15, y-0.35), 3.7, 0.8,
                                         boxstyle="round,pad=0.06",
                                         facecolor=col+"15", edgecolor=col+"66"))
        ax_cfg.text(0.35, y+0.07, label, fontsize=8.5, color=C["muted"])
        ax_cfg.text(3.65, y+0.07, val, fontsize=9, fontweight="bold", color=col, ha="right")

    ax_cfg.add_patch(FancyBboxPatch((0.15, 0.15), 3.7, 0.65,
                                     boxstyle="round,pad=0.06",
                                     facecolor=C["blue"], edgecolor="none"))
    ax_cfg.text(2.0, 0.48, "🎨  Generate Chart", ha="center", fontsize=11,
                fontweight="bold", color="white")

    # Right: generated chart
    ax_out = fig.add_axes([0.42, 0.1, 0.56, 0.82])
    depts = ["Engineering", "Sales", "HR", "Marketing", "Finance"]
    salaries = [68420, 55800, 62100, 63900, 61200]
    colors_bar = [C["blue"], C["green"], C["amber"], C["orange"], C["teal"]]
    bars = ax_out.bar(depts, salaries, color=colors_bar, edgecolor="white", width=0.6)
    for bar, v in zip(bars, salaries):
        ax_out.text(bar.get_x()+bar.get_width()/2, bar.get_height()+500,
                    f"₹{v:,}", ha="center", fontsize=9, fontweight="bold")
    ax_out.set_title("Mean of Salary by department", fontsize=12, fontweight="bold", color=C["dark"])
    ax_out.set_ylabel("salary", fontsize=10); ax_out.set_xlabel("department", fontsize=10)
    ax_out.set_facecolor(C["white"]); ax_out.spines[["top","right"]].set_visible(False)
    ax_out.tick_params(axis="x", labelsize=9); ax_out.set_ylim(0, 82000)
    ax_out.set_title("Mean of salary by department  [Chart Builder Output]",
                     fontsize=10, fontweight="bold", color=C["dark"])

    save(fig, "12_chart_builder.png")

# ═════════════════════════════════════════════════════════════════════════════
# 13. ML MODEL FLOWCHART
# ═════════════════════════════════════════════════════════════════════════════
def fig_ml_flow():
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor(C["light"])
    ax.set_facecolor(C["light"])
    ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("ML Models Pipeline Flowchart", fontsize=14, fontweight="bold", color=C["dark"], pad=12)

    def bx(x, y, w, h, text, color, fs=9):
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                              linewidth=1.5, edgecolor=color, facecolor=color+"25")
        ax.add_patch(rect)
        ax.text(x+w/2, y+h/2, text, ha="center", va="center",
                fontsize=fs, fontweight="bold", color=color)

    def arr(x1, y1, x2, y2):
        ax.annotate("", xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.5))

    # Common input
    bx(0.2, 2.4, 2.0, 1.2, "Cleaned\nDataFrame", C["teal"], 10)
    arr(2.2, 3.0, 3.0, 3.0)

    # Preprocessor
    bx(3.0, 2.4, 2.2, 1.2, "ColumnTransformer\nStandardScaler\n+ OneHotEncoder", C["blue"], 8)

    # Model 1: Ridge
    arr(5.2, 4.2, 6.0, 4.7)
    bx(6.0, 4.3, 2.2, 1.0, "Ridge\nRegression", C["green"])
    arr(8.2, 4.8, 9.0, 4.8)
    bx(9.0, 4.3, 2.2, 1.0, "Predicted\nSalary (₹)", C["green"])

    # Model 2: RF Classifier
    arr(5.2, 3.0, 6.0, 3.0)
    bx(6.0, 2.5, 2.2, 1.0, "Random Forest\nClassifier", C["amber"])
    arr(8.2, 3.0, 9.0, 3.0)
    bx(9.0, 2.5, 2.2, 1.0, "Rating 1–5\n+ Probabilities", C["amber"])

    # Model 3: Heuristic
    arr(5.2, 1.8, 6.0, 1.3)
    bx(6.0, 0.8, 2.2, 1.0, "Business Rules\nHeuristic", C["red"])
    arr(8.2, 1.3, 9.0, 1.3)
    bx(9.0, 0.8, 2.2, 1.0, "Risk Score\n0–100", C["red"])

    # Fan out arrow from preprocessor
    arr(4.1, 3.0, 6.0, 4.8)
    arr(4.1, 3.0, 6.0, 1.3)

    # Labels
    ax.text(6.1, 5.45, "Model 1: Salary Predictor", fontsize=8.5, color=C["green"], fontweight="bold")
    ax.text(6.1, 3.58, "Model 2: Performance Classifier", fontsize=8.5, color=C["amber"], fontweight="bold")
    ax.text(6.1, 1.92, "Model 3: Attrition Risk Scorer", fontsize=8.5, color=C["red"], fontweight="bold")

    # Cross-validation note
    ax.text(6.1, 0.25, "All models evaluated with 5-Fold Cross Validation + MAE / Accuracy / R²",
            fontsize=8, color=C["muted"], style="italic")

    save(fig, "13_ml_flowchart.png")

# ═════════════════════════════════════════════════════════════════════════════
# 14. REMOTE WORK + CITY ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
def fig_remote_city():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Remote Work & City Analysis", fontsize=14, fontweight="bold", color=C["dark"])

    # Remote donut
    ax = axes[0]
    wedges, texts, auts = ax.pie([58, 92], labels=["Remote\n(58)", "On-Site\n(92)"],
                                  autopct="%1.0f%%", colors=[C["purple"], C["blue"]],
                                  startangle=90, wedgeprops=dict(width=0.55))
    for t in texts: t.set_fontsize(10)
    for at in auts: at.set_fontsize(11); at.set_fontweight("bold")
    ax.set_title("Remote vs On-Site Split", fontsize=11, fontweight="bold")

    # City headcount
    ax2 = axes[1]
    cities = ["Delhi", "Pune", "Mumbai", "Bangalore", "Chennai"]
    hc = [38, 32, 29, 28, 23]
    bars = ax2.bar(cities, hc, color=[C["blue"],C["teal"],C["orange"],C["green"],C["purple"]], edgecolor="white")
    for b, v in zip(bars, hc):
        ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, str(v),
                 ha="center", fontsize=9, fontweight="bold")
    ax2.set_title("Headcount by City", fontsize=11, fontweight="bold")
    ax2.set_facecolor(C["white"]); ax2.spines[["top","right"]].set_visible(False)
    ax2.tick_params(axis="x", labelsize=9); ax2.set_ylim(0, 48)

    # Remote by dept
    ax3 = axes[2]
    depts = ["Engineering","Sales","HR","Marketing","Finance"]
    rpct = [42.9, 36.8, 33.3, 37.0, 26.3]
    rcolors = [plt.cm.Purples(0.4+r/200) for r in rpct]
    bars3 = ax3.bar(depts, rpct, color=rcolors, edgecolor="white")
    for b, v in zip(bars3, rpct):
        ax3.text(b.get_x()+b.get_width()/2, b.get_height()+0.3, f"{v:.1f}%",
                 ha="center", fontsize=9, fontweight="bold")
    ax3.set_title("Remote % by Department", fontsize=11, fontweight="bold")
    ax3.set_facecolor(C["white"]); ax3.spines[["top","right"]].set_visible(False)
    ax3.tick_params(axis="x", labelsize=8); ax3.set_ylim(0, 56)

    plt.tight_layout()
    save(fig, "14_remote_city.png")

# ═════════════════════════════════════════════════════════════════════════════
# 15. TENURE & AGE ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
def fig_tenure_age():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.patch.set_facecolor(C["light"])
    fig.suptitle("Tenure & Age Analysis Page", fontsize=14, fontweight="bold", color=C["dark"])
    np.random.seed(3)

    # Age histogram
    ax = axes[0]
    ages = np.random.normal(41, 10, 150).clip(20, 65)
    ax.hist(ages, bins=20, color=C["pink"], edgecolor="white", alpha=0.85)
    ax.axvline(ages.mean(), color=C["dark"], linestyle="--", linewidth=1.5,
               label=f"Mean {ages.mean():.1f}")
    ax.legend(fontsize=8); ax.set_title("Age Distribution", fontsize=11, fontweight="bold")
    ax.set_xlabel("Age (years)", fontsize=9); ax.set_facecolor(C["white"])
    ax.spines[["top","right"]].set_visible(False)

    # Tenure histogram
    ax2 = axes[1]
    tenures = np.random.uniform(3.0, 7.5, 150)
    ax2.hist(tenures, bins=15, color=C["orange"], edgecolor="white", alpha=0.85)
    ax2.axvline(tenures.mean(), color=C["dark"], linestyle="--", linewidth=1.5,
                label=f"Mean {tenures.mean():.1f} yrs")
    ax2.legend(fontsize=8); ax2.set_title("Tenure Distribution", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Tenure (years)", fontsize=9); ax2.set_facecolor(C["white"])
    ax2.spines[["top","right"]].set_visible(False)

    # Salary vs tenure scatter
    ax3 = axes[2]
    tenure2 = np.random.uniform(3, 7.5, 150)
    sal2 = 30000 + tenure2 * 4500 + np.random.normal(0, 12000, 150)
    dept_idx = np.random.randint(0, 5, 150)
    dc = [C["blue"],C["green"],C["amber"],C["orange"],C["teal"]]
    depts = ["Engineering","Sales","HR","Marketing","Finance"]
    for d in range(5):
        mask = dept_idx == d
        ax3.scatter(tenure2[mask], sal2[mask], color=dc[d], alpha=0.55, s=30, label=depts[d])
    m, b = np.polyfit(tenure2, sal2, 1)
    xl = np.linspace(3, 7.5, 40)
    ax3.plot(xl, m*xl+b, color=C["dark"], linewidth=2, linestyle="--")
    ax3.set_xlabel("Tenure (years)", fontsize=9); ax3.set_ylabel("Salary (₹)", fontsize=9)
    ax3.set_title("Salary vs Tenure", fontsize=11, fontweight="bold")
    ax3.legend(fontsize=6.5, ncol=2); ax3.set_facecolor(C["white"])
    ax3.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    save(fig, "15_tenure_age.png")

# ═════════════════════════════════════════════════════════════════════════════
# RUN ALL
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating report diagrams…")
    fig_architecture()
    fig_data_pipeline()
    fig_nav_map()
    fig_overview_mockup()
    fig_data_quality()
    fig_dept_analysis()
    fig_salary_analysis()
    fig_performance_analysis()
    fig_correlations()
    fig_predictions()
    fig_attrition_table()
    fig_chart_builder()
    fig_ml_flow()
    fig_remote_city()
    fig_tenure_age()
    print(f"\nAll diagrams saved to: {OUT}")
