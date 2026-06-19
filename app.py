import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from simulador_categorias import calculo_final_cupons

@st.cache_data
def carregar_dados():
    return pd.read_csv("simulador_de_cupons.csv", sep=";", encoding="utf-8-sig")

df = carregar_dados()

st.set_page_config(
    page_title="Simulador de Cupons",
    layout="wide"
)

col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    st.image("logo.png", width=120)

with col_titulo:
    st.title("Simulador de Cupons")

st.header("Parâmetros")

col1, col2 = st.columns(2)

# =========================
# Inputs
# =========================
with col1:
    margem = st.number_input(
        "Margem (%) - (valores entre 0 e 100%, 0.3 significa 30%)",
        value=0.16,
        step=0.01,
        min_value=0.00,
        max_value=1.00
    )

    valor_cupom = st.number_input(
        "Valor do Cupom (R$)",
        value=20.0,
        step=1.0,
        min_value=0.0
    )

    gasto_minimo = st.number_input(
        "Gasto Mínimo na Categoria (R$)",
        value=100.0,
        step=1.0,
        min_value=0.0
    )
    st.markdown("---")

    conversao_high = st.number_input(
        "Prob. de um cliente HIGH usar o cupom - (valores entre 0 e 100%, 0.3 significa 30%)",
        value=0.10,
        step=0.01,
        min_value=0.00,
        max_value=1.00
    )

    conversao_medium = st.number_input(
        "Prob. de um cliente MEDIUM usar o cupom - (valores entre 0 e 100%, 0.3 significa 30%)",
        value=0.05,
        step=0.01,
        min_value=0.00,
        max_value=1.00
    )

    conversao_low = st.number_input(
        "Prob. de um cliente LOW usar o cupom - (valores entre 0 e 100%, 0.3 significa 30%)",
        value=0.02,
        step=0.01,
        min_value=0.00,
        max_value=1.00
    )

with col2:
    valor_incremento_high = st.number_input(
        "Incremento máximo na categoria de gasto HIGH (R$)",
        value=50.0,
        step=1.0
    )

    valor_incremento_medium = st.number_input(
        "Incremento máximo na categoria  de gasto MEDIUM (R$)",
        value=50.0,
        step=1.0
    )

    valor_incremento_low = st.number_input(
        "Incremento máximo na categoria  de gasto LOW (R$)",
        value=50.0,
        step=1.0
    )

    missao_escolhida = st.selectbox(
        "Qual Categoria Simular?",
        ['AÇOUGUE', 'LIMPEZA', 'PERFUMARIA']
    )


# =========================
# Rodar simulação
# =========================


if st.button("Executar Simulação"):

    try:
        tb_total, tb_segmento_ps, tb_segmento_estrategico = calculo_final_cupons(
            df,
            margem=margem,
            valor_cupom=valor_cupom,
            gasto_minimo = gasto_minimo,
            conversao_high=conversao_high,
            conversao_medium=conversao_medium,
            conversao_low=conversao_low,
            valor_incremento_high=valor_incremento_high,
            valor_incremento_medium=valor_incremento_medium,
            valor_incremento_low=valor_incremento_low,
            missao_de_compra=missao_escolhida
        )

        aba1, aba2, aba3 = st.tabs([
            "Resultado Geral",
            "Resultado por Segmento People Scope",
            "Resultado por Segmento Estratégico"
        ])

        with aba1:
            st.dataframe(tb_total, use_container_width=True)

        with aba2:
            st.dataframe(tb_segmento_ps, use_container_width=True)
            
        with aba3:
            st.dataframe(tb_segmento_estrategico, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao calcular simulação: {e}")