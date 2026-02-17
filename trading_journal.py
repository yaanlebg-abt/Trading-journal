import streamlit as st
import pandas as pd
import os

DATA_FILE = "trades.csv"

st.set_page_config(page_title="Trading Journal", layout="wide")

# =========================================================
# LOAD DATA
# =========================================================
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=[
        "Date",
        "Instrument",
        "Trade Type",
        "Lot Size",
        "Entry",
        "Exit",
        "TP",
        "SL",
        "Status",
        "Gain",
        "Account Balance",
        "Entry Condition"
    ])

df = df.reset_index(drop=True)
df.index.name = "Trade Number"

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "📒 Trade Journal",
    "📊 Statistics",
    "✏️ Edit Trade"
])

# =========================================================
# TAB 1 — ADD TRADE
# =========================================================
with tab1:
    st.title("Trading Journal")

    with st.form("trade_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date")
            instrument = st.text_input("Instrument")
            trade_type = st.selectbox("Trade Type", ["Buy", "Sell"])
            lot_size = st.number_input("Lot Size", step=0.01)
            entry = st.number_input("Entry Price")
            exit_price = st.number_input("Exit Price")
            tp = st.number_input("Take Profit")
            sl = st.number_input("Stop Loss")

        with col2:
            status = st.selectbox("Trade Status", ["Win", "Loss", "BE"])
            gain = st.number_input("Gain / Loss ($)")
            balance = st.number_input("Account Balance After Trade")
            entry_condition = st.text_area("Entry Condition")

        submit = st.form_submit_button("Add Trade")

        if submit:
            text_missing = instrument.strip() == ""

            numeric_missing = any(v == 0 or v == 0.0 for v in [
                lot_size, entry, exit_price, tp, sl, gain, balance
            ])

            if text_missing or numeric_missing:
                st.error("All required fields must be filled and non-zero.")
            else:
                new_trade = pd.DataFrame([{
                    "Date": date,
                    "Instrument": instrument,
                    "Trade Type": trade_type,
                    "Lot Size": lot_size,
                    "Entry": entry,
                    "Exit": exit_price,
                    "TP": tp,
                    "SL": sl,
                    "Status": status,
                    "Gain": gain,
                    "Account Balance": balance,
                    "Entry Condition": entry_condition
                }])

                df = pd.concat([df, new_trade], ignore_index=True)
                df.to_csv(DATA_FILE, index=False)
                st.success("Trade saved successfully")
                st.rerun()

    st.subheader("Trade History")
    display_df = df.reset_index()
    st.dataframe(display_df, use_container_width=True)

    st.divider()

    if st.button("🗑️ Delete ALL Trades"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.warning("All trade data deleted.")
        st.rerun()

# =========================================================
# TAB 2 — STATISTICS
# =========================================================
with tab2:
    st.title("Performance Statistics")

    if len(df) > 0:
        df_stats = df.copy()
        df_stats["Date"] = pd.to_datetime(df_stats["Date"])

        st.subheader("Account Balance Curve")
        st.line_chart(df_stats.set_index("Date")["Account Balance"])

        wins = (df_stats["Status"] == "Win").sum()
        losses = (df_stats["Status"] == "Loss").sum()
        total = len(df_stats)
        winrate = (wins / total) * 100 if total > 0 else 0


        col1, col2, col3 = st.columns(3)
        col1.metric("Total Trades", total)
        col2.metric("Wins", wins)
        col3.metric("Win Rate %", round(winrate, 2))

        st.subheader("Profit / Loss Per Trade")
        st.bar_chart(df_stats["Gain"])

    else:
        st.info("No trades recorded yet.")

# =========================================================
# TAB 3 — EDIT TRADE
# =========================================================
with tab3:
    st.title("Edit Existing Trade")

    if len(df) > 0:
        display_df = df.reset_index()
        st.dataframe(display_df, use_container_width=True)

        trade_number = st.selectbox(
            "Select Trade Number",
            df.index.tolist()
        )

        trade_to_edit = df.loc[trade_number]

        with st.form("edit_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_date = st.date_input("Date", pd.to_datetime(trade_to_edit["Date"]))
                edit_instrument = st.text_input("Instrument", trade_to_edit["Instrument"])
                edit_type = st.selectbox(
                    "Trade Type",
                    ["Buy", "Sell"],
                    index=0 if trade_to_edit["Trade Type"] == "Buy" else 1
                )
                edit_lot = st.number_input("Lot Size", value=float(trade_to_edit["Lot Size"]))
                edit_entry = st.number_input("Entry", value=float(trade_to_edit["Entry"]))
                edit_exit = st.number_input("Exit", value=float(trade_to_edit["Exit"]))
                edit_tp = st.number_input("TP", value=float(trade_to_edit["TP"]))
                edit_sl = st.number_input("SL", value=float(trade_to_edit["SL"]))

            with col2:
                edit_status = st.selectbox(
                    "Status",
                    ["Win", "Loss", "BE"],
                    index=["Win","Loss","BE"].index(trade_to_edit["Status"])
                )
                edit_gain = st.number_input("Gain", value=float(trade_to_edit["Gain"]))
                edit_balance = st.number_input(
                    "Account Balance",
                    value=float(trade_to_edit["Account Balance"])
                )
                edit_condition = st.text_area(
                    "Entry Condition",
                    trade_to_edit["Entry Condition"]
                )

            update = st.form_submit_button("Update Trade")

            if update:
                text_missing = edit_instrument.strip() == ""
                numeric_missing = any(v == 0 or v == 0.0 for v in [
                    edit_lot, edit_entry, edit_exit, edit_tp, edit_sl, edit_gain, edit_balance
                ])

                if text_missing or numeric_missing:
                    st.error("All required fields must be filled and non-zero.")
                else:
                    df.loc[trade_number] = [
                        edit_date,
                        edit_instrument,
                        edit_type,
                        edit_lot,
                        edit_entry,
                        edit_exit,
                        edit_tp,
                        edit_sl,
                        edit_status,
                        edit_gain,
                        edit_balance,
                        edit_condition
                    ]

                    df.to_csv(DATA_FILE, index=False)
                    st.success("Trade updated successfully")
                    st.rerun()

    else:
        st.info("No trades available to edit.")

