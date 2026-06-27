# =========================================================
# AI FIELD FORCE DASHBOARD - ACI Premio Plastics
# Shahinur | Sales Admin
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import base64
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Field Force Dashboard",
    page_icon="📍",
    layout="wide"
)

# =========================================================
# LOGO HELPER
# =========================================================


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


premio_b64 = img_to_base64("ACI_Premio_Plastics_Ltd_.jpg")
aci_b64 = img_to_base64("ACI.png")

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 42px;
    font-weight: 900;
    background: linear-gradient(90deg, #6366F1, #EC4899, #F59E0B, #10B981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2px;
}

.sub-title {
    font-size: 15px;
    color: #64748B;
    margin-bottom: 8px;
}

.kpi-blue {
    background: linear-gradient(135deg, #4F46E5, #818CF8);
    padding: 22px 10px; border-radius: 16px; color: white;
    text-align: center; box-shadow: 0 6px 18px rgba(79,70,229,0.35);
    min-height: 115px;
}
.kpi-green {
    background: linear-gradient(135deg, #059669, #34D399);
    padding: 22px 10px; border-radius: 16px; color: white;
    text-align: center; box-shadow: 0 6px 18px rgba(5,150,105,0.35);
    min-height: 115px;
}
.kpi-cyan {
    background: linear-gradient(135deg, #0284C7, #38BDF8);
    padding: 22px 10px; border-radius: 16px; color: white;
    text-align: center; box-shadow: 0 6px 18px rgba(2,132,199,0.35);
    min-height: 115px;
}
.kpi-orange {
    background: linear-gradient(135deg, #D97706, #FCD34D);
    padding: 22px 10px; border-radius: 16px; color: white;
    text-align: center; box-shadow: 0 6px 18px rgba(217,119,6,0.35);
    min-height: 115px;
}
.kpi-pink {
    background: linear-gradient(135deg, #DB2777, #F9A8D4);
    padding: 22px 10px; border-radius: 16px; color: white;
    text-align: center; box-shadow: 0 6px 18px rgba(219,39,119,0.35);
    min-height: 115px;
}
.kpi-blue h4, .kpi-green h4, .kpi-cyan h4,
.kpi-orange h4, .kpi-pink h4 {
    margin: 0 0 8px 0; font-size: 13px; font-weight: 600; opacity: 0.9;
}
.kpi-blue h2, .kpi-green h2, .kpi-cyan h2,
.kpi-orange h2, .kpi-pink h2 {
    margin: 0; font-size: 30px; font-weight: 900;
}

.photo-card {
    background: linear-gradient(135deg, #1E293B, #334155);
    border-radius: 16px; padding: 20px; text-align: center;
    color: white; box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}

/* ── Sidebar dark theme ── */
[data-testid="stSidebar"] {
    background: #0F172A !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div {
    color: white !important;
    font-weight: 600;
}

/* sidebar logo area */
.sidebar-logo-box {
    background: white;
    border-radius: 12px;
    padding: 10px;
    margin-bottom: 10px;
    text-align: center;
}
.sidebar-aci-box {
    text-align: center;
    margin-bottom: 18px;
}

/* header logo */
.header-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR LOGOS
# =========================================================

st.sidebar.markdown(
    f"""
    <div class="sidebar-logo-box">
        <img src="data:image/jpeg;base64,{premio_b64}"
             style="width:100%;max-width:200px;height:auto;border-radius:8px;">
    </div>
    <div class="sidebar-aci-box">
        <img src="data:image/png;base64,{aci_b64}"
             style="width:64px;height:64px;border-radius:50%;border:3px solid #10B981;">
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("🎛 Dashboard Filters")

# =========================================================
# LOAD DATA
# =========================================================


@st.cache_data
def load_data():
    summary = pd.read_excel("super_tracking_report.xlsx",
                            sheet_name="Summarize_data")
    image_df = pd.read_excel(
        "super_tracking_report.xlsx", sheet_name="Image_URL")
    raw_df = pd.read_excel("super_tracking_report.xlsx",
                           sheet_name="Overall _Raw_data")
    summary["Date"] = pd.to_datetime(summary["Date"], errors="coerce")
    raw_df["Date"] = pd.to_datetime(raw_df["Date"],  errors="coerce")
    raw_df["Latitude"] = pd.to_numeric(raw_df["Latitude"],  errors="coerce")
    raw_df["Longitude"] = pd.to_numeric(raw_df["Longitude"], errors="coerce")
    return summary, image_df, raw_df


try:
    summary_df, image_df, raw_df = load_data()
except Exception as e:
    st.error(f"Excel Loading Error: {e}")
    st.stop()

image_dict = dict(zip(image_df["Employee Name"], image_df["Image"]))

# =========================================================
# SIDEBAR FILTERS
# =========================================================

start_date = st.sidebar.date_input("📅 Start Date", summary_df["Date"].min())
end_date = st.sidebar.date_input("📅 End Date",   summary_df["Date"].max())

group_list = sorted(summary_df["Group"].dropna().unique())
selected_group = st.sidebar.selectbox("🏷 Select Group", ["All"] + group_list)

deg_list = sorted(summary_df["Deg"].dropna().unique())
selected_deg = st.sidebar.selectbox(
    "👔 Select Designation (RSM/TSM)", ["All"] + deg_list)

employee_list = sorted(summary_df["Employee Name"].dropna().unique())
selected_employee = st.sidebar.selectbox(
    "👤 Select Employee", ["All"] + employee_list)

# =========================================================
# HEADER — ACI Logo + Title
# =========================================================

h_left, h_right = st.columns([5, 1])

with h_left:
    st.markdown('<p class="main-title">📍 AI Field Force Tracking Dashboard</p>',
                unsafe_allow_html=True)
    st.markdown('<p class="sub-title">ACI Premio Plastics — Professional Employee Tracking & Productivity Analytics</p>', unsafe_allow_html=True)

with h_right:
    st.markdown(
        f"""
        <div style="text-align:right; padding-top:6px;">
            <img src="data:image/png;base64,{aci_b64}"
                 style="width:72px;height:72px;border-radius:50%;
                        border:3px solid #10B981;
                        box-shadow:0 4px 12px rgba(0,0,0,0.2);">
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================================================
# FILTER DATA
# =========================================================

df = summary_df.copy()
df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
]
if selected_group != "All":
    df = df[df["Group"] == selected_group]
if selected_deg != "All":
    df = df[df["Deg"] == selected_deg]
if selected_employee != "All":
    df = df[df["Employee Name"] == selected_employee]

# =========================================================
# KPI CARDS
# =========================================================

total_emp = df["Employee Name"].nunique()
total_working = round(df["Total Working Hr"].sum(), 1)
total_travel = round(df["Total Travel Hr"].sum(), 1)
total_idle = round(df["Total Idle Hr"].sum(), 1)
avg_productivity = round(df["Work productivity"].mean() * 100, 1)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(
        f'<div class="kpi-blue"><h4>👥 Employee</h4><h2>{total_emp}</h2></div>', unsafe_allow_html=True)
with c2:
    st.markdown(
        f'<div class="kpi-green"><h4>⏱ Working Hr</h4><h2>{total_working}</h2></div>', unsafe_allow_html=True)
with c3:
    st.markdown(
        f'<div class="kpi-cyan"><h4>🚗 Travel Hr</h4><h2>{total_travel}</h2></div>', unsafe_allow_html=True)
with c4:
    st.markdown(
        f'<div class="kpi-orange"><h4>💤 Idle Hr</h4><h2>{total_idle}</h2></div>', unsafe_allow_html=True)
with c5:
    st.markdown(
        f'<div class="kpi-pink"><h4>📊 Productivity %</h4><h2>{avg_productivity}%</h2></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================
# SECTION 1: EMPLOYEE PROFILE + PHOTO
# =========================================================

st.subheader("📸 Employee Profile")

photo_col, info_col = st.columns([1, 3])

with photo_col:
    if selected_employee != "All":
        img_url = image_dict.get(selected_employee, None)
        emp_info = df[df["Employee Name"] == selected_employee]
        deg_val = emp_info["Deg"].iloc[0] if not emp_info.empty else "-"
        group_val = emp_info["Group"].iloc[0] if not emp_info.empty else "-"

        photo_html = (
            f'<img src="{img_url}" width="150" height="150" '
            f'style="border-radius:50%;object-fit:cover;border:4px solid #6366F1;margin-bottom:10px;" '
            f'onerror="this.style.display=\'none\'">'
            if img_url else '<div style="font-size:64px;margin-bottom:10px;">👤</div>'
        )

        st.markdown(f"""
        <div class="photo-card">
            {photo_html}
            <h3 style="margin:6px 0 4px 0;font-size:15px;">{selected_employee}</h3>
            <p style="margin:0;font-size:13px;opacity:0.8;">{deg_val} | {group_val}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="photo-card">
            <div style="font-size:54px;padding:16px;">👥</div>
            <p style="opacity:0.7;margin:0;">Select an employee<br>to view profile</p>
        </div>
        """, unsafe_allow_html=True)

with info_col:
    if selected_employee != "All" and not df.empty:
        ei = df[df["Employee Name"] == selected_employee]
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        with mc1:
            st.metric("📅 Working Days",   ei["Date"].nunique())
        with mc2:
            st.metric("⏱ Working Hr",  round(ei["Total Working Hr"].sum(), 1))
        with mc3:
            st.metric("🚗 Travel Hr",   round(ei["Total Travel Hr"].sum(), 1))
        with mc4:
            st.metric("💤 Idle Hr",     round(ei["Total Idle Hr"].sum(), 1))
        with mc5:
            st.metric("📊 Productivity",
                      f"{round(ei['Work productivity'].mean()*100,1)}%")
    else:
        st.info(
            "📌 Select a specific employee from the sidebar to view individual stats.")

st.markdown("---")

# =========================================================
# SECTION 2: PIE CHART — DAY WISE / FULL MONTH
# =========================================================

st.subheader("🥧 Employee Hours Breakdown (Working / Travel / Idle)")

col_e, col_m = st.columns([2, 2])
with col_e:
    pie_emp = st.selectbox("Select Employee", employee_list, key="pie_emp")
with col_m:
    pie_mode = st.radio(
        "View Mode", ["Day Wise", "Full Month"], horizontal=True)

emp_pie_df = summary_df[
    (summary_df["Employee Name"] == pie_emp) &
    (summary_df["Date"] >= pd.to_datetime(start_date)) &
    (summary_df["Date"] <= pd.to_datetime(end_date))
].copy()

if emp_pie_df.empty:
    st.warning("No data found for selected employee.")
else:
    if pie_mode == "Day Wise":
        available_dates = sorted(emp_pie_df["Date"].dt.date.unique())
        selected_day = st.selectbox(
            "Select Date", available_dates, key="pie_date")
        pie_data = emp_pie_df[emp_pie_df["Date"].dt.date == selected_day]
        pie_title = f"{pie_emp}  —  {selected_day}"
    else:
        pie_data = emp_pie_df
        pie_title = f"{pie_emp}  —  Full Month"

    w = round(pie_data["Total Working Hr"].sum(), 2)
    t = round(pie_data["Total Travel Hr"].sum(), 2)
    i = round(pie_data["Total Idle Hr"].sum(), 2)

    if (w + t + i) > 0:
        fig_pie = px.pie(
            pd.DataFrame({
                "Category": ["Working Hr", "Travel Hr", "Idle Hr"],
                "Hours":    [w, t, i]
            }),
            names="Category", values="Hours",
            hole=0.45, template="plotly_dark",
            color="Category",
            color_discrete_map={
                "Working Hr": "#4F46E5",
                "Travel Hr":  "#06B6D4",
                "Idle Hr":    "#F59E0B"
            },
            title=pie_title
        )
        fig_pie.update_traces(textinfo="percent+label+value")
        fig_pie.update_layout(title_font_size=16)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No hours data available.")

st.markdown("---")

# =========================================================
# SECTION 3: RSM vs TSM PERFORMANCE
# =========================================================

st.subheader("👔 RSM vs TSM Performance Comparison")

deg_df = (
    df.groupby(["Employee Name", "Deg"])["Work productivity"]
    .mean().reset_index()
)
deg_df["Work productivity"] = (deg_df["Work productivity"] * 100).round(1)
deg_df = deg_df.sort_values("Work productivity", ascending=False)

fig_deg = px.bar(
    deg_df,
    x="Employee Name", y="Work productivity",
    color="Deg", text_auto=".1f", barmode="group",
    template="plotly_dark",
    color_discrete_map={"RSM": "#4F46E5", "TSM": "#06B6D4"},
    title="Productivity % by Employee — RSM vs TSM"
)
fig_deg.update_layout(
    yaxis_title="Productivity %",
    xaxis_tickangle=-45,
    legend_title="Designation"
)
st.plotly_chart(fig_deg, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 4: TOP 10 PERFORMERS
# =========================================================

st.subheader("🏆 Top 10 Performers")

top10 = (
    df.groupby("Employee Name")["Work productivity"]
    .mean().reset_index()
    .sort_values("Work productivity", ascending=False)
    .head(10)
)
top10["Work productivity"] = (top10["Work productivity"] * 100).round(1)
top10 = top10.sort_values("Work productivity", ascending=True)

fig_top = px.bar(
    top10,
    x="Work productivity", y="Employee Name",
    orientation="h", text_auto=".1f",
    template="plotly_dark",
    color="Work productivity",
    color_continuous_scale="Viridis",
    title="Top 10 Performers by Productivity %"
)
fig_top.update_layout(
    xaxis_title="Productivity %",
    yaxis_title="",
    coloraxis_showscale=False
)
st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 5: BOTTOM 10 PERFORMERS
# =========================================================

st.subheader("⚠️ Bottom 10 Performers")

bottom10 = (
    df.groupby("Employee Name")["Work productivity"]
    .mean().reset_index()
    .sort_values("Work productivity", ascending=True)
    .head(10)
)
bottom10["Work productivity"] = (bottom10["Work productivity"] * 100).round(1)
bottom10 = bottom10.sort_values("Work productivity", ascending=False)

fig_bot = px.bar(
    bottom10,
    x="Work productivity", y="Employee Name",
    orientation="h", text_auto=".1f",
    template="plotly_dark",
    color="Work productivity",
    color_continuous_scale="Reds_r",
    title="Bottom 10 Performers by Productivity %"
)
fig_bot.update_layout(
    xaxis_title="Productivity %",
    yaxis_title="",
    coloraxis_showscale=False
)
st.plotly_chart(fig_bot, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 6: DAILY PRODUCTIVITY TREND
# =========================================================

st.subheader("📈 Daily Productivity Trend")

daily = df.groupby("Date")["Work productivity"].mean().reset_index()
daily["Work productivity"] = (daily["Work productivity"] * 100).round(1)

fig_trend = px.line(
    daily, x="Date", y="Work productivity",
    markers=True, template="plotly_dark",
    title="Daily Average Productivity %"
)
fig_trend.update_layout(yaxis_title="Productivity %")
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 7: WORKING vs TRAVEL vs IDLE
# =========================================================

st.subheader("⚡ Working vs Travel vs Idle Hours by Employee")

compare_df = (
    df.groupby("Employee Name")[
        ["Total Working Hr", "Total Travel Hr", "Total Idle Hr"]]
    .sum().reset_index()
)
fig_cmp = px.bar(
    compare_df,
    x="Employee Name",
    y=["Total Working Hr", "Total Travel Hr", "Total Idle Hr"],
    barmode="group", template="plotly_dark",
    color_discrete_map={
        "Total Working Hr": "#4F46E5",
        "Total Travel Hr":  "#06B6D4",
        "Total Idle Hr":    "#F59E0B"
    },
    title="Hours Comparison per Employee"
)
fig_cmp.update_layout(xaxis_tickangle=-45, yaxis_title="Hours")
st.plotly_chart(fig_cmp, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 8: GPS ROUTE MAP
# =========================================================

st.subheader("🗺 Employee GPS Route Map")

if selected_employee != "All":

    map_src = raw_df[
        (raw_df["Employee Name"] == selected_employee) &
        (raw_df["Date"] >= pd.to_datetime(start_date)) &
        (raw_df["Date"] <= pd.to_datetime(end_date))
    ].dropna(subset=["Latitude", "Longitude"]).copy()

    if map_src.empty:
        st.warning(
            "No GPS data found for this employee in the selected date range.")
    else:
        map_dates = sorted(map_src["Date"].dt.date.unique())
        selected_map_date = st.selectbox(
            "📅 Select Date for GPS Map",
            ["All Dates"] + [str(d) for d in map_dates],
            key="map_date"
        )

        if selected_map_date != "All Dates":
            map_src = map_src[map_src["Date"].dt.date ==
                              pd.to_datetime(selected_map_date).date()]

        if map_src.empty:
            st.warning("No GPS data for selected date.")
        else:
            center_lat = map_src["Latitude"].mean()
            center_lon = map_src["Longitude"].mean()

            m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

            # Route line
            coords = list(zip(map_src["Latitude"], map_src["Longitude"]))
            if len(coords) > 1:
                folium.PolyLine(
                    coords, color="#6366F1",
                    weight=3, opacity=0.7, tooltip="Route"
                ).add_to(m)

            # Clustered markers
            cluster = MarkerCluster().add_to(m)
            status_color = {"Travelling": "blue", "Idling / Stop": "red"}

            for _, row in map_src.iterrows():
                color = status_color.get(row["Status"], "gray")
                addr = str(row.get(" Address / Diagnostic report", "")).strip()
                popup = f"""
                <b>{row['Employee Name']}</b><br>
                📅 {row['Date'].date()}<br>
                📍 {addr[:70] if addr else 'N/A'}<br>
                🔵 Status: {row['Status']}
                """
                folium.CircleMarker(
                    location=[row["Latitude"], row["Longitude"]],
                    radius=5, color=color, fill=True,
                    fill_color=color, fill_opacity=0.8,
                    popup=folium.Popup(popup, max_width=260),
                    tooltip=row["Status"]
                ).add_to(cluster)

            # Start & End markers
            folium.Marker(
                [map_src.iloc[0]["Latitude"], map_src.iloc[0]["Longitude"]],
                popup="🟢 Start Point",
                tooltip="Start",
                icon=folium.Icon(color="green", icon="play")
            ).add_to(m)

            folium.Marker(
                [map_src.iloc[-1]["Latitude"], map_src.iloc[-1]["Longitude"]],
                popup="🔴 End Point",
                tooltip="End",
                icon=folium.Icon(color="red", icon="stop")
            ).add_to(m)

            # Legend
            m.get_root().html.add_child(folium.Element("""
            <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                        background:white;padding:12px 16px;border-radius:10px;
                        box-shadow:0 2px 10px rgba(0,0,0,0.3);font-size:13px;">
                <b>Legend</b><br>
                <span style="color:blue;">●</span> Travelling<br>
                <span style="color:red;">●</span> Idling / Stop<br>
                <span style="color:green;">▶</span> Start Point<br>
                <span style="color:red;">■</span> End Point
            </div>
            """))

            total_pts = len(map_src)
            travel_pts = len(map_src[map_src["Status"] == "Travelling"])
            idle_pts = len(map_src[map_src["Status"] == "Idling / Stop"])

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("📍 Total GPS Points", total_pts)
            with mc2:
                st.metric("🚗 Travelling Points", travel_pts)
            with mc3:
                st.metric("💤 Idling Points", idle_pts)

            st_folium(m, width=1200, height=550)

else:
    st.info("📌 Select a specific employee from the sidebar to view GPS route map.")

st.markdown("---")

# =========================================================
# SECTION 9: AI PERFORMANCE SUGGESTION
# =========================================================

st.subheader("🤖 AI Performance Suggestion")

if avg_productivity >= 75:
    st.success(f"""✅ **Excellent Performance! ({avg_productivity}%)**
- Maintain current field activity levels
- Increase TP visits slightly for further growth
- Share best practices with lower performers
- Consider for recognition or incentive programs""")
elif avg_productivity >= 50:
    st.warning(f"""⚠️ **Average Performance ({avg_productivity}%)**
- Reduce idle hours through better route planning
- Increase outlet visit frequency daily
- Review travel routes for efficiency
- Set daily working targets per employee""")
else:
    st.error(f"""🚨 **Low Performance Detected ({avg_productivity}%)**
- Minimize idle time immediately
- Increase active working hours
- Improve daily movement & route planning
- Reduce unnecessary travel stops
- Increase TP coverage targets
- Monitor field activity with daily check-ins""")

st.markdown("---")

# =========================================================
# SECTION 10: DETAIL TABLE + DOWNLOAD
# =========================================================

st.subheader("📋 Detailed Data Table")

display_df = df.copy()
display_df["Date"] = display_df["Date"].dt.date
display_df["Work productivity"] = (
    display_df["Work productivity"] * 100).round(1)
display_df = display_df.rename(columns={"Work productivity": "Productivity %"})
st.dataframe(display_df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download Filtered Report (CSV)",
    csv,
    "field_force_report.csv",
    "text/csv"
)

# =========================================================
# FOOTER
# =========================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align:center; padding:20px 0 10px 0; opacity:0.6;">
        <img src="data:image/jpeg;base64,{premio_b64}"
             style="height:40px; margin-right:16px; vertical-align:middle; border-radius:4px;">
        <img src="data:image/png;base64,{aci_b64}"
             style="height:40px; vertical-align:middle; border-radius:50%;">
        <p style="font-size:12px; margin-top:8px; color:#64748B;">
            © ACI Premio Plastics Ltd. | AI Field Force Dashboard
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
