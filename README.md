# 👥 Employee Data Analytics Dashboard

An end-to-end Python data analytics project with a **Streamlit** interactive dashboard for workforce analysis.

---

## 📂 Dataset

| Field | Detail |
|-------|--------|
| **Name** | Employees Raw Data |
| **Source** | Kaggle |
| **Link** | [https://www.kaggle.com/datasets/arjunsinghgangwar/employees-raw-data/data](https://www.kaggle.com/datasets/arjunsinghgangwar/employees-raw-data/data) |
| **Author** | Arjun Singh Gangwar |
| **Format** | CSV |
| **Columns** | `emp_name`, `department`, `join_date`, `salary`, `age`, `performance_rating`, `city`, `remote_work` |

> The dataset was sourced from Kaggle and contains raw employee records requiring cleaning (missing values, inconsistent formatting) before analysis.

---

## 📁 Project Structure

```
employee_analytics/
├── app.py                   ← Streamlit multi-page dashboard (frontend)
├── requirements.txt
├── data/
│   └── employees.csv        ← Cleaned copy of source dataset
└── backend/
    ├── __init__.py
    ├── data_loader.py       ← Data loading, cleaning & feature engineering
    └── analysis.py          ← All aggregation, KPI & analytics functions
```

---

## 🚀 Quick Start

### 1 · Install dependencies

```bash
cd employee_analytics
pip install -r requirements.txt
```

### 2 · Launch the dashboard

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**

---

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| 🏠 Overview | KPI cards + headcount, salary bands, ratings, age groups |
| 🔍 Data Quality | Missing values audit, raw vs cleaned data, cleaning log |
| 📊 Department Analysis | Headcount, salary, performance & remote work by dept |
| 🏙️ City Analysis | Headcount, salary and remote work by city |
| 💰 Salary Analysis | Distribution, box plots, salary vs performance scatter |
| ⭐ Performance Analysis | Rating breakdown, top/bottom performers tables |
| 🏡 Remote Work | Remote vs on-site split, by dept and city |
| 📅 Tenure & Age | Age and tenure histograms, salary vs tenure scatter |
| 📈 Correlations | Heatmap, OLS trendlines for salary/age/tenure/rating |
| 🔎 Employee Explorer | Search, filter, view records, and export CSV |

---

## 🔧 Data Cleaning Steps

| Issue | Fix Applied |
|-------|-------------|
| Mixed `remote_work` values (yes/YES/No/nan) | Normalised to `True`/`False` boolean |
| Missing `department` | Filled with `"Unknown"` |
| Missing `salary` | Imputed with department median |
| Missing `age` | Imputed with overall median |
| Missing `performance_rating` | Imputed with department median (rounded) |

---

## 🆕 Derived Columns

| Column | Description |
|--------|-------------|
| `tenure_years` | (Today − join_date) / 365.25 |
| `age_group` | Bucket: 20–29, 30–39, 40–49, 50+ |
| `salary_band` | Low (<40k), Mid (40k–75k), High (>75k) |

---

## 🛠️ Libraries Used

| Library | Purpose |
|---------|---------|
| `streamlit` | Interactive web frontend |
| `pandas` | Data manipulation |
| `numpy` | Numerical operations |
| `plotly` | Interactive charts |
| `scipy` / `statsmodels` | Statistical trendlines (OLS) |

---

## 💡 Business Insights the Dashboard Surfaces

1. **Which departments are overpaying or underpaying** vs. company median
2. **Top-performing employees** by rating + salary for retention targeting
3. **Remote work adoption** by department and city for policy planning
4. **Salary vs tenure / age correlations** to guide compensation strategy
5. **Low performers** who may need coaching or performance improvement plans
