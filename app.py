import streamlit as st
import pandas as pd
import numpy as np

# -----------------------------
# Page Config
# -----------------------------

st.set_page_config(
    page_title="AIM³ Aftermarket Intelligence",
    layout="wide"
)

# -----------------------------
# Load Custom CSS
# -----------------------------

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# NBC Logo Header
col1, col2 = st.columns([1,8])
with col1:
    st.image("nbc_logo.png", width=120)

# -----------------------------
# Generate Synthetic Dataset
# -----------------------------

np.random.seed(42)

regions = ["North", "South", "East", "West"]
dealers = [f"Dealer_{i}" for i in range(1,21)]
bearings = ["6205", "6206", "6305", "6306", "NU205"]

data = []

for i in range(1000):

    region = np.random.choice(regions)
    dealer = np.random.choice(dealers)
    bearing = np.random.choice(bearings)

    failure_prob = np.round(np.random.rand(),2)
    adps = np.round(np.random.rand(),2)
    rul = np.random.randint(5,120)
    inventory = np.random.randint(10,150)
    demand = np.random.randint(20,200)

    price = np.random.randint(500,3000)

    data.append([
        region,dealer,f"M{i}",bearing,
        failure_prob,adps,rul,inventory,demand,price
    ])

df = pd.DataFrame(data,columns=[
    "Region","Dealer","Machine","Bearing",
    "Failure Probability","ADPS",
    "RUL","Inventory","Predicted Demand","Price"
])

# -----------------------------
# AI Scores
# -----------------------------

df["OVS"] = df["Predicted Demand"] * df["Price"]

df["Demand Score"] = (
    df["ADPS"]*0.6 +
    df["Failure Probability"]*0.4
).round(2)

df["Inventory Gap"] = df["Predicted Demand"] - df["Inventory"]

# -----------------------------
# Login
# -----------------------------

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("AIM³ Predictive Aftermarket Intelligence")

    user = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):
        st.session_state.login = True
        st.rerun()

    st.stop()

# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("AIM³ Navigation")

# Optional logo
# st.sidebar.image("nbc_logo.png", width=150)

page = st.sidebar.radio(
    "Go to",
    [
        "Global Dashboard",
        "Region Explorer",
        "Demand Intelligence",
        "Inventory Planning",
        "Notifications"
    ]
)

# -----------------------------
# Global Dashboard
# -----------------------------

if page == "Global Dashboard":

    st.title("AIM³ Global Aftermarket Dashboard")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Machines Monitored",len(df))
    col2.metric("High Failure Risk",(df["Failure Probability"]>0.7).sum())
    col3.metric("High Demand Bearings",(df["ADPS"]>0.7).sum())
    col4.metric("Inventory Risk",(df["Inventory Gap"]>0).sum())

    st.subheader("Regional Demand Overview")

    region_summary = df.groupby("Region")["Predicted Demand"].sum().reset_index()

    st.bar_chart(region_summary,x="Region",y="Predicted Demand")

    st.subheader("Top Opportunity Regions")

    ovs_region = df.groupby("Region")["OVS"].sum().reset_index()

    st.bar_chart(ovs_region,x="Region",y="OVS")

    st.subheader("Sample Dataset")

    st.dataframe(df.head(20),use_container_width=True)

# -----------------------------
# Region Explorer
# -----------------------------

if page == "Region Explorer":

    st.title("Region Market Explorer")

    region = st.selectbox("Select Region",df["Region"].unique())

    region_df = df[df["Region"]==region]

    st.subheader(f"{region} Market Overview")

    col1,col2,col3 = st.columns(3)

    col1.metric("Dealers",region_df["Dealer"].nunique())
    col2.metric("Machines",len(region_df))
    col3.metric("High Demand",(region_df["ADPS"]>0.7).sum())

    st.divider()

    st.subheader("Filters")

    failure_filter = st.selectbox(
        "Failure Risk",
        ["All","High","Medium","Low"]
    )

    demand_filter = st.selectbox(
        "Demand Probability",
        ["All","High","Medium","Low"]
    )

    filtered = region_df.copy()

    if failure_filter == "High":
        filtered = filtered[filtered["Failure Probability"]>0.7]

    if failure_filter == "Medium":
        filtered = filtered[
            (filtered["Failure Probability"]>0.4) &
            (filtered["Failure Probability"]<=0.7)
        ]

    if failure_filter == "Low":
        filtered = filtered[filtered["Failure Probability"]<=0.4]

    if demand_filter == "High":
        filtered = filtered[filtered["ADPS"]>0.7]

    if demand_filter == "Medium":
        filtered = filtered[
            (filtered["ADPS"]>0.4) &
            (filtered["ADPS"]<=0.7)
        ]

    if demand_filter == "Low":
        filtered = filtered[filtered["ADPS"]<=0.4]

    st.subheader("Machines & Bearings Insights")

    st.dataframe(filtered,use_container_width=True)

