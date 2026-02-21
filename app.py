import streamlit as st
from google import genai

# 1. Configure the app
st.set_page_config(page_title="Universal Betting Agent", layout="centered")
st.title("🇦🇺 Universal Betting Agent")
st.caption("Calculate Expected Value & Dutching Stakes for All Markets")

# Initialize Gemini Client using Streamlit Secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    ai_ready = True
except Exception:
    ai_ready = False

tab1, tab2 = st.tabs(["📊 Promo EV Calculator", "⚖️ 2-Way Dutching"])

with tab1:
    st.header("Universal Bonus Back Calculator")
    
    col1, col2 = st.columns(2)
    with col1:
        stake = st.number_input("Stake ($)", value=50.0, step=5.0)
        bookie_odds = st.number_input("Bookie Back Odds", value=5.00, step=0.1)
    
    with col2:
        true_win_prob = st.number_input("True Win % (Betfair)", value=18.0, step=0.5) / 100
        true_fail_prob = st.number_input("True 2nd/3rd % (Promo Trigger)", value=40.0, step=0.5) / 100
    
    with st.expander("⚙️ Advanced Settings"):
        bonus_retention = st.slider("Bonus Bet Retention Rate (%)", 60, 90, 75) / 100
        max_refund = st.number_input("Max Refund Cap ($)", value=50.0)

    if st.button("Calculate EV & Get AI Advice", use_container_width=True):
        win_profit = (stake * bookie_odds) - stake
        expected_win_return = true_win_prob * win_profit
        
        bonus_value = min(stake, max_refund) * bonus_retention
        expected_bonus_return = true_fail_prob * bonus_value
        
        prob_loss = 1.0 - true_win_prob - true_fail_prob
        expected_loss = prob_loss * stake
        
        total_ev = (expected_win_return + expected_bonus_return) - expected_loss
        ev_roi = (total_ev / stake) * 100
        score = max(0, min(100, 50 + (ev_roi * 2)))
        
        st.divider()
        c1, c2 = st.columns(2)
        c1.metric("Risk/Reward Score", f"{score:.0f}/100")
        c2.metric("Est. Profit Per Bet", f"${total_ev:.2f}", delta=f"{ev_roi:.1f}% ROI")
        
        if total_ev > 0:
            st.success("✅ **POSITIVE VALUE:** This bet is mathematically profitable long-term.")
        else:
            st.error("❌ **NEGATIVE VALUE:** The odds do not justify the risk.")
            
        # The AI Agent Analysis Block
        if ai_ready:
            with st.spinner("Agent is analyzing risk profile..."):
                prompt = f"Act as an expert sports betting risk analyst. I am evaluating an Australian sports promotion. My stake is ${stake} at odds of {bookie_odds}. The true probability of winning is {true_win_prob*100}%, and the true probability of triggering the bonus refund is {true_fail_prob*100}%. The calculated Expected Value (EV) is {ev_roi}%. In exactly 3 sentences, provide a blunt assessment of this bet, advising if the risk/reward ratio is optimal or if I should look for a better match."
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.info(f"🤖 **Agent Verdict:**\n\n{response.text}")
                except Exception as e:
                    st.warning("AI Agent could not generate a response. Please check your API key limits.")

with tab2:
    st.header("Head-to-Head Dutching")
    st.warning("⚠️ Strictly for 2-outcome sports (e.g., NBL, AFL). Do NOT use for Racing.")
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Bookie A")
        stake_a = st.number_input("Your Stake ($)", value=50.0)
        odds_a = st.number_input("Your Odds", value=1.90)
    
    with colB:
        st.subheader("Bookie B")
        odds_b = st.number_input("Partner's Odds", value=1.90)
    
    if st.button("Calculate Hedge Stake", use_container_width=True):
        target_return = stake_a * odds_a
        required_stake_b = target_return / odds_b
        total_outlay = stake_a + required_stake_b
        net_result = target_return - total_outlay
        
        st.divider()
        st.metric("Partner Must Bet:", f"${required_stake_b:.2f}")
        st.write(f"**Total Outlay:** ${total_outlay:.2f}")
        
        if net_result >= 0:
            st.success(f"📈 **ARBITRAGE:** Guaranteed profit of ${net_result:.2f}")
        else:
            st.info(f"📉 **QUALIFYING LOSS:** You lose ${abs(net_result):.2f} to trigger promos.")
