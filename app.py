import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.set_page_config(page_title="AIM³ Predictive Aftermarket", layout="wide")

st.title("AIM³: Aftermarket Intelligence & Monetization")
st.caption("Predictive Sales through Connected Customer Data")

# Sidebar Logo
st.sidebar.image("nbc_logo.png", width=120)

# st.sidebar.markdown("### AIM³ Navigation")
# st.sidebar.markdown("Go to")

# -------------------------------------------------------
# DATA GENERATION
# -------------------------------------------------------

np.random.seed(42)

regions = ["North","South","East","West"]
dealers = [f"Dealer_{i}" for i in range(1,21)]
bearings = ["6205","6206","6305","6306","NU205"]

data = []

for i in range(1000):

    region = np.random.choice(regions)
    dealer = np.random.choice(dealers)
    bearing = np.random.choice(bearings)

    failure_prob = np.round(np.random.rand(),2)
    demand_prob = np.round(np.random.rand(),2)

    rul = np.random.randint(5,120)

    inventory = np.random.randint(10,150)
    demand = np.random.randint(20,200)

    price = np.random.randint(500,3000)

    data.append([
        region,dealer,f"Machine_{i}",
        bearing,failure_prob,demand_prob,
        rul,inventory,demand,price
    ])

df = pd.DataFrame(data,columns=[
"Region","Dealer","Machine","Bearing",
"Failure Probability","Demand Probability",
"RUL","Inventory","Current Demand","Price"
])

# -------------------------------------------------------
# ANALYTICS
# -------------------------------------------------------

df["Next Demand"] = (df["Current Demand"]*(1+np.random.normal(0.1,0.05,len(df)))).astype(int)

df["Opportunity Value"] = df["Next Demand"] * df["Price"]

df["Inventory Gap"] = df["Next Demand"] - df["Inventory"]

df["Inventory Status"] = np.where(
df["Inventory Gap"] > 20,"Shortage",
np.where(df["Inventory Gap"] < -20,"Overstock","Balanced")
)

df["Failure Risk"] = np.where(
df["Failure Probability"] > 0.75,"Critical",
np.where(df["Failure Probability"] > 0.5,"High","Normal")
)

df["High Risk Replacement"] = np.where(
(df["Failure Probability"] > 0.7) | (df["RUL"] < 20),
True,False
)

df["Sales Opportunity"] = np.where(
(df["Failure Probability"] > 0.6) &
(df["Demand Probability"] > 0.6),
True,False
)

high_risk = df[df["High Risk Replacement"]]
sales_leads = df[df["Sales Opportunity"]]

# -------------------------------------------------------
# FIND TOP OPPORTUNITY REGION
# -------------------------------------------------------

region_opportunity = df.groupby("Region")["Opportunity Value"].sum().reset_index()
top_region = region_opportunity.sort_values("Opportunity Value",ascending=False).iloc[0]

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------

page = st.sidebar.radio(
"Navigation",
[
"Global Dashboard",
"Region Explorer",
"Smart Inventory & Supply Chain",
"Sales Opportunity Center",
"Notification Center"
]
)

# -------------------------------------------------------
# GLOBAL DASHBOARD
# -------------------------------------------------------

if page == "Global Dashboard":

    st.header("Global Aftermarket Overview")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Machines Monitored",len(df))
    c2.metric("Critical Failures",(df["Failure Risk"]=="Critical").sum())
    c3.metric("Inventory Shortages",(df["Inventory Status"]=="Shortage").sum())
    c4.metric("Opportunity Value ₹",int(df["Opportunity Value"].sum()))

    # Top Opportunity Region Highlight
    st.info(
        f"Top Opportunity Region: **{top_region['Region']}** "
        f"with potential aftermarket value of ₹{int(top_region['Opportunity Value']):,}"
    )

    st.subheader("Predictive Aftermarket Intelligence")

    a,b = st.columns(2)

    a.metric(
    "High Risk Customers (Potential Bearing Replacement)",
    len(high_risk)
    )

    a.caption(f"{len(high_risk)} customers likely need bearing replacement soon.")

    b.metric("Predictive Sales Opportunities",len(sales_leads))

    st.subheader("Aftermarket Demand by Region")

    region_demand = df.groupby("Region")["Next Demand"].sum().reset_index()

    fig = px.bar(region_demand,x="Region",y="Next Demand",color="Region")
    st.plotly_chart(fig,use_container_width=True)

    selected_region = st.selectbox("Explore Region",df["Region"].unique())

    region_df = df[df["Region"]==selected_region]

    st.dataframe(region_df.head(20))

# -------------------------------------------------------
# REGION EXPLORER (UPDATED)
# -------------------------------------------------------

