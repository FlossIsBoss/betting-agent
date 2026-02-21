import streamlit as st

# 1. Configure the app to be mobile-friendly and generic
st.set_page_config(page_title="Universal Betting Agent", layout="centered")
st.title("🇦🇺 Universal Betting Agent")
st.caption("Calculate Expected Value & Dutching Stakes for All Markets")

# 2. Create Tabs for different betting modes
tab1, tab2 = st.tabs(["📊 Promo EV Calculator", "⚖️ 2-Way Dutching"])

# --- TAB 1: UNIVERSAL EV CALCULATOR (Racing & Sports) ---
with tab1:
    st.header("Universal Bonus Back Calculator")
    st.info("Use this for Horse Racing, Greyhounds, or any Multi-Leg Sport Promo.")
    
    # Inputs
    col1, col2 = st.columns(2)
    with col1:
        stake = st.number_input("Stake ($)", value=50.0, step=5.0)
        bookie_odds = st.number_input("Bookie Back Odds", value=5.00, step=0.1)
    
    with col2:
        true_win_prob = st.number_input("True Win % (Betfair)", value=18.0, step=0.5) / 100
        true_fail_prob = st.number_input("True 2nd/3rd % (Promo Trigger)", value=40.0, step=0.5) / 100
    
    # Advanced Settings (Hidden by default to keep it clean)
    with st.expander("⚙️ Advanced Settings"):
        bonus_retention = st.slider("Bonus Bet Retention Rate (%)", 60, 90, 75) / 100
        max_refund = st.number_input("Max Refund Cap ($)", value=50.0)

    if st.button("Calculate EV", use_container_width=True):
        # Math: (Probability of Win * Profit) + (Probability of Bonus * Bonus Value) - Stake
        win_profit = (stake * bookie_odds) - stake
        expected_win_return = true_win_prob * win_profit
        
        bonus_value = min(stake, max_refund) * bonus_retention
        expected_bonus_return = true_fail_prob * bonus_value
        
        # Calculate Loss Probability (The times you get nothing)
        prob_loss = 1.0 - true_win_prob - true_fail_prob
        expected_loss = prob_loss * stake
        
        # Net EV
        total_ev = (expected_win_return + expected_bonus_return) - expected_loss
        ev_roi = (total_ev / stake) * 100
        
        # 0-100 Score Logic
        score = max(0, min(100, 50 + (ev_roi * 2)))
        
        # Display Results
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Risk/Reward Score", f"{score:.0f}/100")
        c2.metric("Est. Profit Per Bet", f"${total_ev:.2f}", delta=f"{ev_roi:.1f}% ROI")
        
        if total_ev > 0:
            st.success("✅ **POSITIVE VALUE:** This bet is mathematically profitable long-term.")
        else:
            st.error("❌ **NEGATIVE VALUE:** The odds do not justify the risk.")

# --- TAB 2: HEAD-TO-HEAD DUTCHING (Sports Only) ---
with tab2:
    st.header("Head-to-Head Dutching")
    st.warning("⚠️ Strictly for 2-outcome sports (NBA, NRL, AFL, Tennis). Do NOT use for Racing.")
    
    st.write("Calculates the perfect hedge stake for you and your partner.")
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Bookie A (You)")
        stake_a = st.number_input("Your Stake ($)", value=50.0)
        odds_a = st.number_input("Your Odds", value=1.90)
    
    with colB:
        st.subheader("Bookie B (Partner)")
        odds_b = st.number_input("Partner's Odds", value=1.90)
    
    if st.button("Calculate Hedge Stake", use_container_width=True):
        # Dutching Math: Target Return = Stake A * Odds A
        target_return = stake_a * odds_a
        required_stake_b = target_return / odds_b
        
        total_outlay = stake_a + required_stake_b
        net_result = target_return - total_outlay
        
        st.divider()
        st.metric("Partner Must Bet:", f"${required_stake_b:.2f}")
        
        st.write(f"**Total Outlay:** ${total_outlay:.2f}")
        st.write(f"**Guaranteed Return:** ${target_return:.2f}")
        
        if net_result >= 0:
            st.success(f"📈 **ARBITRAGE:** You make a guaranteed profit of ${net_result:.2f}!")
        else:
            st.info(f"📉 **QUALIFYING LOSS:** You lose ${abs(net_result):.2f} to trigger the promos.")