# -----------------------------
# Demand Intelligence
# -----------------------------

if page == "Demand Intelligence":

    st.title("AIM³ Demand Intelligence Engine")

    st.subheader("Regional Demand Trend")

    trend = df.groupby("Region")[["ADPS","Predicted Demand","OVS"]].mean().reset_index()

    st.bar_chart(trend,x="Region",y="Predicted Demand")

    st.divider()

    region = st.selectbox("Select Region for Dealer Analysis",df["Region"].unique())

    region_df = df[df["Region"]==region]

    dealer_summary = region_df.groupby("Dealer").agg({
        "Predicted Demand":"sum",
        "ADPS":"mean",
        "OVS":"sum"
    }).reset_index()

    dealer_summary = dealer_summary.sort_values(
        "Predicted Demand",
        ascending=False
    )

    st.subheader("Dealers Likely to Generate Demand")

    st.dataframe(dealer_summary,use_container_width=True)

    st.divider()

    dealer = st.selectbox("Select Dealer",dealer_summary["Dealer"])

    dealer_data = region_df[region_df["Dealer"]==dealer]

    st.subheader(f"Dealer Intelligence: {dealer}")

    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "Total Demand",
        int(dealer_data["Predicted Demand"].sum())
    )

    col2.metric(
        "Average ADPS",
        round(dealer_data["ADPS"].mean(),2)
    )

    col3.metric(
        "Opportunity Value",
        int(dealer_data["OVS"].sum())
    )

    col4.metric(
        "Machines Installed",
        dealer_data["Machine"].nunique()
    )

    st.divider()

    st.subheader("Machine Level Demand Signals")

    st.dataframe(dealer_data,use_container_width=True)

    st.divider()

    avg_score = dealer_data["Demand Score"].mean()

    st.subheader("AIM³ AI Final Judgement")

    if avg_score > 0.7:
        st.success("HIGH PROBABILITY DEALER – Immediate Sales Outreach Recommended")

    elif avg_score > 0.4:
        st.warning("MEDIUM DEMAND – Monitor Dealer Engagement")

    else:
        st.info("LOW DEMAND – No Immediate Action Required")

    st.divider()

    st.subheader("Action Center")

    col1,col2,col3,col4 = st.columns(4)

    if col1.button("Send to Sales Team"):
        st.success(f"Sales team notified for dealer {dealer}")

    if col2.button("Generate Lead"):
        st.success("CRM lead generated successfully")

    if col3.button("Trigger Notification"):
        st.warning("Dealer demand alert triggered")

    if col4.button("Check Inventory"):

        stock = dealer_data["Inventory"].sum()
        demand = dealer_data["Predicted Demand"].sum()

        if demand > stock:
            st.error("Inventory Shortage Detected")
        else:
            st.success("Inventory Sufficient")

# -----------------------------
# Inventory Planning
# -----------------------------

if page == "Inventory Planning":

    st.title("Smart Inventory Planning")

    risk = df[df["Inventory Gap"]>0]

    st.metric("Regions with Shortage",risk["Region"].nunique())

    summary = risk.groupby(["Region","Bearing"])["Inventory Gap"].sum().reset_index()

    st.dataframe(summary,use_container_width=True)

    st.bar_chart(summary,x="Region",y="Inventory Gap")

# -----------------------------
# Notifications
# -----------------------------

if page == "Notifications":

    st.title("AIM³ Notification Center")

    alerts = df[
        (df["Failure Probability"]>0.7) &
        (df["ADPS"]>0.7)
    ]

    for _,row in alerts.head(10).iterrows():

        st.error(
            f"""
HIGH ALERT  

Machine: {row['Machine']}  
Bearing: {row['Bearing']}  
Region: {row['Region']}  

Failure Probability: {row['Failure Probability']}  
Demand Probability: {row['ADPS']}  
Opportunity Value: ₹{row['OVS']}
"""
        )