if page == "Region Explorer":

    st.header("Region Market Explorer")

    region = st.selectbox("Select Region", df["Region"].unique())

    region_df = df[df["Region"] == region]

    c1,c2,c3 = st.columns(3)

    c1.metric("Machines Monitored", len(region_df))
    c2.metric("Dealers", region_df["Dealer"].nunique())
    c3.metric("Total Predicted Demand", int(region_df["Next Demand"].sum()))

    st.subheader("Dealer Demand Analysis")

    if st.button("Analyze Dealer Demand"):

        dealer_demand = region_df.groupby("Dealer")["Next Demand"].sum().reset_index()

        # Percentile thresholds
        high_threshold = dealer_demand["Next Demand"].quantile(0.75)
        medium_threshold = dealer_demand["Next Demand"].quantile(0.40)

        dealer_demand["Demand Category"] = dealer_demand["Next Demand"].apply(
            lambda x:
            "High Demand" if x >= high_threshold
            else ("Medium Demand" if x >= medium_threshold else "Low Demand")
        )

        st.dataframe(dealer_demand)

        st.subheader("Demand Category Distribution")

        fig = px.bar(
            dealer_demand,
            x="Dealer",
            y="Next Demand",
            color="Demand Category",
            title="Dealer Aftermarket Demand"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Insights")

        high_count = len(dealer_demand[dealer_demand["Demand Category"]=="High Demand"])
        medium_count = len(dealer_demand[dealer_demand["Demand Category"]=="Medium Demand"])
        low_count = len(dealer_demand[dealer_demand["Demand Category"]=="Low Demand"])

        st.info(
            f"In region **{region}**: "
            f"{high_count} high-demand dealers, "
            f"{medium_count} medium-demand dealers, "
            f"{low_count} low-demand dealers identified."
        )
# -------------------------------------------------------
# SMART INVENTORY + SUPPLY CHAIN
# -------------------------------------------------------

if page == "Smart Inventory & Supply Chain":

    st.header("Smart Inventory & Supply Chain Planner")

    shortage = df[df["Inventory Status"]=="Shortage"]
    overstock = df[df["Inventory Status"]=="Overstock"]

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Shortage Locations")
        st.dataframe(shortage[
        ["Region","Dealer","Machine","Bearing",
        "Inventory","Next Demand","Inventory Gap"]
        ])

    with col2:
        st.subheader("Overstock Locations")
        st.dataframe(overstock[
        ["Region","Dealer","Machine","Bearing",
        "Inventory","Next Demand","Inventory Gap"]
        ])

    st.subheader("AI Suggested Inventory Transfers")

    transfers = []

    shortage_rows = shortage.to_dict("records")
    overstock_rows = overstock.to_dict("records")

    for s in shortage_rows:

        needed = abs(s["Inventory Gap"])

        for o in overstock_rows:

            if o["Bearing"] == s["Bearing"] and o["Inventory Gap"] < 0:

                available = abs(o["Inventory Gap"])

                transfer = min(needed,available)

                if transfer > 0:

                    transfers.append({

                    "From Dealer":o["Dealer"],
                    "To Dealer":s["Dealer"],
                    "Region From":o["Region"],
                    "Region To":s["Region"],
                    "Bearing":s["Bearing"],
                    "Transfer Qty":transfer

                    })

                    needed -= transfer

                if needed <= 0:
                    break

    transfer_df = pd.DataFrame(transfers)

    st.dataframe(transfer_df)

    if st.button("Send Inventory Transfer Orders"):

        st.success("Inventory transfer orders sent to logistics system")

# -------------------------------------------------------
# SALES OPPORTUNITY CENTER (SMART VERSION)
# -------------------------------------------------------

if page == "Sales Opportunity Center":

    st.header("Predictive Sales Opportunity Engine")

    st.metric("High Value Leads", len(sales_leads))

    st.subheader("AI Predicted Sales Opportunities")

    st.dataframe(sales_leads)

    # -------------------------------------------------------
    # DEMAND CLASSIFICATION
    # -------------------------------------------------------

    dealer_demand = df.groupby("Dealer")["Next Demand"].sum().reset_index()

    high_threshold = dealer_demand["Next Demand"].quantile(0.75)
    medium_threshold = dealer_demand["Next Demand"].quantile(0.40)

    dealer_demand["Demand Category"] = dealer_demand["Next Demand"].apply(
        lambda x:
        "High Demand" if x >= high_threshold
        else ("Medium Demand" if x >= medium_threshold else "Low Demand")
    )

    st.subheader("Dealer Demand Segmentation")

    st.dataframe(dealer_demand)

    # -------------------------------------------------------
    # ACTION BUTTONS
    # -------------------------------------------------------

    col1,col2,col3,col4 = st.columns(4)

    # SEND LEADS (HIGH DEMAND DEALERS)
    if col1.button("Send Leads to Sales Team"):

        high_dealers = dealer_demand[
            dealer_demand["Demand Category"]=="High Demand"
        ]

        st.success("Sales leads generated for high-demand dealers")

        st.write("High Opportunity Dealers")

        st.dataframe(high_dealers)

    # CRM OPPORTUNITY
    if col2.button("Create CRM Opportunities"):

        st.success("CRM opportunities created for predicted demand customers")

    # SERVICE VISIT
    if col3.button("Schedule Service Outreach"):

        st.success("Service outreach scheduled for predictive maintenance")

    # TRIGGER NOTIFICATIONS (LOW + MEDIUM DEALERS)
    if col4.button("Trigger Market Engagement Notifications"):

        notify_dealers = dealer_demand[
            dealer_demand["Demand Category"].isin(
                ["Low Demand","Medium Demand"]
            )
        ]

        st.warning("Notifications sent to dealers requiring engagement")

        st.write("Dealers Notified")

        st.dataframe(notify_dealers)
# -------------------------------------------------------
# ALERT CENTER
# -------------------------------------------------------

if page == "Notification Center":

    st.header("AIM³ Proactive Alerts")

    alerts = df[
    (df["Failure Risk"]=="Critical") |
    (df["Inventory Status"]=="Shortage")
    ]

    for _,row in alerts.head(10).iterrows():

        st.warning(f"""
⚠ ALERT

Machine: {row['Machine']}

Dealer: {row['Dealer']}

Region: {row['Region']}

Failure Risk: {row['Failure Risk']}

Inventory Status: {row['Inventory Status']}

Recommended Action:
Ensure spare bearing availability and schedule maintenance.
""")