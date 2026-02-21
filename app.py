import streamlit as st
from google import genai
import betfairlightweight

st.set_page_config(page_title="Universal Betting Agent", layout="centered")
st.title("🇦🇺 Universal Betting Agent")
st.caption("Calculate Expected Value & Dutching Stakes for All Markets")

# Initialize Gemini Client
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    ai_ready = True
except Exception:
    ai_ready = False

# Create Three Tabs now
tab1, tab2, tab3 = st.tabs(["📊 EV Calculator", "⚖️ 2-Way Dutching", "⚙️ Betfair API Test"])

# --- TAB 1: EV CALCULATOR ---
with tab1:
    st.header("Universal Bonus Back Calculator")
    col1, col2 = st.columns(2)
    with col1:
        stake = st.number_input("Stake ($)", value=50.0, step=5.0)
        bookie_odds = st.number_input("Bookie Back Odds", value=5.00, step=0.1)
    with col2:
        true_win_prob = st.number_input("True Win % (Betfair)", value=18.0, step=0.5) / 100
        true_fail_prob = st.number_input("True 2nd/3rd % (Promo Trigger)", value=40.0, step=0.5) / 100
    
    with st.expander("Advanced Settings"):
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
        
        if ai_ready:
            with st.spinner("Agent is analyzing risk profile..."):
                prompt = f"Act as an expert sports betting risk analyst. My stake is ${stake} at odds of {bookie_odds}. The true probability of winning is {true_win_prob*100}%, and the true probability of triggering the bonus refund is {true_fail_prob*100}%. The calculated Expected Value (EV) is {ev_roi}%. In exactly 3 sentences, provide a blunt assessment of this bet."
                try:
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    st.info(f"🤖 **Agent Verdict:**\n\n{response.text}")
                except Exception:
                    st.warning("AI Agent could not generate a response.")

# --- TAB 2: DUTCHING ---
with tab2:
    st.header("Head-to-Head Dutching")
    colA, colB = st.columns(2)
    with colA:
        stake_a = st.number_input("Your Stake ($)", value=50.0)
        odds_a = st.number_input("Your Odds", value=1.90)
    with colB:
        odds_b = st.number_input("Partner's Odds", value=1.90)
    
    if st.button("Calculate Hedge Stake", use_container_width=True):
        target_return = stake_a * odds_a
        required_stake_b = target_return / odds_b
        st.metric("Partner Must Bet:", f"${required_stake_b:.2f}")

# --- TAB 3: BETFAIR API TEST ---
with tab3:
    st.header("Betfair Connection Status")
    st.write("Click below to test if the app can successfully read your Exchange wallet.")
    
    if st.button("Ping Betfair API", use_container_width=True):
        with st.spinner("Connecting to Betfair servers..."):
            try:
                # Retrieve credentials from the secure vault
                username = st.secrets["BETFAIR_USERNAME"]
                password = st.secrets["BETFAIR_PASSWORD"]
                app_key = st.secrets["BETFAIR_APP_KEY"]
                
                # Initialize and login
                trading = betfairlightweight.APIClient(username, password, app_key=app_key)
                trading.login_interactive()
                
                # Fetch account funds
                account_funds = trading.account.get_account_funds()
                balance = account_funds.available_to_bet_balance
                
                st.success("✅ Connection Successful!")
                st.metric("Available Bankroll", f"${balance:.2f}")
                
            except Exception as e:
                st.error("❌ Connection Failed. Check your Secrets formatting.")
                st.write(f"Error Details: {e}")
