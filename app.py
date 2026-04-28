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

.parchment-container { 
    background: linear-gradient(to bottom, #f4e4bc, #e6d5a8, #d6c498); 
    border: 8px solid #5c3a1e; border-radius: 4px; 
    box-shadow: inset 0 0 30px rgba(0,0,0,0.2), 10px 10px 20px rgba(0,0,0,0.5); 
    padding: 40px 50px; color: #2b1d0e; 
    font-family: 'EB Garamond', serif; 
    font-size: 1.25rem; 
    line-height: 1.6;   
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
    personagem = st.text_input("👤 Personagem Principal", help="De quem a história é sobre?")
    narrador = st.text_input("🗣️ Narrador", help="Quem está escrevendo? Pode ser o próprio personagem ou uma testemunha ocular (ex: um anjo, um discípulo, etc).")
    destinatario = st.text_input("✉️ Destinatário")
    tomm = st.selectbox("🎭 Tom", ["Poético", "Urgente", "Materno", "Solene", "Mistério e Aventura"])

with col2:
    versao = st.selectbox("🔍 Versão Bíblica", ["ARA", "NVI", "ARC", "NLT", "ACF"])
    divisoes = st.number_input("📑 Qtd de Cartas", min_value=1, max_value=5, value=2)
    paginas_por_carta = st.number_input("📄 Páginas por Carta", min_value=1, max_value=5, value=2, help="Cada página equivale a cerca de 3 parágrafos densos.")

historia = st.text_area("📖 História Bíblica", height=150)

st.markdown("")
gerar_btn = st.button("✒️ Redigir Manuscritos", type="primary", use_container_width=True)

# ==========================================
# NOVO PROMPT: LINGUAGEM MODERNA + NARRADOR
# ==========================================
SYSTEM_PROMPT = """Você é um mestre da escrita épica e adaptador de histórias bíblicas. Sua missão é transformar relatos em manuscritos imersivos, usando uma LINGUAGEM MODERNA E ACESSÍVEL.

REGRA ABSOLUTAS (NÃO QUEBRE NENHUMA DESSAS):
1. LINGUAGEM MODERNA: Escreva em português atual, elegante, mas sem termos arcaicos ou rebuscados excessivamente (não force palavras como "sículos", "papiros" se não fluir naturalmente). A leitura deve ser fluida como um livro contemporâneo de alta qualidade.
2. DINÂMICA NARRADOR X PERSONAGEM:
- O "Personagem Principal" é o SUJEITO da história (sobre quem estamos falando).
- O "Narrador" é A VOZ que escreve a carta.
- Se o Narrador for o próprio Personagem Principal: Escreva em 1ª pessoa (Eu vi, Eu fiz).
- Se o Narrador for uma testemunha/terceira pessoa: Escreva em 3ª pessoa (Ele viu, Ele fez), mas como um relato direto, observacional e cheio de emoção para o Destinatário.
3. FIDELIDADE BÍBLICA: NÃO INVENTE fatos, nomes ou locais. Mantenha TODOS os detalhes bíblicos exatos da história fornecida, apenas adapte a forma de contar.
4. APLICAÇÃO DO TOM (use como tempero na escrita):
- Poético: Metáforas modernas e beleza estética nas palavras.
- Urgente: Ritmo acelerado, frases curtas, pressa.
- Materno: Acolhimento, cuidado contemporâneo e profundo afeto.
- Solene: Reverência, peso e gravidade nas situações.
- Mistério e Aventura: Suspense, tensão, atmosfera de desconhecido, revelações gradativas e ritmo de um thriller/adventure moderno.
5. EXTENSÃO EXATA: Obedeça estritamente à quantidade de PÁGINAS POR CARTA (1 página = aprox. 3 parágrafos longos e densos).
6. ESTRUTURA: Divida na quantidade de cartas exata. Use um cabeçalho contextual em itálico no início de cada carta. Crie despedidas marcantes.
7. FORMATAÇÃO: Separe as cartas usando EXATAMENTE três traços: ---
8. PROIBIÇÃO TOTAL: NÃO adicione dicas de curadoria, papel, aroma, ou "Snail Mail". Apenas escreva o manuscrito."""

if gerar_btn:
    if not personagem or not historia or not narrador:
        st.error("Por favor, preencha o Personagem, o Narrador e a História.")
    else:
        paragrafos_esperados = paginas_por_carta * 3
        max_tokens = (paginas_por_carta * 800) * divisoes 

        with st.spinner(f'Preparando a tinta... Redigindo {divisoes} cartas de {paginas_por_carta} páginas cada.'):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                
                # Adicionado o narrador ao prompt do usuário
                user_prompt = f"Personagem Principal (Sujeito): {personagem}\nNarrador (Voz que escreve): {narrador}\nDestinatário: {destinatario}\nTom: {tomm}\nDivisões: {divisoes} cartas.\nTAMANHO: Cada carta deve ter {paginas_por_carta} páginas (aproximadamente {paragrafos_esperados} parágrafos longos).\nVersão: {versao}\nHistória Base: {historia}\n\nEscreva os manuscritos agora."
                
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
