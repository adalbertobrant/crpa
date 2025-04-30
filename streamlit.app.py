# app_crpa_streamlit.py

import streamlit as st
import yfinance as yf
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

st.set_page_config(page_title="Country Risk Premium - Brasil", layout="centered")

# ============================
# Funções de dados e cálculo
# ============================

def fetch_us_treasuries():
    treasuries = {
        '2Y': '^FVX',
        '5Y': '^FVX',
        '10Y': '^TNX',
        '30Y': '^TYX'
    }
    us_data = []
    for dur, ticker in treasuries.items():
        try:
            bond = yf.Ticker(ticker)
            hist = bond.history(period="1d")
            yield_pct = hist['Close'].iloc[-1]
            yield_decimal = yield_pct / 100 if yield_pct > 1 else yield_pct
            duration = float(dur.strip('Y'))
            us_data.append((duration, yield_decimal))
        except:
            continue
    return sorted(us_data, key=lambda x: x[0])

def fetch_brazil_bonds():
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/1?formato=json"
        response = requests.get(url)
        data = response.json()
        taxa_br = float(data[0]['valor']) / 100
        exchange_rate = fetch_bcb_exchange_rate()
        vencimento = datetime(2035, 5, 15)
        hoje = datetime.now()
        duration = (vencimento - hoje).days / 365
        usd_yield = taxa_br / exchange_rate
        return [(round(duration, 1), usd_yield)]
    except:
        return []

def fetch_bcb_exchange_rate():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados/ultimos/1?formato=json"
    response = requests.get(url)
    data = response.json()
    return float(data[0]['valor'])

def calculate_crp(br_data, us_data):
    try:
        br_durations = np.array([d for d, y in br_data])
        br_yields = np.array([y for d, y in br_data])
        us_durations = np.array([d for d, y in us_data])
        us_yields = np.array([y for d, y in us_data])
        min_dur = max(min(br_durations), min(us_durations))
        max_dur = min(max(br_durations), max(us_durations))
        common_durations = np.linspace(min_dur, max_dur, 100)
        br_interp = np.interp(common_durations, br_durations, br_yields)
        us_interp = np.interp(common_durations, us_durations, us_yields)
        spread = br_interp - us_interp
        crp_bps = np.mean(spread) * 10000
        return round(crp_bps, 2)
    except:
        return None

def get_cambio_bcb():
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json"
        response = requests.get(url)
        data = response.json()
        return float(data[0]['valor'])
    except:
        return None

def get_investing_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8'
    }
    try:
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        selectors = [
            ('div[data-test="instrument-price-last"]', 1),
            ('span[data-test="instrument-price-last"]', 2),
            ('div.quotesHeaderPesquisa', 3)
        ]
        for selector, _ in selectors:
            element = soup.select_one(selector)
            if element:
                return clean_and_convert_number(element.text.strip())
        return None
    except:
        return None

def clean_and_convert_number(text):
    clean_text = re.sub(r'[^\d.,+-]', '', text)
    if ',' in clean_text and '.' in clean_text:
        clean_text = clean_text.replace('.', '').replace(',', '.')
    elif ',' in clean_text:
        clean_text = clean_text.replace(',', '.')
    return float(clean_text)

# ============================
# Interface Streamlit
# ============================

st.title("📈 Country Risk Premium - Brasil")
st.markdown("Este app calcula o **Country Risk Premium (CRP)** com base em dados dos EUA e Brasil.")

if st.button("🔄 Atualizar dados"):
    with st.spinner("Coletando dados..."):
        us_data = fetch_us_treasuries()
        br_data = fetch_brazil_bonds()
        crp = calculate_crp(br_data, us_data) if us_data and br_data else None

        cambio = get_cambio_bcb()
        taxa_br = get_investing_data('https://www.investing.com/rates-bonds/brazil-10-year-bond-yield')
        taxa_eua = get_investing_data('https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield')

    st.subheader("📊 Resultados")
    st.write(f"**CRP (Risco País):** {crp} bps" if crp is not None else "Erro ao calcular CRP")
    st.write(f"**Taxa Brasil 10 anos:** {taxa_br}%" if taxa_br else "Indisponível")
    st.write(f"**Taxa EUA 10 anos:** {taxa_eua}%" if taxa_eua else "Indisponível")
    st.write(f"**Câmbio USD/BRL:** {cambio}" if cambio else "Indisponível")

    if None not in [crp, taxa_br, taxa_eua, cambio]:
        analise = taxa_br - taxa_eua - cambio / 100 - crp / 10000
        st.subheader("📉 Análise Integrada")
        st.markdown(f"**Resultado:** {analise:.2f}% {'(⚠️ Maior risco Brasil)' if analise < 0 else '(✅ Risco controlado)'}")

else:
    st.info("Clique no botão acima para iniciar a análise.")


