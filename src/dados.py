"""
dados.py — Carga e agregações dos dados de emissão (com cache).

Todas as funções de agregação são cacheadas com @st.cache_data, então o
custo é pago uma vez por combinação de parâmetros. Isso torna a interação
no app (clicar em estado, mudar ano) instantânea.
"""

from pathlib import Path
import json

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────
PASTA = Path(__file__).parent.parent  # raiz do projeto

CORES_SETOR = {
    # Paleta "Fogo" — espectro âmbar/fogo, hierarquia clara
    "Mudança de Uso da Terra e Floresta": "#D94F1E",  # fogo intenso — o maior emissor
    "Agropecuária":                       "#E07C20",  # laranja âmbar — sol/terra/gado
    "Energia":                            "#A0522D",  # mogno — combustível fóssil
    "Processos Industriais":              "#8B7355",  # terra ocre — industrial
    "Resíduos":                           "#5C5046",  # cinza-terra — resíduo
}

# Apelidos curtos para gráficos onde o nome completo não cabe
SETOR_CURTO = {
    "Mudança de Uso da Terra e Floresta": "Desmatamento",
    "Agropecuária":                       "Agropecuária",
    "Energia":                            "Energia",
    "Processos Industriais":              "Indústria",
    "Resíduos":                           "Resíduos",
}

SIGLA_NOME = {
    "AC":"Acre","AL":"Alagoas","AM":"Amazonas","AP":"Amapá","BA":"Bahia",
    "CE":"Ceará","DF":"Distrito Federal","ES":"Espírito Santo","GO":"Goiás",
    "MA":"Maranhão","MG":"Minas Gerais","MS":"Mato Grosso do Sul",
    "MT":"Mato Grosso","PA":"Pará","PB":"Paraíba","PE":"Pernambuco",
    "PI":"Piauí","PR":"Paraná","RJ":"Rio de Janeiro","RN":"Rio Grande do Norte",
    "RO":"Rondônia","RR":"Roraima","RS":"Rio Grande do Sul","SC":"Santa Catarina",
    "SE":"Sergipe","SP":"São Paulo","TO":"Tocantins",
}

# Centro geográfico aproximado de cada UF (lat, lon) — usado para zoom no mapa
CENTROIDE_UF = {
    "AC":(-9.0,-70.0),"AL":(-9.6,-36.6),"AM":(-3.9,-65.0),"AP":(1.4,-51.8),
    "BA":(-12.5,-41.7),"CE":(-5.2,-39.6),"DF":(-15.8,-47.9),"ES":(-19.6,-40.3),
    "GO":(-15.9,-49.6),"MA":(-5.4,-45.4),"MG":(-18.5,-44.5),"MS":(-20.5,-54.5),
    "MT":(-12.9,-55.9),"PA":(-4.0,-52.5),"PB":(-7.1,-36.8),"PE":(-8.4,-37.9),
    "PI":(-7.7,-42.7),"PR":(-24.5,-51.5),"RJ":(-22.2,-42.7),"RN":(-5.8,-36.6),
    "RO":(-10.9,-62.8),"RR":(2.1,-61.4),"RS":(-30.0,-53.2),"SC":(-27.2,-50.5),
    "SE":(-10.6,-37.4),"SP":(-22.2,-48.7),"TO":(-10.2,-48.3),
}

POP_2022 = {
    "AC":906876,"AL":3351543,"AM":4269995,"AP":877613,"BA":14930634,"CE":9240580,
    "DF":3094325,"ES":4108508,"GO":7206589,"MA":7153262,"MG":21411923,"MS":2833742,
    "MT":3784239,"PA":8777124,"PB":4059905,"PE":9674793,"PI":3289290,"PR":11597484,
    "RJ":17463349,"RN":3560903,"RO":1815278,"RR":652713,"RS":11466630,"SC":7764977,
    "SE":2338474,"SP":46649132,"TO":1607363,
}

EVENTOS = {
    2003: "Pico histórico — 3.005 Mt (auge do desmatamento)",
    2004: "Lançamento do PPCDAm (política anti-desmatamento)",
    2010: "Mínimo histórico — 1.637 Mt (−45% vs 2003)",
    2019: "Retomada da alta do desmatamento",
}


