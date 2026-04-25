import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="O Escriba", page_icon="📜", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap');

/* Fundo principal */
.stApp { background: linear-gradient(135deg, #2b1d0e 0%, #1a1209 100%); color: #e6dcc3; }

/* Esconde TODAS as barras laterais, topo e rodapé para não ter bug de menu */
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], #MainMenu, footer, header { display: none !important; }

/* Títulos */
.main-title { font-family: 'Cinzel', serif; color: #c9a84c; text-align: center; font-size: 2.8rem; text-shadow: 2px 2px 4px #000000; margin-bottom: 10px; letter-spacing: 2px; }
.subtitle { font-family: 'Lora', serif; color: #a89272; text-align: center; font-style: italic; font-size: 1.1rem; margin-bottom: 30px; }

/* Estilo dos Inputs */
.stTextInput, .stTextArea, .stSelectbox, .stNumberInput { background-color: #1a1209 !important; border: 1px solid #5c4a2a !important; color: #e6dcc3 !important; border-radius: 8px; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label { font-family: 'Cinzel', serif; color: #c9a84c !important; font-weight: bold; }

/* Estilo do Botão */
.stButton > button[kind="primary"] { background: linear-gradient(90deg, #8b6914, #c9a84c); color: #1a1209; font-family: 'Cinzel', serif; font-weight: bold; font-size: 1.1rem; border: none; border-radius: 8px; padding: 15px 24px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0px 4px 8px rgba(0,0,0,0.5); transition: all 0.3s ease; width: 100%; }
.stButton > button[kind="primary"]:hover { background: linear-gradient(90deg, #c9a84c, #e6c86e); transform: translateY(-2px); box-shadow: 0px 6px 12px rgba(201, 168, 76, 0.4); }

/* Pergaminho final */
.parchment-container { background: linear-gradient(to bottom, #f4e4bc, #e6d5a8, #d6c498); border: 8px solid #5c3a1e; border-radius: 4px; box-shadow: inset 0 0 30px rgba(0,0,0,0.2), 10px 10px 20px rgba(0,0,0,0.5); padding: 40px 50px; color: #2b1d0e; font-family: 'Lora', serif; font-size: 1.15rem; line-height: 1.8; margin-bottom: 30px; }
.parchment-container h1, .parchment-container h2, .parchment-container h3 { font-family: 'Cinzel', serif; color: #5c3a1e; border-bottom: 1px solid #8b6914; padding-bottom: 10px; margin-top: 30px; }
.parchment-container strong { color: #8b0000; }

/* Divisória dourada */
.divider-gold { border-top: 2px solid #5c3a1e; margin: 30px 0; box-shadow: 0px -2px 10px rgba(201, 168, 76, 0.3); }
</style>""", unsafe_allow_html=True)

# ==========================================
# TELA PRINCIPAL
# ==========================================
st.markdown('<div class="main-title">📜 O Escriba</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">"Dê voz à alma dos personagens"</div>', unsafe_allow_html=True)

st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)

# --- CAMPOS DE ENTRADA (Na tela principal, sem sidebar) ---
col1, col2 = st.columns(2)

with col1:
    personagem = st.text_input("👤 Personagem")
    destinatario = st.text_input("✉️ Destinatário")
    tomm = st.selectbox("🎭 Tom", ["Poético", "Urgente", "Materno", "Solene", "Mistério"])

with col2:
    versao = st.selectbox("🔍 Versão Bíblica", ["ARA", "NVI", "ARC", "NLT", "ACF"])
    divisoes = st.number_input("📑 Qtd de Cartas", min_value=1, max_value=5, value=2)

historia = st.text_area("📖 História Bíblica", height=150)

st.markdown("")
gerar_btn = st.button("✒️ Redigir Manuscritos", type="primary", use_container_width=True)

# ==========================================
# LÓGICA DE GERAÇÃO
# ==========================================
SYSTEM_PROMPT = """Você é um mestre da literatura epistolar e historiador bíblico. Converta relatos em manuscritos imersivos. Dê voz à alma dos personagens. Regras: 1. Divida na quantidade de cartas exata. 2. Cabeçalho histórico poético em itálico. 3. Termos da época (siclos, papiro). 4. Despedida característica. 5. Ao final de CADA carta, adicione: **"Dica de Curadoria para o Snail Mail"** com sugestões de papel/aroma. 6. Separe cartas com ---. Tons: Mistério (noir, sombras), Poético (natureza, ritmo), Urgente (frases curtas, ofegante), Materno (ternura), Solene (reverência)."""

if gerar_btn:
    if not personagem or not historia:
        st.error("Por favor, preencha o Personagem e a História.")
    else:
        with st.spinner('Preparando a tinta, esticando o papiro...'):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                user_prompt = f"Personagem: {personagem}\nHistória: {historia}\nDestinatário: {destinatario}\nTom: {tomm}\nDivisões: {divisoes} cartas.\nVersão: {versao}\n\nEscreva os manuscritos agora."
                
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT}, 
                        {"role": "user", "content": user_prompt}
                    ], 
                    temperature=0.8
                )
                manuscript_text = response.choices[0].message.content
                st.markdown(f'<div class="parchment-container">{manuscript_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao contactar o escriba: {e}")
