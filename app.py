import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Page Configuration
st.set_page_config(
    page_title="E-Commerce Demand & Inventory Dashboard",
    page_icon="📈",
    layout="wide"
)

# Load Data from SQLite
@st.cache_data
def load_data():
    conn = sqlite3.connect("ecommerce_demand.db")
    
    # Load Transactions & Products
    df_trans = pd.read_sql("""
        SELECT t.date, t.customer_id, t.product_id, p.product_name, p.category, t.quantity_sold, t.total_revenue
        FROM Transactions t
        JOIN Products p ON t.product_id = p.product_id
    """, conn)
    
    # Load Inventory Status
    df_inv = pd.read_sql("""
        SELECT i.product_id, p.product_name, p.category, i.stock_on_hand, i.safety_stock_threshold, i.last_restock_date
        FROM Inventory i
        JOIN Products p ON i.product_id = p.product_id
    """, conn)
    
    conn.close()
    df_trans['date'] = pd.to_datetime(df_trans['date'])
    return df_trans, df_inv

df_trans, df_inv = load_data()

# --- SIDEBAR NAVIGATION & FILTERS ---
st.sidebar.header("📊 Control Panel")
selected_category = st.sidebar.selectbox(
    "Filter by Category",
    options=["All"] + list(df_trans['category'].unique())
)

# Filter Data based on sidebar selection
if selected_category != "All":
    filtered_trans = df_trans[df_trans['category'] == selected_category]
    filtered_inv = df_inv[df_inv['category'] == selected_category]
else:
    filtered_trans = df_trans
    filtered_inv = df_inv

# --- MAIN DASHBOARD HEADER ---
st.title("🛒 E-Commerce Demand Forecasting & Inventory Intelligence")
st.markdown("Monitor real-time sales velocity, track stockout risks, and analyze category performance.")

# --- TOP KPI METRICS ROW ---
total_revenue = filtered_trans['total_revenue'].sum()
total_units = filtered_trans['quantity_sold'].sum()
low_stock_items = len(filtered_inv[filtered_inv['stock_on_hand'] <= filtered_inv['safety_stock_threshold']])

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Total Units Sold", f"{total_units:,}")
col3.metric("Stockout Alerts", f"{low_stock_items} Items", delta_color="inverse" if low_stock_items > 0 else "normal")

st.markdown("---")

# --- TABS FOR ORGANIZED LAYOUT ---
tab1, tab2, tab3 = st.tabs(["📈 Sales & Demand Trends", "⚠️ Inventory & Stock Risk", "📋 Raw Data Explorer"])

with tab1:
    st.subheader("Daily Sales Velocity by Product")
    
    # Aggregate daily sales for plotting
    daily_trend = filtered_trans.groupby([pd.Grouper(key='date', freq='D'), 'product_name'])['quantity_sold'].sum().reset_index()
    
    fig_trend = px.line(
        daily_trend, 
        x='date', 
        y='quantity_sold', 
        color='product_name',
        labels={'quantity_sold': 'Units Sold', 'date': 'Date', 'product_name': 'Product'},
        template='plotly_white'
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("Inventory Health & Safety Thresholds")
    st.markdown("Products where **Stock on Hand** is approaching or below the **Safety Threshold** require reordering.")
    
    # Highlight low stock items
    fig_inv = px.bar(
        filtered_inv,
        x='product_name',
        y=['stock_on_hand', 'safety_stock_threshold'],
        barmode='group',
        labels={'value': 'Quantity', 'product_name': 'Product Name', 'variable': 'Metric'},
        template='plotly_white'
    )
    st.plotly_chart(fig_inv, use_container_width=True)
    
    # Warning table for low stock
    at_risk = filtered_inv[filtered_inv['stock_on_hand'] <= filtered_inv['safety_stock_threshold']]
    if not at_risk.empty:
        st.warning(f"⚠️ Action Required: {len(at_risk)} product(s) are at or below safety stock limits!")
        st.dataframe(at_risk, use_container_width=True)
    else:
        st.success("✅ All inventories are currently above safety thresholds.")

with tab3:
    st.subheader("Transactional Records Explorer")
    st.dataframe(filtered_trans, use_container_width=True)