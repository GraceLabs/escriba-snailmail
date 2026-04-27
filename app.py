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

/* ESTILO DO BOTÃO DE PDF */
.pdf-btn { background: #3e2c18; color: #e6dcc3; font-family: 'MedievalSharp', cursive; font-size: 1.2rem; border: 2px solid #c9a84c; border-radius: 8px; padding: 12px 24px; cursor: pointer; transition: all 0.3s ease; display: inline-block; text-decoration: none; }
.pdf-btn:hover { background: #c9a84c; color: #1a1209; }

/* MODO DE IMPRESSÃO / PDF (ESCONDE TUDO E DEIXA SÓ O PERGAMINHO) */
@media print {
    body { background: white !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
    .stApp, .main { background: white !important; padding: 0 !important; margin: 0 !important; overflow: visible !important; }
    [data-testid="stSidebar"], .stButton, .stTextInput, .stTextArea, .stSelectbox, .stNumberInput, .divider-gold, .main-title, .subtitle, #MainMenu, header, footer, .stToolbar, .pdf-container { display: none !important; }
    .parchment-container { 
        border: 2px solid #5c3a1e !important; 
        box-shadow: none !important; 
        padding: 20px !important; 
        margin: 0 !important;
        color: #2b1d0e !important;
        background: white !important;
        font-size: 12pt !important; 
        line-height: 1.5 !important;
    }
}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📜 O Escriba</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">"Dê voz à alma dos personagens"</div>', unsafe_allow_html=True)
st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    personagem = st.text_input("👤 Personagem Principal", help="De quem a história é sobre?")
    narrador = st.text_input("🗣️ Narrador", help="Quem está escrevendo? Pode ser o próprio personagem ou uma testemunha ocular.")
    destinatario = st.text_input("✉️ Destinatário")
    tomm = st.selectbox("🎭 Tom", ["Poético", "Urgente", "Materno", "Solene", "Mistério e Aventura"])

with col2:
    versao = st.selectbox("🔍 Versão Bíblica", ["ARA", "NVI", "ARC", "NLT", "ACF"])
    divisoes = st.number_input("📑 Qtd de Cartas", min_value=1, max_value=5, value=2)
    paginas_por_carta = st.number_input("📄 Páginas por Carta", min_value=1, max_value=5, value=2, help="Cada página equivale a cerca de 3 parágrafos densos.")

historia = st.text_area("📖 História Bíblica", height=150)

st.markdown("")
gerar_btn = st.button("✒️ Redigir Manuscritos", type="primary", use_container_width=True)

SYSTEM_PROMPT = """Você é um mestre da escrita épica e adaptador de histórias bíblicas. Sua missão é transformar relatos em manuscritos imersivos, usando uma LINGUAGEM MODERNA E ACESSÍVEL.

REGRA ABSOLUTAS (NÃO QUEBRE NENHUMA DESSAS):
1. LINGUAGEM MODERNA: Escreva em português atual, elegante, mas sem termos arcaicos. A leitura deve ser fluida como um livro contemporâneo de alta qualidade.
2. DINÂMICA NARRADOR X PERSONAGEM:
- O "Personagem Principal" é o SUJEITO da história.
- O "Narrador" é A VOZ que escreve a carta.
- Se o Narrador for o próprio Personagem Principal: Escreva em 1ª pessoa (Eu vi, Eu fiz).
- Se o Narrador for uma testemunha/terceira pessoa: Escreva em 3ª pessoa (Ele viu, Ele fez), mas como um relato direto, observacional e cheio de emoção.
3. FIDELIDADE BÍBLICA: NÃO INVENTE fatos. Mantenha TODOS os detalhes exatos da história fornecida.
4. APLICAÇÃO DO TOM: Poético (metáforas modernas); Urgente (ritmo acelerado); Materno (acolhimento profundo); Solene (reverência); Mistério e Aventura (suspense, tensão, revelações).
5. EXTENSÃO EXATA: Obedeça à quantidade de PÁGINAS POR CARTA (1 página = aprox. 3 parágrafos longos).
6. ESTRUTURA: Divida nas cartas exatas. Cabeçalho contextual em itálico. Despedidas marcantes. Separe com ---.
7. PROIBIÇÃO TOTAL: NÃO adicione dicas de curadoria, papel, aroma, ou "Snail Mail"."""

if gerar_btn:
    if not personagem or not historia or not narrador:
        st.error("Por favor, preencha o Personagem, o Narrador e a História.")
    else:
        paragrafos_esperados = paginas_por_carta * 3
        max_tokens = (paginas_por_carta * 800) * divisoes 

        with st.spinner(f'Preparando a tinta... Redigindo {divisoes} cartas de {paginas_por_carta} páginas cada.'):
            try:
                client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
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
                
                # Renderiza o texto
                st.markdown(f'<div class="parchment-container">{manuscript_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                
                # BOTÃO DE SALVAR EM PDF (Aparece logo abaixo do texto)
                st.markdown("""
                <div class="pdf-container" style="text-align: center; margin-bottom: 50px;">
                    <button class="pdf-btn" onclick="window.print()">📥 Salvar Manuscrito em PDF</button>
                    <p style="font-size: 0.9rem; color: #a89272; margin-top: 5px;">(Ao clicar, escolha 'Salvar como PDF' na janela que abrir)</p>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erro ao contactar o escriba: {e}")
