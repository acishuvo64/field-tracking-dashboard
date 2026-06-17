import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Field Tracking Dashboard", layout="wide")

st.title("📊 Field Tracking Power BI Dashboard")

# ================= LOGIN SYSTEM (FIXED) =================


def login():
    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Username").strip().lower()
    password = st.sidebar.text_input("Password", type="password").strip()

    if st.sidebar.button("Login"):
        if username == "shuvo" and password == "shuvo":
            st.session_state["user"] = username
            st.session_state["role"] = "Admin"
            st.success("Login Successful ✔ Welcome Shuvo")
        else:
            st.error("❌ Invalid credentials")


login()

if "user" not in st.session_state:
    st.stop()

# ================= FILE UPLOAD =================
uploaded_file = st.file_uploader(
    "Upload Excel File (.xlsx)", type=["xlsx", "xls"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # ================= SAFE CHECK =================
    required = ["Employee Name", "Total Working Hr",
                "Total Idle Hr", "Total Travel Hr", "Total Tp Visit"]

    missing = [c for c in required if c not in df.columns]

    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    # ================= DATE FIX =================
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # ================= NUMERIC CLEAN =================
    num_cols = ["Total Working Hr", "Total Idle Hr",
                "Total Travel Hr", "Total Tp Visit"]

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ================= KPI CALC =================
    df["Travel %"] = (df["Total Travel Hr"] /
                      df["Total Working Hr"].replace(0, np.nan)) * 100
    df["Idle %"] = (df["Total Idle Hr"] /
                    df["Total Working Hr"].replace(0, np.nan)) * 100
    df["Work Productivity"] = 100 - df["Idle %"].fillna(0)
    df["TP Visit %"] = (df["Total Tp Visit"] / 20) * 100
    df.fillna(0, inplace=True)

    # ================= SIDEBAR FILTER =================
    st.sidebar.header("Filters")

    if "Group" in df.columns:
        group_filter = st.sidebar.multiselect(
            "Group", df["Group"].dropna().unique())
        if group_filter:
            df = df[df["Group"].isin(group_filter)]

    if "Deg" in df.columns:
        deg_filter = st.sidebar.multiselect(
            "Designation", df["Deg"].dropna().unique())
        if deg_filter:
            df = df[df["Deg"].isin(deg_filter)]

    # ================= KPI CARDS =================
    st.subheader("📌 Executive KPI Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Employees", df["Employee Name"].nunique())
    col2.metric("Total Visits", int(df["Total Tp Visit"].sum()))
    col3.metric("Avg Productivity", f"{df['Work Productivity'].mean():.2f}%")
    col4.metric("Avg Idle %", f"{df['Idle %'].mean():.2f}%")

    st.divider()

    # ================= PERFORMANCE =================
    st.subheader("🏆 Performance Leaderboard")

    emp = df.groupby("Employee Name").agg({
        "Total Tp Visit": "sum",
        "Work Productivity": "mean"
    }).reset_index()

    top = emp.sort_values("Total Tp Visit", ascending=False).head(10)
    bottom = emp.sort_values("Total Tp Visit").head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Top 10 Performers")
        st.dataframe(top, use_container_width=True)

    with col2:
        st.markdown("### 🔴 Bottom 5 Performers")
        st.dataframe(bottom, use_container_width=True)

    st.divider()

    # ================= GROUP ANALYSIS =================
    if "Group" in df.columns:
        st.subheader("👥 Group Analysis")

        group = df.groupby("Group").agg({
            "Total Tp Visit": "sum",
            "Work Productivity": "mean"
        }).reset_index()

        fig1 = px.bar(group, x="Group", y="Total Tp Visit", text_auto=True)
        st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ================= DESIGNATION =================
    if "Deg" in df.columns:
        st.subheader("👔 Designation Analysis")

        deg = df.groupby("Deg").agg({
            "Total Tp Visit": "sum",
            "Work Productivity": "mean"
        }).reset_index()

        fig2 = px.bar(deg, x="Deg", y="Work Productivity", color="Deg")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ================= TREND =================
    if "Date" in df.columns:
        st.subheader("📈 Trend Analysis")

        trend = df.groupby(["Date", "Employee Name"])[
            "Total Tp Visit"].sum().reset_index()

        fig3 = px.line(trend, x="Date", y="Total Tp Visit",
                       color="Employee Name")
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ================= TARGET =================
    st.subheader("🎯 20 Visit Target Analysis")

    df["Visit Gap"] = 20 - df["Total Tp Visit"]

    fig4 = px.bar(df, x="Employee Name", y="Visit Gap")
    st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ================= RAW DATA =================
    st.subheader("📄 Raw Data")
    st.dataframe(df, use_container_width=True)

else:
    st.info("Please upload Excel file to start dashboard")
