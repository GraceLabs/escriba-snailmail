import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title="O Escriba", page_icon="📜", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=MedievalSharp&display=swap');

.stApp { background: linear-gradient(135deg, #2b1d0e 0%, #1a1209 100%); color: #e6dcc3; }
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], #MainMenu, footer, header { display: none !important; }

.main-title { font-family: 'MedievalSharp', cursive; color: #c9a84c; text-align: center; font-size: 3.5rem; text-shadow: 2px 2px 4px #000000; margin-bottom: 10px; letter-spacing: 2px; }
.subtitle { font-family: 'EB Garamond', serif; color: #a89272; text-align: center; font-style: italic; font-size: 1.6rem; margin-bottom: 30px; }

.stTextInput, .stTextArea, .stSelectbox, .stNumberInput { background-color: #1a1209 !important; border: 1px solid #5c4a2a !important; color: #e6dcc3 !important; border-radius: 8px; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label { font-family: 'MedievalSharp', cursive; color: #c9a84c !important; font-weight: bold; font-size: 1.1rem; }

.stButton > button[kind="primary"] { background: linear-gradient(90deg, #8b6914, #c9a84c); color: #1a1209; font-family: 'MedievalSharp', cursive; font-weight: bold; font-size: 1.4rem; border: none; border-radius: 8px; padding: 15px 24px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0px 4px 8px rgba(0,0,0,0.5); transition: all 0.3s ease; width: 100%; }
.stButton > button[kind="primary"]:hover { background: linear-gradient(90deg, #c9a84c, #e6c86e); transform: translateY(-2px); box-shadow: 0px 6px 12px rgba(201, 168, 76, 0.4); }

/* PERGAMINHO AJUSTADO - TAMANHO PADRONIZADO */
.parchment-container { 
    background: linear-gradient(to bottom, #f4e4bc, #e6d5a8, #d6c498); 
    border: 8px solid #5c3a1e; border-radius: 4px; 
    box-shadow: inset 0 0 30px rgba(0,0,0,0.2), 10px 10px 20px rgba(0,0,0,0.5); 
    padding: 40px 50px; color: #2b1d0e; 
    font-family: 'EB Garamond', serif; 
    font-size: 1.25rem; /* TAMANHO PADRONIZADO */
    line-height: 1.6;   /* ESPAÇAMENTO PADRONIZADO */
    margin-bottom: 30px; 
}
.parchment-container h1, .parchment-container h2, .parchment-container h3 { font-family: 'MedievalSharp', cursive; color: #5c3a1e; border-bottom: 1px solid #8b6914; padding-bottom: 10px; margin-top: 30px; font-size: 1.6rem; }
.parchment-container strong { color: #8b0000; }
.divider-gold { border-top: 2px solid #5c3a1e; margin: 30px 0; box-shadow: 0px -2px 10px rgba(201, 168, 76, 0.3); }
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 O Escriba</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">"Dê voz à alma dos personagens"</div>', unsafe_allow_html=True)
st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    personagem = st.text_input("👤 Personagem")
    destinatario = st.text_input("✉️ Destinatário")
    tomm = st.selectbox("🎭 Tom", ["Poético", "Urgente", "Materno", "Solene", "Mistério"])

with col2:
    versao = st.selectbox("🔍 Versão Bíblica", ["ARA", "NVI", "ARC", "NLT", "ACF"])
    divisoes = st.number_input("📑 Qtd de Cartas", min_value=1, max_value=5, value=2)
    paginas_por_carta = st.number_input("📄 Páginas por Carta", min_value=1, max_value=5, value=2, help="Cada página equivale a cerca de 3 parágrafos densos.")

historia = st.text_area("📖 História Bíblica", height=150)

st.markdown("")
gerar_btn = st.button("✒️ Redigir Manuscritos", type="primary", use_container_width=True)

SYSTEM_PROMPT = """Você é um escriba e mestre da literatura epistolar. Sua missão é transformar relatos bíblicos em manuscritos imersivos contados EM PRIMEIRA PESSOA.

REGRA ABSOLUTAS (NÃO QUEBRE NENHUMA DESSAS):
1. EXTENSÃO EXATA: Obedeça estritamente à quantidade de PÁGINAS POR CARTA solicitada pelo usuário. Considere 1 página como aproximadamente 3 parágrafos longos e densos. Não faça menos, não faça mais.
2. PESSOA: O texto DEVE ser escrito estritamente na 1ª pessoa (ex: "Eu vi", "Meu coração ardeu"). O personagem está escrevendo a carta.
3. FIDELIDADE BÍBLICA: NÃO INVENTE fatos, nomes ou locais que não estejam na história fornecida. Mantenha TODOS os detalhes bíblicos exatos. 
4. USO DO TOM: O tom escolhido deve ser usado como um tempero na forma de escrever (ex: se for "urgente", use frases curtas e desespero; se for "materno", use ternura), mas SEM alterar os fatos bíblicos.
5. ESTRUTURA: Divida na quantidade de cartas exata solicitada.
6. ESTÉTICA: Use um cabeçalho histórico poético em itálico no começo de cada carta. Use termos da época (siclos, papiro, cítara, etc.). Crie despedidas características.
7. FORMATAÇÃO: Separe as cartas usando EXATAMENTE três traços: ---
8. PROIBIÇÃO TOTAL: NÃO adicione dicas de curadoria, dicas de papel, aroma, ou qualquer menção a "Snail Mail". Apenas escreva a carta."""

if gerar_btn:
    if not personagem or not historia:
        st.error("Por favor, preencha o Personagem e a História.")
    else:
        paragrafos_esperados = paginas_por_carta * 3
        max_tokens = (paginas_por_carta * 800) * divisoes 

        with st.spinner(f'Preparando a tinta... Redigindo {divisoes} cartas de {paginas_por_carta} páginas cada.'):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                user_prompt = f"Personagem: {personagem}\nHistória: {historia}\nDestinatário: {destinatario}\nTom: {tomm}\nDivisões: {divisoes} cartas.\nTAMANHO: Cada carta deve ter {paginas_por_carta} páginas (aproximadamente {paragrafos_esperados} parágrafos longos).\nVersão: {versao}\n\nEscreva os manuscritos agora."
                
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT}, 
                        {"role": "user", "content": user_prompt}
                    ], 
                    temperature=0.7,
                    max_tokens=max_tokens
                )
                manuscript_text = response.choices[0].message.content
                st.markdown(f'<div class="parchment-container">{manuscript_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erro ao contactar o escriba: {e}")
