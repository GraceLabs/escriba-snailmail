import streamlit as st
from openai import OpenAI
import os

# ==========================================
# 1. CONFIGURAÇÃO INICIAL E SESSÃO
# ==========================================
st.set_page_config(page_title="O Escriba", page_icon="📜", layout="centered", initial_sidebar_state="expanded")

# Evita que a tela suma ao recarregar
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "resultado_gerado" not in st.session_state:
    st.session_state.resultado_gerado = None

# ==========================================
# 2. ESTILOS VISUAIS (CSS)
# ==========================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap');
.stApp { background: linear-gradient(135deg, #2b1d0e 0%, #1a1209 100%); color: #e6dcc3; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #3e2c18 0%, #2b1d0e 100%); border-right: 2px solid #8b6914; }
[data-testid="stSidebar"] * { color: #e6dcc3 !important; }
.main-title { font-family: 'Cinzel', serif; color: #c9a84c; text-align: center; font-size: 2.8rem; text-shadow: 2px 2px 4px #000000; margin-bottom: 10px; letter-spacing: 2px; }
.subtitle { font-family: 'Lora', serif; color: #a89272; text-align: center; font-style: italic; font-size: 1.1rem; margin-bottom: 40px; }
.stTextInput, .stTextArea, .stSelectbox, .stNumberInput { background-color: #1a1209 !important; border: 1px solid #5c4a2a !important; color: #e6dcc3 !important; border-radius: 8px; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label { font-family: 'Cinzel', serif; color: #c9a84c !important; font-weight: bold; }
.stButton > button[kind="primary"] { background: linear-gradient(90deg, #8b6914, #c9a84c); color: #1a1209; font-family: 'Cinzel', serif; font-weight: bold; font-size: 1.1rem; border: none; border-radius: 8px; padding: 12px 24px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0px 4px 8px rgba(0,0,0,0.5); transition: all 0.3s ease; width: 100%; }
.stButton > button[kind="primary"]:hover { background: linear-gradient(90deg, #c9a84c, #e6c86e); transform: translateY(-2px); box-shadow: 0px 6px 12px rgba(201, 168, 76, 0.4); }
.parchment-container { background: linear-gradient(to bottom, #f4e4bc, #e6d5a8, #d6c498); border: 8px solid #5c3a1e; border-radius: 4px; box-shadow: inset 0 0 30px rgba(0,0,0,0.2), 10px 10px 20px rgba(0,0,0,0.5); padding: 40px 50px; color: #2b1d0e; font-family: 'Lora', serif; font-size: 1.15rem; line-height: 1.8; margin-bottom: 30px; }
.parchment-container h1, .parchment-container h2, .parchment-container h3 { font-family: 'Cinzel', serif; color: #5c3a1e; border-bottom: 1px solid #8b6914; padding-bottom: 10px; margin-top: 30px; }
.parchment-container strong { color: #8b0000; }
#MainMenu, footer, header { visibility: hidden; }
.center-btn { display: flex; justify-content: center; margin-top: 40px; }
</style>""", unsafe_allow_html=True)

# ==========================================
# 3. BARRA LATERAL (SEMPRE VISÍVEL)
# ==========================================
with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/391/scroll_1f4dc.png", width=80)
    
    # --- NOVA ÁREA DE CONFIGURAÇÕES (NÃO SOME MAIS) ---
    with st.expander("⚙️ Configurações (API Key)"):
        api_key = st.text_input("Sua OpenAI API Key", type="password", help="Necessário se não estiver usando o arquivo .streamlit/secrets.toml")
    st.divider()
    
    st.markdown("### Parâmetros")
    personagem = st.text_input("👤 Personagem")
    historia = st.text_area("📖 História Bíblica", height=120)
    destinatario = st.text_input("✉️ Destinatário")
    tomm = st.selectbox("🎭 Tom", ["Poético", "Urgente", "Materno", "Solene", "Mistério"])
    divisoes = st.number_input("📑 Qtd de Cartas", min_value=1, max_value=5, value=2)
    versao = st.selectbox("🔍 Versão Bíblica", ["ARA", "NVI", "ARC", "NLT", "ACF"])

    gerar_btn = st.button("✒️ Redigir Manuscritos", type="primary", use_container_width=True)

# ==========================================
# 4. LÓGICA PRINCIPAL
# ==========================================
SYSTEM_PROMPT = """Você é um mestre da literatura epistolar e historiador bíblico. Converta relatos em manuscritos imersivos. Dê voz à alma dos personagens. Regras: 1. Divida na quantidade de cartas exata. 2. Cabeçalho histórico poético em itálico. 3. Termos da época (siclos, papiro). 4. Despedida característica. 5. Ao final de CADA carta, adicione: **"Dica de Curadoria para o Snail Mail"** com sugestões de papel/aroma. 6. Separe cartas com ---. Tons: Mistério (noir, sombras), Poético (natureza, ritmo), Urgente (frases curtas, ofegante), Materno (ternura), Solene (reverência)."""

# Se o botão for clicado E o usuário já tiver entrado
if gerar_btn and st.session_state.logged_in:
    if not personagem or not historia:
        st.error("Por favor, preencha o Personagem e a História.")
    else:
        # Tenta pegar a key da sidebar, se não tiver, tenta dos secrets
        key_to_use = api_key if api_key else st.secrets.get("OPENAI_API_KEY", None)
        
        if not key_to_use:
            st.error("⚠️ Nenhuma API Key encontrada. Por favor, insira na aba 'Configurações' na sidebar.")
        else:
            with st.spinner('Preparando a tinta, esticando o papiro...'):
                try:
                    client = OpenAI(api_key=key_to_use)
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
                    st.session_state.resultado_gerado = manuscript_text
                except Exception as e:
                    st.error(f"Erro ao contactar o escriba: {e}")

# ==========================================
# 5. TELAS (SIGN IN vs APP PRINCIPAL)
# ==========================================
if not st.session_state.logged_in:
    # TELA DE ENTRADA
    st.markdown('<div class="main-title">📜 O Escriba</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">"Dê voz à alma dos personagens"</div>', unsafe_allow_html=True)
    
    st.markdown("<div style='text-align: center; margin-top: 50px;'>")
    if st.button("🚪 Entrar no Estúdio", type="primary", key="login_btn"):
        st.session_state.logged_in = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

else:
    # TELA DO APP PRINCIPAL
    st.markdown('<div class="main-title">📜 O Escriba</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">"Dê voz à alma dos personagens"</div>', unsafe_allow_html=True)

    # Mostra o resultado se existir
    if st.session_state.resultado_gerado:
        st.markdown(f'<div class="parchment-container">{st.session_state.resultado_gerado.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
