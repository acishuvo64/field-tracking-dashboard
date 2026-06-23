# =========================================================
# AI FIELD FORCE DASHBOARD - FINAL VERSION
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import folium

from streamlit_folium import st_folium

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
    font-weight:800;
    color:#0F172A;
}

.sub-title{
    font-size:18px;
    color:#64748B;
    margin-bottom:20px;
}

.kpi-card{
    background: linear-gradient(135deg,#4F46E5,#7C3AED);
    padding:22px;
    border-radius:20px;
    color:white;
    text-align:center;
    box-shadow:0px 8px 20px rgba(0,0,0,0.12);
}

[data-testid="stSidebar"]{
    background:#0F172A;
}

[data-testid="stSidebar"] label{
    color:white !important;
    font-weight:600;
}

.stSelectbox div[data-baseweb="select"] > div{
    background:white !important;
    color:black !important;
}

.stDateInput input{
    background:white !important;
    color:black !important;
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
# LOAD EXCEL
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

    st.error(f"Excel Loading Error : {e}")
    st.stop()

# =========================================================
# DATE CLEANING
# =========================================================

summary_df["Date"] = pd.to_datetime(
    summary_df["Date"],
    errors="coerce"
)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("🎛 Dashboard Filters")

employee_list = sorted(
    summary_df["Employee Name"]
    .dropna()
    .unique()
)

selected_employee = st.sidebar.selectbox(
    "Select Employee",
    ["All"] + employee_list
)

group_list = sorted(
    summary_df["Group"]
    .dropna()
    .unique()
)

selected_group = st.sidebar.selectbox(
    "Select Group",
    ["All"] + group_list
)

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

    df = df[
        df["Employee Name"] == selected_employee
    ]

if selected_group != "All":

    df = df[
        df["Group"] == selected_group
    ]

df = df[
    (df["Date"] >= pd.to_datetime(start_date))
    &
    (df["Date"] <= pd.to_datetime(end_date))
]

# =========================================================
# KPI
# =========================================================

total_emp = df["Employee Name"].nunique()

total_working = round(
    df["Total Working Hr"].sum(),
    1
)

total_travel = round(
    df["Total Travel Hr"].sum(),
    1
)

total_idle = round(
    df["Total Idle Hr"].sum(),
    1
)

avg_productivity = round(
    df["Work productivity"].mean() * 100,
    1
)

st.markdown("---")

c1, c2, c3, c4 = st.columns(4)

kpis = [

    ("Employee", total_emp),

    ("Working Hr", total_working),

    ("Travel Hr", total_travel),

    ("Productivity %", f"{avg_productivity}%")
]

for col, (title, value) in zip(
    [c1, c2, c3, c4],
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
# PRODUCTIVITY CHART
# =========================================================

st.subheader("🏆 Employee Productivity Ranking")

prod = (
    df.groupby("Employee Name")
    ["Work productivity"]
    .mean()
    .reset_index()
)

prod["Work productivity"] = (
    prod["Work productivity"] * 100
).round(1)

fig = px.bar(
    prod,
    x="Employee Name",
    y="Work productivity",
    color="Work productivity",
    text_auto='.1f',
    template="plotly_dark"
)

fig.update_layout(
    yaxis_title="Productivity %"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================================
# PIE CHART
# =========================================================

st.subheader("🥧 Productivity Distribution")

total_time = (
    total_working +
    total_travel +
    total_idle
)

work_per = round(
    (total_working / total_time) * 100,
    1
)

travel_per = round(
    (total_travel / total_time) * 100,
    1
)

idle_per = round(
    (total_idle / total_time) * 100,
    1
)

pie_df = pd.DataFrame({

    "Category": [
        "Working Productivity",
        "Travel Productivity",
        "Idle Productivity"
    ],

    "Value": [
        work_per,
        travel_per,
        idle_per
    ]
})

fig2 = px.pie(
    pie_df,
    names="Category",
    values="Value",
    hole=0.45,
    template="plotly_dark"
)

fig2.update_traces(
    textinfo="percent+label"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================================
# DAILY PRODUCTIVITY TREND
# =========================================================

st.subheader("📈 Daily Productivity Trend")

daily = (
    df.groupby("Date")
    ["Work productivity"]
    .mean()
    .reset_index()
)

daily["Work productivity"] = (
    daily["Work productivity"] * 100
).round(1)

fig3 = px.line(
    daily,
    x="Date",
    y="Work productivity",
    markers=True,
    template="plotly_dark"
)

fig3.update_layout(
    yaxis_title="Productivity %"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# =========================================================
# WORKING VS TRAVEL
# =========================================================

st.subheader("⚡ Working vs Travel Hours")

compare_df = (
    df.groupby("Employee Name")[
        [
            "Total Working Hr",
            "Total Travel Hr",
            "Total Idle Hr"
        ]
    ]
    .sum()
    .reset_index()
)

fig4 = px.bar(
    compare_df,
    x="Employee Name",
    y=[
        "Total Working Hr",
        "Total Travel Hr",
        "Total Idle Hr"
    ],
    barmode="group",
    template="plotly_dark"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

# =========================================================
# MAP SECTION
# =========================================================

st.subheader("🗺 Employee Daily GPS Map")

try:

    if (
        selected_employee != "All"
        and
        "Lat,Lon" in df.columns
    ):

        map_df = df.dropna(
            subset=["Lat,Lon"]
        ).copy()

        lat_list = []
        lon_list = []

        for val in map_df["Lat,Lon"]:

            try:

                lat = float(
                    str(val).split(",")[0]
                )

                lon = float(
                    str(val).split(",")[1]
                )

                lat_list.append(lat)

                lon_list.append(lon)

            except:

                lat_list.append(None)
                lon_list.append(None)

        map_df["Latitude"] = lat_list
        map_df["Longitude"] = lon_list

        map_df = map_df.dropna(
            subset=["Latitude", "Longitude"]
        )

        if not map_df.empty:

            center_lat = map_df[
                "Latitude"
            ].mean()

            center_lon = map_df[
                "Longitude"
            ].mean()

            m = folium.Map(
                location=[
                    center_lat,
                    center_lon
                ],
                zoom_start=10
            )

            for _, row in map_df.iterrows():

                popup_text = f"""
                <b>{row['Employee Name']}</b><br>
                Date : {row['Date']}<br>
                Productivity : {round(row['Work productivity']*100,1)}%
                """

                folium.Marker(
                    [
                        row["Latitude"],
                        row["Longitude"]
                    ],
                    popup=popup_text,
                    tooltip=row["Employee Name"]
                ).add_to(m)

            st_folium(
                m,
                width=1200,
                height=500
            )

        else:

            st.warning(
                "No valid GPS data found"
            )

    else:

        st.info(
            "Select one employee to view GPS map"
        )

except Exception as e:

    st.error(f"Map Error : {e}")

# =========================================================
# AI PERFORMANCE ANALYSIS
# =========================================================

st.subheader("🤖 AI Performance Suggestion")

if avg_productivity >= 75:

    st.success("""
    Excellent productivity performance.

    Suggestions:
    • Maintain current field activity
    • Increase TP visits slightly
    • Continue strong working discipline
    """)

elif avg_productivity >= 50:

    st.warning("""
    Average productivity detected.

    Suggestions:
    • Reduce idle hours
    • Increase outlet visit frequency
    • Improve travel route planning
    • Focus on working efficiency
    """)

else:

    st.error("""
    Low productivity detected.

    AI Suggestions:
    • Minimize idle time immediately
    • Increase active working hours
    • Improve daily movement planning
    • Reduce unnecessary travel
    • Increase TP coverage
    • Monitor field activity regularly
    """)

# =========================================================
# DETAIL TABLE
# =========================================================

st.subheader("📋 Detailed Data")

st.dataframe(
    df,
    use_container_width=True
)

# =========================================================
# DOWNLOAD
# =========================================================

csv = df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "⬇ Download Report",
    csv,
    "tracking_report.csv",
    "text/csv"
)
