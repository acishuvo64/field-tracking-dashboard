import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

.section-box{
    background-color:#F8FAFC;
    padding:15px;
    border-radius:15px;
    margin-top:10px;
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
# FILE UPLOAD
# =========================================================
uploaded_file = st.file_uploader(
    "📂 Upload Excel File",
    type=["xlsx"]
)

# =========================================================
# MAIN APP
# =========================================================
if uploaded_file:

    # =====================================================
    # READ SHEETS
    # =====================================================
    summary_df = pd.read_excel(
        uploaded_file,
        sheet_name="Summarize_data"
    )

    image_df = pd.read_excel(
        uploaded_file,
        sheet_name="Image_URL"
    )

    # =====================================================
    # DATE FORMAT
    # =====================================================
    summary_df["Date"] = pd.to_datetime(
        summary_df["Date"],
        errors="coerce"
    )

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================
    st.sidebar.title("🎛 Dashboard Filters")

    # Employee Filter
    employee_list = sorted(
        summary_df["Employee Name"].dropna().unique()
    )

    selected_employee = st.sidebar.selectbox(
        "Select Employee",
        ["All"] + employee_list
    )

    # Group Filter
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

    # Designation Filter
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

    # Date Filter
    start_date = st.sidebar.date_input(
        "Start Date",
        summary_df["Date"].min()
    )

    end_date = st.sidebar.date_input(
        "End Date",
        summary_df["Date"].max()
    )

    # =====================================================
    # FILTER DATA
    # =====================================================
    filtered_df = summary_df.copy()

    # Employee
    if selected_employee != "All":
        filtered_df = filtered_df[
            filtered_df["Employee Name"] == selected_employee
        ]

    # Group
    if selected_group != "All":
        filtered_df = filtered_df[
            filtered_df["Group"] == selected_group
        ]

    # Designation
    if selected_deg != "All":
        filtered_df = filtered_df[
            filtered_df["Deg"] == selected_deg
        ]

    # Date
    filtered_df = filtered_df[
        (filtered_df["Date"] >= pd.to_datetime(start_date)) &
        (filtered_df["Date"] <= pd.to_datetime(end_date))
    ]

    # =====================================================
    # KPI SECTION
    # =====================================================
    total_emp = filtered_df["Employee Name"].nunique()

    total_visit = filtered_df["Total Tp Visit"].sum()

    total_working = filtered_df["Total Working Hr"].sum()

    total_travel = filtered_df["Total Travel Hr"].sum()

    total_idle = filtered_df["Total Idle Hr"].sum()

    avg_productivity = filtered_df["Work productivity"].mean()

    st.markdown("---")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>Total Employee</h4>
            <h2>{total_emp}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>Total TP Visit</h4>
            <h2>{round(total_visit,0)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>Total Working Hr</h4>
            <h2>{round(total_working,2)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>Total Travel Hr</h4>
            <h2>{round(total_travel,2)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>Total Idle Hr</h4>
            <h2>{round(total_idle,2)}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>Avg Productivity</h4>
            <h2>{round(avg_productivity,2)}</h2>
        </div>
        """, unsafe_allow_html=True)

    # =====================================================
    # TOP PERFORMER
    # =====================================================
    st.markdown("---")

    top_emp = filtered_df.sort_values(
        by="Work productivity",
        ascending=False
    ).head(1)

    if len(top_emp) > 0:

        emp_name = top_emp.iloc[0]["Employee Name"]
        emp_prod = top_emp.iloc[0]["Work productivity"]

        st.success(
            f"🏆 Top Performer: {emp_name} | Productivity: {round(emp_prod,2)}"
        )

    # =====================================================
    # EMPLOYEE IMAGE
    # =====================================================
    if selected_employee != "All":

        emp_img = image_df[
            image_df["Employee Name"] == selected_employee
        ]

        if len(emp_img) > 0:

            if "Image" in emp_img.columns:

                img_url = emp_img.iloc[0]["Image"]

                st.image(
                    img_url,
                    width=180
                )

    # =====================================================
    # PRODUCTIVITY BAR CHART
    # =====================================================
    st.markdown("---")

    st.subheader("🏆 Employee Productivity Ranking")

    productivity_data = filtered_df.groupby(
        "Employee Name",
        as_index=False
    )["Work productivity"].mean()

    fig_bar = px.bar(
        productivity_data,
        x="Employee Name",
        y="Work productivity",
        color="Work productivity",
        text_auto=True
    )

    fig_bar.update_layout(
        height=600,
        xaxis_tickangle=-90
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # =====================================================
    # DAILY PRODUCTIVITY TREND
    # =====================================================
    st.subheader("📈 Daily Productivity Trend")

    daily_data = filtered_df.groupby(
        "Date",
        as_index=False
    )["Work productivity"].mean()

    fig_line = px.line(
        daily_data,
        x="Date",
        y="Work productivity",
        markers=True
    )

    fig_line.update_layout(
        template="plotly_white",
        height=500
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

    # =====================================================
    # PIE CHART
    # =====================================================
    st.subheader("🥧 Travel vs Idle Analysis")

    pie_df = pd.DataFrame({
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

    fig_pie = px.pie(
        pie_df,
        names="Category",
        values="Value",
        hole=0.4
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

    # =====================================================
    # TOP 10 PERFORMER
    # =====================================================
    st.subheader("🔥 Top 10 Performer")

    top10 = filtered_df.groupby(
        "Employee Name",
        as_index=False
    )["Work productivity"].mean()

    top10 = top10.sort_values(
        by="Work productivity",
        ascending=False
    ).head(10)

    fig_top10 = px.bar(
        top10,
        x="Employee Name",
        y="Work productivity",
        color="Work productivity",
        text_auto=True
    )

    st.plotly_chart(
        fig_top10,
        use_container_width=True
    )

    # =====================================================
    # LOWEST 10
    # =====================================================
    st.subheader("⚠ Lowest 10 Performer")

    low10 = filtered_df.groupby(
        "Employee Name",
        as_index=False
    )["Work productivity"].mean()

    low10 = low10.sort_values(
        by="Work productivity",
        ascending=True
    ).head(10)

    fig_low10 = px.bar(
        low10,
        x="Employee Name",
        y="Work productivity",
        color="Work productivity",
        text_auto=True
    )

    st.plotly_chart(
        fig_low10,
        use_container_width=True
    )

    # =====================================================
    # GROUP COMPARISON
    # =====================================================
    if "Group" in filtered_df.columns:

        st.subheader("👥 Group Productivity Comparison")

        group_data = filtered_df.groupby(
            "Group",
            as_index=False
        )["Work productivity"].mean()

        fig_group = px.bar(
            group_data,
            x="Group",
            y="Work productivity",
            color="Work productivity",
            text_auto=True
        )

        st.plotly_chart(
            fig_group,
            use_container_width=True
        )

    # =====================================================
    # PERFORMANCE TABLE
    # =====================================================
    st.subheader("📋 Detailed Performance Table")

    st.dataframe(
        filtered_df,
        use_container_width=True
    )

    # =====================================================
    # RISK INDICATOR
    # =====================================================
    st.subheader("🚨 Risk Indicator")

    risk_df = filtered_df[
        filtered_df["Work productivity"] < 3
    ]

    st.write(
        f"Low Productivity Employees Found: {risk_df['Employee Name'].nunique()}"
    )

    st.dataframe(
        risk_df,
        use_container_width=True
    )

else:

    st.info("⬆ Please Upload Excel File")
