import html
import streamlit as st

NAVY, EMERALD, MINT = "#101B32", "#174F45", "#75B9A2"
LAVENDER, CREAM, GOLD = "#B8A6DF", "#F4F1E9", "#E7B978"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Manrope:wght@400;500;600;700&display=swap');

html, body, .stApp {{ font-family: 'Manrope', system-ui, sans-serif; color: {NAVY}; }}
.stApp {{
  background:
    radial-gradient(900px 420px at 85% -5%, rgba(184,166,223,.28), transparent 60%),
    radial-gradient(800px 400px at -10% 10%, rgba(117,185,162,.22), transparent 60%),
    {CREAM};
}}
.block-container {{ max-width: 780px; padding-top: 1.5rem; }}
h1, h2, h3 {{ font-family: 'Fraunces', Georgia, serif; font-weight: 600; letter-spacing: -.01em; color: {NAVY}; }}
h2, h3 {{ margin-top: 1.4rem; }}

.thw-hero {{
  position: relative; overflow: hidden; border-radius: 28px; padding: 2.4rem 2rem 2.2rem;
  color: {CREAM}; margin-bottom: 1.6rem;
  background:
    radial-gradient(1.5px 1.5px at 12% 22%, #fff 99%, transparent),
    radial-gradient(1px 1px at 28% 70%, rgba(255,255,255,.8) 99%, transparent),
    radial-gradient(1.5px 1.5px at 47% 30%, rgba(255,255,255,.9) 99%, transparent),
    radial-gradient(1px 1px at 63% 78%, rgba(255,255,255,.7) 99%, transparent),
    radial-gradient(2px 2px at 78% 18%, {GOLD} 99%, transparent),
    radial-gradient(1px 1px at 90% 60%, rgba(255,255,255,.8) 99%, transparent),
    radial-gradient(120% 140% at 100% 0%, rgba(184,166,223,.55), transparent 55%),
    linear-gradient(135deg, {NAVY} 0%, {EMERALD} 62%, #3b4f8a 130%);
  box-shadow: 0 18px 40px -22px rgba(16,27,50,.6);
}}
.thw-hero h1 {{ color: {CREAM}; font-size: 2.5rem; margin: 0 0 .35rem; padding: 0; }}
.thw-hero p {{ margin: 0; max-width: 34rem; font-size: 1.02rem; line-height: 1.55; color: rgba(244,241,233,.86); }}

[data-testid="stForm"] {{
  background: rgba(255,255,255,.62); border: 1px solid rgba(23,79,69,.14);
  border-radius: 22px; padding: 1.4rem 1.4rem .6rem; backdrop-filter: blur(6px);
}}
.stButton > button, [data-testid="stFormSubmitButton"] > button {{
  background: linear-gradient(135deg, {EMERALD}, #1f6556); color: {CREAM}; border: 0;
  border-radius: 999px; padding: .6rem 1.6rem; font-weight: 600;
  box-shadow: 0 8px 20px -10px {EMERALD};
}}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{ filter: brightness(1.1); color: #fff; }}
.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] > button:focus-visible {{ outline: 3px solid {GOLD}; outline-offset: 2px; }}

.stTabs [data-baseweb="tab-list"] {{ gap: .4rem; border-bottom: 1px solid rgba(23,79,69,.15); }}
.stTabs [data-baseweb="tab"] {{ border-radius: 999px 999px 0 0; padding: .5rem 1.1rem; font-weight: 600; }}
.stTabs [aria-selected="true"] {{ color: {EMERALD}; }}
.stTabs [data-baseweb="tab-highlight"] {{ background: {EMERALD}; }}

.thw-result {{ display: flex; align-items: center; gap: 1.4rem; margin: .4rem 0 1.2rem; }}
.thw-orb {{
  flex: 0 0 auto; width: 104px; height: 104px; border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, #fff 0%, {MINT} 22%, {EMERALD} 62%, {NAVY} 100%);
  box-shadow: 0 0 0 6px rgba(117,185,162,.16), 0 0 38px 6px rgba(184,166,223,.45);
  display: grid; place-items: center; color: {CREAM};
  font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 600;
}}
.thw-result h2 {{ margin: 0; font-size: 1.7rem; }}
.thw-result small {{ color: rgba(16,27,50,.7); font-size: .95rem; }}

.thw-note {{
  border-left: 3px solid {GOLD}; background: rgba(231,185,120,.14);
  padding: .8rem 1rem; border-radius: 0 14px 14px 0; font-size: .92rem; line-height: 1.5; margin: 1rem 0;
}}
.thw-factor {{ padding: .7rem 0; border-bottom: 1px solid rgba(16,27,50,.08); }}
.thw-factor b {{ color: {EMERALD}; }}

@media (prefers-reduced-motion: no-preference) {{ .stButton > button {{ transition: filter .2s ease; }} }}
@media (max-width: 640px) {{ .thw-hero h1 {{ font-size: 1.9rem; }} .thw-result {{ flex-direction: column; text-align: center; }} }}
</style>
"""


def inject_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero() -> None:
    st.markdown(
        """<div class="thw-hero"><h1>The Healthy Way</h1>
        <p>Enter your habits to see how a statistical model reads your profile,
        then get meal and movement ideas that fit your day.</p></div>""",
        unsafe_allow_html=True,
    )


def result_card(label: str, bmi: float) -> None:
    pretty = html.escape(label.replace("_", " "))
    st.markdown(
        f"""<div class="thw-result"><div class="thw-orb" aria-hidden="true">{bmi:.1f}</div>
        <div><small>Model estimate for your profile</small><h2>{pretty}</h2>
        <small>BMI {bmi:.1f}, calculated from your height and weight</small></div></div>""",
        unsafe_allow_html=True,
    )


def note(text: str) -> None:
    st.markdown(f'<div class="thw-note">{html.escape(text)}</div>', unsafe_allow_html=True)


def factor(title: str, body: str) -> None:
    st.markdown(f'<div class="thw-factor"><b>{html.escape(title)}</b><br>{html.escape(body)}</div>',
                unsafe_allow_html=True)


DISCLAIMER = ("The Healthy Way offers general lifestyle information and model-based estimates. "
              "It is not medical advice, a diagnosis, or a treatment plan. "
              "Talk to a doctor or registered dietitian about your personal health.")
