import streamlit as st
import pandas as pd
import plotly.express as px

# ── Blue & green theme ────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #ffffff; }

    /* Hide sidebar entirely */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }

    /* Title */
    h1 { color: #1E40AF !important; }
    h2, h3 { color: #16A34A !important; }

    /* KPI metric cards */
    [data-testid="stMetric"] {
        background-color: #DBEAFE;
        border-left: 4px solid #16A34A;
        border-radius: 8px;
        padding: 12px;
    }
    [data-testid="stMetricLabel"] { color: #1E40AF !important; }
    [data-testid="stMetricValue"] { color: #1E3A8A !important; }

    /* Divider */
    hr { border-color: #93C5FD; }
</style>
""", unsafe_allow_html=True)

BLUE_GREEN = ["#1D4ED8", "#16A34A", "#2563EB", "#22C55E", "#3B82F6",
              "#4ADE80", "#60A5FA", "#86EFAC"]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")
st.title("📊 Sales Dashboard")

# ── Load data ─────────────────────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1g6tcDj9OaeF85xYTBSb6ioO5zOjRkWQGUwK9kJbSbb0/export?format=csv"

@st.cache_data(ttl=300)
def load_data(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    return df.dropna(subset=["Date", "Sales", "Quantity"])

if "YOUR_SHEET_ID" in SHEET_URL:
    st.info("Upload your CSV to preview the dashboard.")
    uploaded = st.file_uploader("Upload your exported CSV", type="csv")
    if uploaded is None:
        st.stop()
    df = pd.read_csv(uploaded)
    df.columns = df.columns.str.strip()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df = df.dropna(subset=["Date", "Sales", "Quantity"])
else:
    df = load_data(SHEET_URL)

# ── Top filters ────────────────────────────────────────────────────────────────
with st.expander("🔍 Filters", expanded=True):
    f1, f2, f3 = st.columns(3)

    date_min = df["Date"].min().date()
    date_max = df["Date"].max().date()
    with f1:
        start_date, end_date = st.date_input(
            "Date range",
            value=[date_min, date_max],
            min_value=date_min,
            max_value=date_max,
        )

    with f2:
        countries = st.multiselect(
            "Country",
            options=sorted(df["Country"].unique()),
            default=sorted(df["Country"].unique()),
        )

    with f3:
        products = st.multiselect(
            "Product",
            options=sorted(df["Product"].unique()),
            default=sorted(df["Product"].unique()),
        )

# ── Apply filters ──────────────────────────────────────────────────────────────
mask = (
    (df["Date"].dt.date >= start_date)
    & (df["Date"].dt.date <= end_date)
    & (df["Country"].isin(countries))
    & (df["Product"].isin(products))
)
filtered = df[mask]

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# ── KPI cards ─────────────────────────────────────────────────────────────────
total_sales    = filtered["Sales"].sum()
total_quantity = filtered["Quantity"].sum()
num_countries  = filtered["Country"].nunique()
num_products   = filtered["Product"].nunique()

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Sales",    f"RWF {total_sales:,.0f}")
k2.metric("📦 Total Quantity", f"{total_quantity:,.0f}")
k3.metric("🌍 Countries",      num_countries)
k4.metric("🛒 Products",       num_products)

st.markdown("---")

LAYOUT = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font_color="#1E40AF",
    margin=dict(t=10, b=10),
    showlegend=False,
)

# ── Charts – row 1 ────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Over Time")
    daily = filtered.groupby("Date", as_index=False)["Sales"].sum()
    fig1 = px.histogram(
        daily, x="Date", y="Sales", nbins=30,
        labels={"Sales": "Sales ($)", "Date": "Date"},
        color_discrete_sequence=["#1D4ED8"],
    )
    fig1.update_layout(**LAYOUT)
    fig1.update_traces(marker_line_color="#1E3A8A", marker_line_width=1)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Sales by Country")
    by_country = (
        filtered.groupby("Country", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    fig2 = px.bar(
        by_country, x="Country", y="Sales",
        labels={"Sales": "Sales (RWF)"},
        color="Country",
        color_discrete_sequence=BLUE_GREEN,
    )
    fig2.update_layout(**LAYOUT)
    fig2.update_traces(marker_line_color="#1E3A8A", marker_line_width=1)
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts – row 2 ────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Sales by Product")
    by_product = (
        filtered.groupby("Product", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    fig3 = px.bar(
        by_product, x="Product", y="Sales",
        labels={"Sales": "Sales (RWF)"},
        color="Product",
        color_discrete_sequence=BLUE_GREEN,
    )
    fig3.update_layout(**LAYOUT)
    fig3.update_traces(marker_line_color="#1E3A8A", marker_line_width=1)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Quantity Distribution")
    fig4 = px.histogram(
        filtered, x="Quantity", nbins=20,
        labels={"Quantity": "Quantity", "count": "Frequency"},
        color_discrete_sequence=["#16A34A"],
    )
    fig4.update_layout(**LAYOUT)
    fig4.update_traces(marker_line_color="#1E3A8A", marker_line_width=1)
    st.plotly_chart(fig4, use_container_width=True)

# ── Raw data table ────────────────────────────────────────────────────────────
with st.expander("Show raw data"):
    st.dataframe(
        filtered.sort_values("Date", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )
