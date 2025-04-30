import yfinance as yf
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

# =============================================
# Parte 1: Cálculo do Country Risk Premium (CRP)
# =============================================

def fetch_us_treasuries():
    """Coleta dados dos US Treasuries com diferentes durações"""
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
        except Exception as e:
            print(f"Erro ao coletar {ticker}: {str(e)}")
    
    return sorted(us_data, key=lambda x: x[0])

def fetch_brazil_bonds():
    """Coleta dados dos títulos brasileiros via API do BCB"""
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
    except Exception as e:
        print(f"Erro ao coletar dados do Brasil: {str(e)}")
        return []

def fetch_bcb_exchange_rate():
    """Obtém a taxa de câmbio implícita do BCB"""
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.10813/dados/ultimos/1?formato=json"
    response = requests.get(url)
    data = response.json()
    return float(data[0]['valor'])

def calculate_crp(br_data, us_data):
    """Calcula o Country Risk Premium"""
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
    except Exception as e:
        print(f"Erro no cálculo: {str(e)}")
        return None

# =============================================
# Parte 2: Coleta de dados complementares
# =============================================

def get_cambio_bcb():
    """Obtém a taxa de câmbio direto do BCB"""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json"
        response = requests.get(url)
        data = response.json()
        return float(data[0]['valor'])
    except Exception as e:
        print(f"Erro ao obter câmbio BCB: {str(e)}")
        return None

def get_investing_data(url):
    """Coleta dados genéricos do Investing com tratamento robusto"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        # Novos seletores atualizados
        selectors = [
            ('div[data-test="instrument-price-last"]', 1),
            ('span[data-test="instrument-price-last"]', 2),
            ('div.quotesHeaderPesquisa', 3)
        ]
        
        for selector, method in selectors:
            element = soup.select_one(selector)
            if element:
                data = element.text.strip()
                print(f"Debuger-> Valor encontrado (método {method} - selector{selector}): {data}")
                return clean_and_convert_number(data)
        
        # Fallback para JavaScript embedded
        script_data = soup.find('script', text=re.compile('window.__INITIAL_STATE__'))
        if script_data:
            match = re.search(r'"last":([\d.]+)', script_data.text)
            if match:
                print(f"Valor encontrado (método 4): {match.group(1)}")
                return float(match.group(1))
        
        raise ValueError("Nenhum seletor funcionou")
        
    except Exception as e:
        print(f"Erro no scraping: {str(e)}")
        return None

def clean_and_convert_number(text):
    """Conversão robusta para números"""
    clean_text = re.sub(r'[^\d.,+-]', '', text)
    
    # Trata formato brasileiro
    if ',' in clean_text and '.' in clean_text:
        clean_text = clean_text.replace('.', '').replace(',', '.')
    elif ',' in clean_text:
        clean_text = clean_text.replace(',', '.')
    
    return float(clean_text)

# =============================================
# Execução principal
# =============================================

def main():
    print("=== Cálculo do Country Risk Premium (CRP) ===")
    us_data = fetch_us_treasuries()
    br_data = fetch_brazil_bonds()
    
    crp = calculate_crp(br_data, us_data) if us_data and br_data else None
    
    print("\n=== Dados de Mercado ( Web Scrap )===")
    cambio = get_cambio_bcb()  # Usando BCB para câmbio
    taxa_br = get_investing_data('https://www.investing.com/rates-bonds/brazil-10-year-bond-yield')
    taxa_eua = get_investing_data('https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield')
    
    print("\n=== Resultados Finais ===")
    print(f"CRP (Risco País): {crp} bps {'(Negativo - Risco Elevado)' if crp and crp < 0 else ''}")
    print(f"Taxa de Juros Brasil 10 anos: {taxa_br}%" if taxa_br else "Taxa Brasil indisponível")
    print(f"Taxa de Juros EUA 10 anos: {taxa_eua}%" if taxa_eua else "Taxa EUA indisponível")
    print(f"Câmbio USD/BRL (BCB): {cambio}" if cambio else "Câmbio indisponível")
    
    if None not in [crp, taxa_br, taxa_eua, cambio]:
        analise = taxa_br - taxa_eua - cambio/100 - crp/10000
        print(f"\nAnálise Integrada: {analise:.2f}%")
        print("(Valores negativos indicam maior risco Brasil)")

if __name__ == "__main__":
    main()