# ─────────────────────────────────────────────────────────────
# CARGA
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Carregando dados…")
def carregar_seeg() -> pd.DataFrame:
    """Carrega o SEEG tidy do parquet. Se não existir, processa do Excel."""
    cache = PASTA / "data" / "seeg_tidy.parquet"
    if cache.exists():
        df = pd.read_parquet(cache)
        df["setor"] = df["setor"].str.strip()
        return df

    # Fallback: processar do Excel (lento, só na primeira vez)
    excel = PASTA.parent.parent.parent / "dados" / "-SEEG10_GERAL-BR_UF_2022.10.27-FINAL-SITE.xlsx"
    if not excel.exists():
        st.error(
            f"Dados não encontrados. Rode `python src/preparar_dados.py` "
            f"ou coloque o Excel do SEEG em `dados/`."
        )
        st.stop()
    raw = pd.read_excel(excel, sheet_name="GEE Estados", engine="openpyxl")
    raw = raw.rename(columns={
        "Nível 1 - Setor": "setor", "Nível 2": "nivel2",
        "Emissão / Remoção / Bunker": "tipo", "Gás": "gas", "Estado": "estado",
    })
    raw = raw[(raw.gas == "CO2e (t) GWP-AR6") & (raw.tipo == "Emissão") &
              (raw.estado != "NA") & (raw.estado.notna())].copy()
    anos = [c for c in raw.columns if isinstance(c, int) and 1970 <= c <= 2021]
    df = raw.melt(id_vars=["setor", "nivel2", "estado"], value_vars=anos,
                  var_name="ano", value_name="valor_t")
    df["ano"] = df["ano"].astype(int)
    df["valor_mt"] = df["valor_t"] / 1_000_000
    df["setor"] = df["setor"].str.strip()
    df = df.dropna(subset=["valor_mt"]).drop(columns=["valor_t"])
    cache.parent.mkdir(exist_ok=True)
    df.to_parquet(cache, index=False)
    return df


@st.cache_data(show_spinner=False)
def carregar_internacional() -> pd.DataFrame:
    """CO₂ fóssil per capita por país (para comparação Brasil vs Mundo)."""
    caminho = PASTA.parent.parent.parent / "dados" / "co2_percapita.xlsx"
    if not caminho.exists():
        return pd.DataFrame()
    df = pd.read_excel(caminho)
    df = df[["País", "Ano", "Total"]].dropna(subset=["Total"])
    df["t_per_capita"] = df["Total"] / 1_000_000  # normaliza p/ t CO₂/hab
    return df


