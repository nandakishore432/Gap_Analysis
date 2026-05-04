import streamlit as st
import pandas as pd
import plotly
import plotly.express as px

# Load data
file = r"C:\Users\admin\Desktop\Stackly tasks\10. Dashboard for Gap Analysis\automobile_dashboard_dataset.xlsx"
vehicles = pd.read_excel(file, sheet_name="Vehicles")
users = pd.read_excel(file, sheet_name="Users")
interactions = pd.read_excel(file, sheet_name="Interactions")

# Merge data
df = interactions.merge(vehicles, on="VehicleID").merge(users, on="UserID")

st.set_page_config(layout="wide")
st.title("🚗 Automobile Sales & Conversion Dashboard")

# KPIs
total_views = len(df[df["Action"] == "View"])
test_drives = len(df[df["Action"] == "Test Drive"])
purchases = len(df[df["Action"] == "Purchase"])
conversion = purchases / total_views if total_views > 0 else 0
revenue = df[df["Action"] == "Purchase"]["Price"].sum()

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Views", total_views)
col2.metric("Test Drives", test_drives)
col3.metric("Purchases", purchases)
col4.metric("Conversion Rate", f"{conversion:.2%}")
col5.metric("Revenue", f"₹{revenue:,}")

# Funnel Data
funnel_df = pd.DataFrame({
    "Stage": ["Views", "Test Drives", "Purchases"],
    "Count": [total_views, test_drives, purchases]
})

fig_funnel = px.funnel(funnel_df, x="Count", y="Stage")
st.plotly_chart(fig_funnel, use_container_width=True)

# Revenue by Brand
rev_brand = df[df["Action"] == "Purchase"].groupby("Brand")["Price"].sum().reset_index()
fig_bar = px.bar(rev_brand, x="Brand", y="Price", title="Revenue by Brand")
st.plotly_chart(fig_bar, use_container_width=True)

# Purchases over time
df["Date"] = pd.to_datetime(df["Date"])
purchases_time = df[df["Action"] == "Purchase"].groupby("Date").size().reset_index(name="Count")
fig_line = px.line(purchases_time, x="Date", y="Count", title="Purchases Over Time")
st.plotly_chart(fig_line, use_container_width=True)

# Category share
cat = vehicles["Category"].value_counts().reset_index()
cat.columns = ["Category", "Count"]
fig_pie = px.pie(cat, names="Category", values="Count", title="Category Share")
st.plotly_chart(fig_pie, use_container_width=True)

# Map (City sales)
city_sales = df[df["Action"] == "Purchase"].groupby("City").size().reset_index(name="Sales")
fig_map = px.scatter_geo(city_sales, locations="City", locationmode="country names", size="Sales")
st.plotly_chart(fig_map, use_container_width=True)

# Low conversion table
vehicle_perf = df.groupby("VehicleID").agg(
    Views=("Action", lambda x: (x == "View").sum()),
    Purchases=("Action", lambda x: (x == "Purchase").sum())
).reset_index()

vehicle_perf["Conversion"] = vehicle_perf["Purchases"] / vehicle_perf["Views"]
st.subheader("⚠ Low Conversion Vehicles")
st.dataframe(vehicle_perf.sort_values("Conversion"))
