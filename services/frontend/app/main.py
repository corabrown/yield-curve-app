import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import api

st.set_page_config(page_title="Yield Curve", layout="wide")
st.title("US Treasury Yield Curve")

tab_curve, tab_history, tab_user = st.tabs(["Yield Curve", "History", "User"])

# ── Tab 1: Yield Curve ────────────────────────────────────────────────────────
with tab_curve:
    try:
        dates = api.get_dates()
    except Exception as e:
        st.error(f"Could not reach API: {e}")
        st.stop()

    selected_date = st.selectbox("Date", dates, index=0)

    try:
        data = api.get_curve(selected_date)
    except Exception as e:
        st.error(f"Failed to load curve for {selected_date}: {e}")
        st.stop()

    df = pd.DataFrame(data["rates"])
    df = df.dropna(subset=["rate"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["tenor"],
        y=df["rate"],
        mode="lines+markers",
        line=dict(color="#185FA5", width=2),
        marker=dict(size=6),
        hovertemplate="%{x}: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(title="Tenor"),
        yaxis=dict(title="Yield (%)"),
        title=f"Treasury Yield Curve — {selected_date}",
        hovermode="x unified",
        height=500,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: History ────────────────────────────────────────────────────────────
with tab_history:
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start date", value=pd.Timestamp("2020-01-01"))
    with col2:
        end = st.date_input("End date", value=pd.Timestamp.today())

    try:
        rows = api.get_history(start=str(start), end=str(end))
    except Exception as e:
        st.error(f"Failed to load history: {e}")
        st.stop()

    df_hist = pd.DataFrame(rows)
    df_hist = df_hist.dropna(subset=["rate"])
    df_hist["date"] = pd.to_datetime(df_hist["date"])

    all_tenors = sorted(df_hist["tenor"].unique(), key=lambda t: df_hist.loc[df_hist["tenor"] == t, "maturity_years"].iloc[0])
    selected_tenors = st.multiselect("Tenors", all_tenors, default=["2Y", "5Y", "10Y", "30Y"])

    df_filtered = df_hist[df_hist["tenor"].isin(selected_tenors)]

    fig2 = px.line(
        df_filtered,
        x="date",
        y="rate",
        color="tenor",
        labels={"rate": "Yield (%)", "date": "Date", "tenor": "Tenor"},
        title="Yield History",
        height=500,
    )
    fig2.update_layout(hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab 3: User ───────────────────────────────────────────────────────────────
with tab_user:

    if "selected_user_id" not in st.session_state:
        st.session_state.selected_user_id = None

    def show_orders(user: dict):
        try:
            orders = api.get_user_orders(user["id"])
            st.subheader(f"Orders for {user['first_name']} (ID: {user['id']})")
            if not orders:
                st.info("No orders yet.")
            else:
                df_orders = pd.DataFrame(orders)[["id", "term", "amount", "created_at"]]
                df_orders.columns = ["Order ID", "Term", "Amount ($)", "Created At"]
                st.dataframe(df_orders, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Could not fetch orders: {e}")

    # ── Select existing user ──────────────────────────────────────────────────
    st.subheader("Select User")
    try:
        users = api.get_users()
    except Exception as e:
        st.error(f"Could not load users: {e}")
        users = []

    if users:
        ids = [u["id"] for u in users]
        default_idx = ids.index(st.session_state.selected_user_id) if st.session_state.selected_user_id in ids else 0
        selected_user = st.selectbox(
            "User",
            users,
            index=default_idx,
            format_func=lambda u: f"{u['first_name']} (ID: {u['id']})",
        )
        st.session_state.selected_user_id = selected_user["id"]
    else:
        st.info("No users yet. Create one below.")
        selected_user = None

    st.divider()

    # ── Create user ───────────────────────────────────────────────────────────
    st.subheader("Create User")
    with st.form("create_user_form"):
        first_name = st.text_input("First name")
        submitted = st.form_submit_button("Create")
    if submitted:
        if not first_name.strip():
            st.warning("Please enter a first name.")
        else:
            try:
                user = api.create_user(first_name.strip())
                st.success(f"Created user '{user['first_name']}' (ID: {user['id']})")
                st.session_state.selected_user_id = user["id"]
                st.rerun()
            except Exception as e:
                st.error(f"Could not create user: {e}")

    st.divider()

    # ── Create order ──────────────────────────────────────────────────────────
    st.subheader("Create Order")
    if not selected_user:
        st.info("Select or create a user above to place an order.")
    else:
        st.write(f"Placing order for **{selected_user['first_name']}** (ID: {selected_user['id']})")
        with st.form("create_order_form"):
            tenor_options = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
            term = st.selectbox("Term", tenor_options)
            amount = st.number_input("Amount ($)", min_value=0.01, step=100.0, format="%.2f")
            order_submitted = st.form_submit_button("Place Order")
        if order_submitted:
            try:
                order = api.create_order(selected_user["id"], term, amount)
                st.success(f"Order placed — ID: {order['id']}, Term: {order['term']}, Amount: ${order['amount']}")
                st.rerun()
            except Exception as e:
                st.error(f"Could not create order: {e}")

    if selected_user:
        st.divider()
        show_orders(selected_user)