@st.cache_data(show_spinner=False)
def carregar_geojson() -> dict:
    """GeoJSON das UFs do Brasil (chave: properties.sigla)."""
    with open(PASTA / "brasil_uf.geojson", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────
# AGREGAÇÕES CACHEADAS (interação instantânea)
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def serie_setor_nacional(_df: pd.DataFrame) -> pd.DataFrame:
    """Emissão por ano × setor (Brasil)."""
    return _df.groupby(["ano", "setor"])["valor_mt"].sum().reset_index()


@st.cache_data(show_spinner=False)
def total_nacional(_df: pd.DataFrame) -> pd.DataFrame:
    """Emissão total por ano (Brasil)."""
    return _df.groupby("ano")["valor_mt"].sum().reset_index()


@st.cache_data(show_spinner=False)
def mapa_por_estado(_df: pd.DataFrame, ano: int, per_capita: bool) -> pd.DataFrame:
    """Emissão por estado num ano específico (para o mapa)."""
    d = _df[_df.ano == ano].groupby("estado")["valor_mt"].sum().reset_index()
    d["nome"] = d["estado"].map(SIGLA_NOME)
    if per_capita:
        d["valor"] = d["valor_mt"] * 1_000_000 / d["estado"].map(POP_2022)
        d["unidade"] = "t CO₂e/hab"
    else:
        d["valor"] = d["valor_mt"]
        d["unidade"] = "Mt CO₂e"
    return d


@st.cache_data(show_spinner=False)
def heatmap_estados(_df: pd.DataFrame) -> pd.DataFrame:
    """Matriz estado × ano (pivot) para heatmap."""
    piv = _df.groupby(["estado", "ano"])["valor_mt"].sum().reset_index()
    piv = piv.pivot(index="estado", columns="ano", values="valor_mt")
    # ordenar por total acumulado (maiores no topo)
    piv = piv.loc[piv.sum(axis=1).sort_values(ascending=True).index]
    return piv


@st.cache_data(show_spinner=False)
def treemap_data(_df: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Setor → subsetor → estado para treemap de um ano."""
    d = _df[_df.ano == ano].groupby(["setor", "nivel2", "estado"])["valor_mt"].sum().reset_index()
    return d[d["valor_mt"] > 0]


@st.cache_data(show_spinner=False)
def mapa_acumulado(_df: pd.DataFrame, per_capita: bool) -> pd.DataFrame:
    """Soma de todos os anos (1970-2021) por estado — para o toggle 'Acumulado'."""
    d = _df.groupby("estado")["valor_mt"].sum().reset_index()
    d["nome"] = d["estado"].map(SIGLA_NOME)
    if per_capita:
        d["valor"] = d["valor_mt"] * 1_000_000 / d["estado"].map(POP_2022)
        d["unidade"] = "t CO₂e/hab (1970–2021)"
    else:
        d["valor"] = d["valor_mt"]
        d["unidade"] = "Mt CO₂e (total 1970–2021)"
    return d


def drill_estado(df: pd.DataFrame, uf: str, ano: int = 2021) -> dict:
    """Dados detalhados de um estado para o painel de drill-down.

    Sem @st.cache_data — a função é rápida (pandas groupby em memória)
    e o cache causava conflito de assinatura com o parâmetro `ano`.
    O parâmetro `ano` controla qual ano é usado para composição, subsetores
    e KPIs (corrige bug onde o painel sempre mostrava 2021).
    """
    sub = df[df.estado == uf]
    serie = sub.groupby(["ano", "setor"])["valor_mt"].sum().reset_index()
    composicao = sub[sub.ano == ano].groupby("setor")["valor_mt"].sum().reset_index()
    subsetores = (sub[sub.ano == ano].groupby("nivel2")["valor_mt"].sum()
                  .sort_values(ascending=False).reset_index())
    total_ano = sub[sub.ano == ano]["valor_mt"].sum()
    return {
        "serie": serie,
        "composicao": composicao,
        "subsetores": subsetores,
        "total_ano": total_ano,
        "per_capita_ano": total_ano * 1_000_000 / POP_2022.get(uf, 1),
        "ano": ano,
    }


@st.cache_data(show_spinner=False)
def top_estados_serie(_df: pd.DataFrame, n: int = 6) -> dict:
    """Top N estados por emissão acumulada + série histórica anual de cada um."""
    totais = _df.groupby("estado")["valor_mt"].sum().nlargest(n)
    series = {}
    for uf in totais.index:
        series[uf] = _df[_df.estado == uf].groupby("ano")["valor_mt"].sum().reset_index()
    return {"ranking": totais, "series": series}


@st.cache_data(show_spinner=False)
def delta_estados(_df: pd.DataFrame, ano_ini: int = 2003, ano_fim: int = 2021) -> pd.DataFrame:
    """Variação de emissão de cada estado entre dois anos (para ranking quem melhorou)."""
    a = _df[_df.ano == ano_ini].groupby("estado")["valor_mt"].sum()
    b = _df[_df.ano == ano_fim].groupby("estado")["valor_mt"].sum()
    delta = (b - a).reset_index()
    delta.columns = ["estado", "delta_mt"]
    delta["nome"] = delta["estado"].map(SIGLA_NOME)
    return delta.sort_values("delta_mt")


@st.cache_data(show_spinner=False)
def brasil_gee_per_capita_2021(_df: pd.DataFrame) -> float:
    """Total GEE per capita do Brasil em 2021 (t CO₂e/pessoa), calculado do SEEG."""
    total_mt  = _df[_df.ano == 2021]["valor_mt"].sum()
    pop_total = sum(POP_2022.values())
    return total_mt * 1_000_000 / pop_total


@st.cache_data(show_spinner=False)
def kpis_nacionais(_df: pd.DataFrame) -> dict:
    """KPIs do header."""
    tot = total_nacional(_df)
    set21 = _df[_df.ano == 2021].groupby("setor")["valor_mt"].sum().sort_values(ascending=False)
    ano_pico = int(tot.loc[tot.valor_mt.idxmax(), "ano"])
    mt_pico = tot.valor_mt.max()
    mt_2021 = tot[tot.ano == 2021].valor_mt.values[0]
    return {
        "ano_pico": ano_pico,
        "mt_pico": mt_pico,
        "mt_2021": mt_2021,
        "delta_pct": (mt_2021 / mt_pico - 1) * 100,
        "maior_setor": set21.index[0],
        "pct_maior": set21.iloc[0] / set21.sum() * 100,
        "pct_top2": set21.iloc[:2].sum() / set21.sum() * 100,
    }
