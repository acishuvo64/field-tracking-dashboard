import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Field Force Dashboard",
    page_icon="📍",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.main-title{
    font-size:42px;
    font-weight:bold;
    color:#0F172A;
}
.sub-title{
    font-size:18px;
    color:#64748B;
}
.kpi-card{
    background: linear-gradient(135deg,#1E3A8A,#2563EB);
    padding:20px;
    border-radius:18px;
    color:white;
    text-align:center;
    box-shadow:0px 4px 12px rgba(0,0,0,0.15);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown(
    '<p class="main-title">📍 AI Field Force Tracking Dashboard</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="sub-title">Professional Employee Tracking & Productivity Analytics</p>',
    unsafe_allow_html=True
)

# =========================================================
# LOAD EXCEL FROM GITHUB REPO
# =========================================================
try:
    summary_df = pd.read_excel(
        "super_tracking_report.xlsx",
        sheet_name="Summarize_data"
    )

    image_df = pd.read_excel(
        "super_tracking_report.xlsx",
        sheet_name="Image_URL"
    )

except Exception as e:
    st.error(f"Excel File Loading Error: {e}")
    st.stop()

# =========================================================
# DATA CLEANING
# =========================================================
summary_df["Date"] = pd.to_datetime(
    summary_df["Date"],
    errors="coerce"
)

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.title("🎛 Dashboard Filters")

employee_list = sorted(
    summary_df["Employee Name"].dropna().unique()
)

selected_employee = st.sidebar.selectbox(
    "Select Employee",
    ["All"] + employee_list
)

if "Group" in summary_df.columns:
    group_list = sorted(
        summary_df["Group"].dropna().unique()
    )
    selected_group = st.sidebar.selectbox(
        "Select Group",
        ["All"] + group_list
    )
else:
    selected_group = "All"

if "Deg" in summary_df.columns:
    deg_list = sorted(
        summary_df["Deg"].dropna().unique()
    )
    selected_deg = st.sidebar.selectbox(
        "Select Designation",
        ["All"] + deg_list
    )
else:
    selected_deg = "All"

start_date = st.sidebar.date_input(
    "Start Date",
    summary_df["Date"].min()
)

end_date = st.sidebar.date_input(
    "End Date",
    summary_df["Date"].max()
)

# =========================================================
# FILTER DATA
# =========================================================
df = summary_df.copy()

if selected_employee != "All":
    df = df[df["Employee Name"] == selected_employee]

if selected_group != "All" and "Group" in df.columns:
    df = df[df["Group"] == selected_group]

if selected_deg != "All" and "Deg" in df.columns:
    df = df[df["Deg"] == selected_deg]

df = df[
    (df["Date"] >= pd.to_datetime(start_date))
    &
    (df["Date"] <= pd.to_datetime(end_date))
]

# =========================================================
# KPI CALCULATION
# =========================================================
total_emp = df["Employee Name"].nunique()
total_visit = df["Total Tp Visit"].sum()
total_working = df["Total Working Hr"].sum()
total_travel = df["Total Travel Hr"].sum()
total_idle = df["Total Idle Hr"].sum()
avg_productivity = df["Work productivity"].mean()

st.markdown("---")

col1, col2, col3, col4, col5, col6 = st.columns(6)

kpis = [
    ("Total Employee", total_emp),
    ("Total TP Visit", total_visit),
    ("Total Working Hr", total_working),
    ("Total Travel Hr", total_travel),
    ("Total Idle Hr", total_idle),
    ("Avg Productivity", round(avg_productivity, 2))
]

for col, (title, value) in zip(
    [col1, col2, col3, col4, col5, col6],
    kpis
):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <h4>{title}</h4>
                <h2>{value}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

# =========================================================
# TOP PERFORMER
# =========================================================
st.markdown("---")

top_emp = (
    df.groupby("Employee Name")["Work productivity"]
    .mean()
    .sort_values(ascending=False)
    .head(1)
)

if not top_emp.empty:
    st.success(
        f"🏆 Top Performer: {top_emp.index[0]} | "
        f"Productivity: {round(top_emp.iloc[0], 2)}"
    )

# =========================================================
# EMPLOYEE IMAGE
# =========================================================
if selected_employee != "All":

    img = image_df[
        image_df["Employee Name"] == selected_employee
    ]

    if not img.empty and "Image" in img.columns:
        st.image(img.iloc[0]["Image"], width=180)

# =========================================================
# PRODUCTIVITY CHART
# =========================================================
st.subheader("🏆 Employee Productivity Ranking")

prod = (
    df.groupby("Employee Name")["Work productivity"]
    .mean()
    .reset_index()
)

fig = px.bar(
    prod,
    x="Employee Name",
    y="Work productivity",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DAILY TREND
# =========================================================
st.subheader("📈 Daily Productivity Trend")

daily = (
    df.groupby("Date")["Work productivity"]
    .mean()
    .reset_index()
)

fig2 = px.line(
    daily,
    x="Date",
    y="Work productivity",
    markers=True
)

st.plotly_chart(fig2, use_container_width=True)

# =========================================================
# PIE CHART
# =========================================================
st.subheader("🥧 Work Distribution")

pie = pd.DataFrame({
    "Category": [
        "Travel Hr",
        "Idle Hr",
        "Working Hr"
    ],
    "Value": [
        total_travel,
        total_idle,
        total_working
    ]
})

fig3 = px.pie(
    pie,
    names="Category",
    values="Value",
    hole=0.4
)

st.plotly_chart(fig3, use_container_width=True)

# =========================================================
# TOP 10
# =========================================================
st.subheader("🔥 Top 10 Performer")

top10 = (
    df.groupby("Employee Name")["Work productivity"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    top10,
    x="Employee Name",
    y="Work productivity",
    text_auto=True
)

st.plotly_chart(fig4, use_container_width=True)

# =========================================================
# LOW 10
# =========================================================
st.subheader("⚠ Lowest 10 Performer")

low10 = (
    df.groupby("Employee Name")["Work productivity"]
    .mean()
    .sort_values()
    .head(10)
    .reset_index()
)

fig5 = px.bar(
    low10,
    x="Employee Name",
    y="Work productivity",
    text_auto=True
)

st.plotly_chart(fig5, use_container_width=True)

# =========================================================
# GROUP ANALYSIS
# =========================================================
if "Group" in df.columns:

    st.subheader("👥 Group Comparison")

    gdf = (
        df.groupby("Group")["Work productivity"]
        .mean()
        .reset_index()
    )

    fig6 = px.bar(
        gdf,
        x="Group",
        y="Work productivity",
        text_auto=True
    )

    st.plotly_chart(fig6, use_container_width=True)

# =========================================================
# TABLE
# =========================================================
st.subheader("📋 Detailed Data")

st.dataframe(df, use_container_width=True)

# =========================================================
# RISK EMPLOYEES
# =========================================================
st.subheader("🚨 Risk Employees")

risk = df[df["Work productivity"] < 3]

st.write(
    f"Low Productivity Employees: "
    f"{risk['Employee Name'].nunique()}"
)

st.dataframe(risk, use_container_width=True)
