"""
graficos.py — Funções que constroem as figuras Plotly.

Cada função recebe dados já agregados (de dados.py) e devolve uma figura
com tema dark consistente. Nenhuma faz I/O — só visualização.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .dados import CORES_SETOR, SETOR_CURTO, SIGLA_NOME, CENTROIDE_UF, EVENTOS

# ── Paleta "Fogo" ───────────────────────────────────────────
BG    = "#0F0A06"   # marrom muito escuro — terra queimada
PANEL = "#1A1109"   # superfície quente
TXT   = "#B8967A"   # âmbar opaco — labels, eixos
GRID  = "#2E1E10"   # grade quente
TXT_P = "#F0D8B8"   # pergaminho — texto principal

# Escala do mapa: pergaminho pálido → laranja → vinho escuro
MAP_SCALE = [
    (0.0,  "#1A0E06"),
    (0.20, "#4A1E08"),
    (0.45, "#8B3A10"),
    (0.68, "#C9561A"),
    (0.85, "#E07C20"),
    (1.0,  "#F5A623"),
]


def _dark(fig: go.Figure, panel: bool = True, h: int = 400) -> go.Figure:
    """Aplica tema escuro consistente."""
    bg = PANEL if panel else BG
    fig.update_layout(
        paper_bgcolor=bg, plot_bgcolor=bg, font_color=TXT,
        margin=dict(l=10, r=10, t=30, b=10), height=h,
        legend=dict(font=dict(size=11, color=TXT)),
        xaxis=dict(gridcolor=GRID, color=TXT, linecolor=GRID),
        yaxis=dict(gridcolor=GRID, color=TXT, linecolor=GRID),
        font=dict(family="Inter, -apple-system, sans-serif"),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# MAPA NACIONAL — estático e CLICÁVEL (leve, 1 ano por vez)
# ─────────────────────────────────────────────────────────────
def mapa_brasil(df_estado, geojson, titulo_unidade: str) -> go.Figure:
    fig = px.choropleth(
        df_estado,
        geojson=geojson,
        locations="estado",
        featureidkey="properties.sigla",
        color="valor",
        color_continuous_scale=MAP_SCALE,
        hover_name="nome",
        hover_data={"estado": False, "valor": ":.1f"},
        scope="south america",
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor=BG)
    fig.update_traces(
        marker_line_color="#555", marker_line_width=0.4,
        customdata=df_estado[["estado"]].values,  # p/ capturar clique
        hovertemplate="<b>%{hovertext}</b><br>%{z:.1f} " + titulo_unidade + "<extra></extra>",
    )
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG, font_color=TXT,
        margin=dict(l=0, r=0, t=0, b=0), height=560,
        coloraxis_colorbar=dict(
            title=dict(text=titulo_unidade, font=dict(color="#bbb")),
            tickfont=dict(color="#bbb"), thickness=14, len=0.7,
        ),
        dragmode=False,
    )
    return fig


def mapa_estado_zoom(geojson, uf: str) -> go.Figure:
    """Mapa com zoom num estado específico (destaca a UF selecionada)."""
    lat, lon = CENTROIDE_UF.get(uf, (-15, -50))
    feats = [f for f in geojson["features"] if f["properties"].get("sigla") == uf]
    mini = {"type": "FeatureCollection", "features": feats}

    fig = go.Figure(go.Choropleth(
        geojson=mini,
        locations=[uf],
        featureidkey="properties.sigla",
        z=[1],
        colorscale=[[0, "#e63946"], [1, "#e63946"]],
        showscale=False,
        marker_line_color="#fff", marker_line_width=1.2,
        hovertext=[SIGLA_NOME.get(uf, uf)],
        hovertemplate="<b>%{hovertext}</b><extra></extra>",
    ))
    fig.update_geos(
        fitbounds="locations", visible=True, bgcolor=PANEL,
        showcountries=False, showcoastlines=False, showland=True,
        landcolor="#18181B", center=dict(lat=lat, lon=lon),
    )
    fig.update_layout(paper_bgcolor=PANEL, margin=dict(l=0, r=0, t=0, b=0), height=240)
    return fig


# ─────────────────────────────────────────────────────────────
# HEATMAP estados × anos
# ─────────────────────────────────────────────────────────────
def heatmap_estados_anos(piv) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=piv.values,
        x=piv.columns,
        y=[SIGLA_NOME.get(s, s) for s in piv.index],
        colorscale="YlOrRd",
        colorbar=dict(title="Mt CO₂e", tickfont=dict(color="#bbb"),
                      title_font=dict(color="#bbb")),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f} Mt CO₂e<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font_color=TXT,
        margin=dict(l=10, r=10, t=10, b=10), height=620,
        xaxis=dict(title="Ano", dtick=5),
        yaxis=dict(title=""),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# SÉRIE empilhada (Mt) com eventos anotados
# ─────────────────────────────────────────────────────────────
def serie_empilhada(df_setor, anotar_eventos: bool = True) -> go.Figure:
    fig = px.area(
        df_setor, x="ano", y="valor_mt", color="setor",
        color_discrete_map=CORES_SETOR,
        labels={"valor_mt": "Mt CO₂e", "ano": "Ano", "setor": "Setor"},
    )
    if anotar_eventos:
        totais = df_setor.groupby("ano")["valor_mt"].sum()
        for ano in [2003, 2010]:
            if ano in totais.index:
                fig.add_annotation(
                    x=ano, y=totais[ano], text=str(ano), showarrow=True,
                    arrowcolor="#ccc", font=dict(color="#ccc", size=11),
                    ax=0, ay=-35,
                )
    fig.update_layout(hovermode="x unified")
    return _dark(fig, h=420)


# ─────────────────────────────────────────────────────────────
# SÉRIE normalizada 100% (composição relativa)
# ─────────────────────────────────────────────────────────────
def serie_normalizada(df_setor) -> go.Figure:
    piv = df_setor.pivot(index="ano", columns="setor", values="valor_mt").fillna(0)
    pct = piv.div(piv.sum(axis=1), axis=0) * 100
    fig = go.Figure()
    for setor in CORES_SETOR:
        if setor in pct.columns:
            fig.add_trace(go.Scatter(
                x=pct.index, y=pct[setor], name=setor, mode="lines",
                stackgroup="one", line=dict(width=0.5, color=CORES_SETOR[setor]),
                hovertemplate="%{y:.0f}%<extra>" + SETOR_CURTO.get(setor, setor) + "</extra>",
            ))
    fig.update_layout(
        yaxis=dict(title="% do total", ticksuffix="%", range=[0, 100]),
        xaxis=dict(title="Ano"), hovermode="x unified",
    )
    return _dark(fig, h=400)


# ─────────────────────────────────────────────────────────────
# DECOMPOSIÇÃO da queda 2003 → 2010 (quem explicou a redução)
# ─────────────────────────────────────────────────────────────
def decomposicao_queda(df, ano_ini=2003, ano_fim=2010) -> go.Figure:
    a = df[df.ano == ano_ini].groupby("setor")["valor_mt"].sum()
    b = df[df.ano == ano_fim].groupby("setor")["valor_mt"].sum()
    delta = (b - a).sort_values()
    cores = ["#2dc653" if v < 0 else "#e63946" for v in delta.values]
    fig = go.Figure(go.Bar(
        x=delta.values,
        y=[SETOR_CURTO.get(s, s) for s in delta.index],
        orientation="h",
        marker_color=cores,
        text=[f"{v:+.0f} Mt" for v in delta.values],
        textposition="outside",
        hovertemplate="%{y}: %{x:+.0f} Mt CO₂e<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(title=f"Variação {ano_ini}→{ano_fim} (Mt CO₂e)"),
        title=dict(text=f"Quem explicou a queda de {ano_ini} a {ano_fim}?",
                   font=dict(size=14)),
    )
    return _dark(fig, h=340)


# ─────────────────────────────────────────────────────────────
# TREEMAP setor → subsetor → estado
# ─────────────────────────────────────────────────────────────
def treemap(df_tree, ano: int) -> go.Figure:
    df = df_tree.copy()
    df["setor_c"] = df["setor"].map(SETOR_CURTO).fillna(df["setor"])
    fig = px.treemap(
        df,
        path=[px.Constant(f"Brasil {ano}"), "setor_c", "nivel2", "estado"],
        values="valor_mt",
        color="setor_c",
        color_discrete_map={SETOR_CURTO.get(k, k): v for k, v in CORES_SETOR.items()},
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>%{value:.0f} Mt CO₂e<br>%{percentRoot} do total<extra></extra>",
        root_color=PANEL,
    )
    fig.update_layout(paper_bgcolor=PANEL, font_color=TXT,
                      margin=dict(l=0, r=0, t=10, b=0), height=520)
    return fig


# ─────────────────────────────────────────────────────────────
# RANKING de estados
# ─────────────────────────────────────────────────────────────
def ranking_estados(df_estado, unidade: str) -> go.Figure:
    d = df_estado.sort_values("valor", ascending=True).tail(15)
    fig = px.bar(
        d, x="valor", y="nome", orientation="h",
        color="valor", color_continuous_scale="YlOrRd",
        labels={"valor": unidade, "nome": ""},
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f} " + unidade + "<extra></extra>")
    return _dark(fig, h=440)


# ─────────────────────────────────────────────────────────────
# SCATTER — emissão absoluta vs per capita (bolha = população)
# ─────────────────────────────────────────────────────────────
def scatter_abs_percapita(df_estado_abs, df_estado_pc, pop_map) -> go.Figure:
    import pandas as pd
    d = df_estado_abs[["estado", "nome", "valor"]].rename(columns={"valor": "absoluto"})
    d = d.merge(df_estado_pc[["estado", "valor"]].rename(columns={"valor": "percapita"}), on="estado")
    d["pop_mi"] = d["estado"].map(pop_map) / 1_000_000
    fig = px.scatter(
        d, x="absoluto", y="percapita", size="pop_mi", text="estado",
        color="percapita", color_continuous_scale="YlOrRd",
        labels={"absoluto": "Emissão total (Mt CO₂e)",
                "percapita": "Emissão per capita (t CO₂e/hab)",
                "pop_mi": "População (mi)"},
        size_max=45,
    )
    fig.update_traces(textposition="top center", textfont=dict(size=9, color="#ccc"),
                      hovertemplate="<b>%{text}</b><br>Total: %{x:.0f} Mt<br>"
                                    "Per capita: %{y:.1f} t/hab<extra></extra>")
    fig.update_layout(coloraxis_showscale=False)
    return _dark(fig, h=460)


# ─────────────────────────────────────────────────────────────
# BRASIL vs MUNDO — CO₂ fóssil per capita
# ─────────────────────────────────────────────────────────────
def brasil_total_vs_mundo(brasil_total_pc: float) -> go.Figure:
    """Total GEE per capita (inclui desmatamento) — o 'plot twist'.
    Contrasta com brasil_vs_mundo() que só mostra CO₂ fóssil.
    Dados: EDGAR 2022 para outros países; SEEG 2022 para Brasil."""
    import pandas as pd

    # Dados internacionais — total GHG per capita 2021
    # Fonte: EDGAR v8 / Global Carbon Budget 2022
    dados = {
        "EUA":           16.1,
        "Austrália":     14.8,
        "Rússia":        13.2,
        "Canadá":        13.0,
        "Brasil\n(SEEG)": round(brasil_total_pc, 1),
        "China":          9.5,
        "U. Europeia":    7.5,
        "Média mundial":  6.8,
        "Índia":          2.8,
    }

    df = pd.DataFrame(list(dados.items()), columns=["pais", "valor"])
    df = df.sort_values("valor")  # menor → maior (horizontal)

    cores = []
    for p in df["pais"]:
        if "Brasil" in p:
            cores.append("#E07C20")      # âmbar destaque
        elif "Média" in p:
            cores.append("#6B4E35")      # cinza-terra para média mundial
        else:
            cores.append("#5C3818")      # marrom escuro para os outros

    fig = go.Figure(go.Bar(
        x=df["valor"],
        y=df["pais"],
        orientation="h",
        marker_color=cores,
        marker_line_width=0,
        text=[f"{v:.1f} t" for v in df["valor"]],
        textposition="outside",
        textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{y}</b><br>%{x:.1f} t CO₂e/pessoa<extra></extra>",
    ))
    # Linha da média mundial
    media_val = dados["Média mundial"]
    fig.add_vline(
        x=media_val, line_color="#6B4E35", line_width=1.5, line_dash="dot",
        annotation_text="Média mundial", annotation_position="top right",
        annotation_font=dict(size=9, color=TXT),
    )
    fig.update_layout(
        xaxis=dict(title="t CO₂e / pessoa (2021)", color=TXT, gridcolor=GRID),
        yaxis=dict(title="", color=TXT),
        font=dict(family="Inter, -apple-system, sans-serif"),
    )
    return _dark(fig, h=380)


def brasil_vs_mundo(df_int, ano: int = 2021) -> go.Figure:
    paises = ["Catar","Austrália","Estados Unidos","Canadá","Rússia","Japão",
              "Alemanha","China","Brasil","Índia"]
    d = df_int[(df_int.Ano == ano) & (df_int["País"].isin(paises))].copy()
    d = d.sort_values("t_per_capita", ascending=True)
    cores = ["#2dc653" if p == "Brasil" else "#457b9d" for p in d["País"]]
    fig = go.Figure(go.Bar(
        x=d["t_per_capita"], y=d["País"], orientation="h",
        marker_color=cores,
        text=[f"{v:.1f}" for v in d["t_per_capita"]], textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:.1f} t CO₂ fóssil/hab<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(title="t CO₂ fóssil per capita (" + str(ano) + ")"),
        title=dict(text="Em CO₂ fóssil, o Brasil é um dos MENORES emissores per capita",
                   font=dict(size=13)),
    )
    return _dark(fig, h=400)


# ─────────────────────────────────────────────────────────────
# Gráficos do DRILL-DOWN de estado
# ─────────────────────────────────────────────────────────────
def drill_serie(serie) -> go.Figure:
    fig = px.area(serie, x="ano", y="valor_mt", color="setor",
                  color_discrete_map=CORES_SETOR,
                  labels={"valor_mt": "Mt CO₂e", "ano": "", "setor": ""})
    fig.update_layout(hovermode="x unified", showlegend=False)
    return _dark(fig, h=220)


def drill_composicao(comp, total_mt: float = 0.0, ano: int = 2021) -> go.Figure:
    """Donut de composição por setor — ordenado do maior para menor,
    com pull no setor dominante e total Mt anotado no centro."""
    comp = comp.copy().sort_values("valor_mt", ascending=False)
    comp["setor_c"] = comp["setor"].map(SETOR_CURTO).fillna(comp["setor"])

    # Pull leve no maior setor (destaque visual)
    pull = [0.07] + [0.0] * (len(comp) - 1)

    cores_ord = [CORES_SETOR.get(s, "#888") for s in comp["setor"]]

    fig = go.Figure(go.Pie(
        labels=comp["setor_c"],
        values=comp["valor_mt"],
        hole=0.60,
        pull=pull,
        marker=dict(colors=cores_ord, line=dict(color=PANEL, width=2)),
        textinfo="percent",
        textfont=dict(size=11, color=TXT),
        sort=False,  # já ordenamos manualmente
        direction="clockwise",
        hovertemplate="<b>%{label}</b><br>%{value:.1f} Mt CO₂e<br>%{percent}<extra></extra>",
    ))

    # Anotação central: total Mt + ano
    fig.add_annotation(
        text=(f"<b style='font-size:15px'>{total_mt:.0f}</b>"
              f"<br><span style='font-size:9px; color:#8B6748'>Mt CO₂e</span>"
              f"<br><span style='font-size:9px; color:#8B6748'>{ano}</span>"),
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=TXT),
        align="center",
    )

    fig.update_layout(
        paper_bgcolor=PANEL, font_color=TXT,
        margin=dict(l=0, r=0, t=0, b=30), height=230,
        showlegend=True,
        legend=dict(font=dict(size=9), orientation="h",
                    y=-0.08, x=0.5, xanchor="center"),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# SMALL MULTIPLES — Top 6 estados, série 1970-2021
# ─────────────────────────────────────────────────────────────
def small_multiples_estados(series_dict: dict, sigla_nome: dict) -> go.Figure:
    """6 mini line charts (2×3), um por estado do top 6.
    Marca automaticamente o pico de cada estado."""
    estados = list(series_dict.keys())
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[sigla_nome.get(uf, uf) for uf in estados],
        vertical_spacing=0.16,
        horizontal_spacing=0.07,
    )
    for i, uf in enumerate(estados):
        row, col = (i // 3) + 1, (i % 3) + 1
        s = series_dict[uf]
        # Área preenchida âmbar
        fig.add_trace(go.Scatter(
            x=s["ano"], y=s["valor_mt"],
            mode="lines",
            line=dict(color="#E07C20", width=2.0),
            fill="tozeroy",
            fillcolor="rgba(224,124,32,0.10)",
            showlegend=False,
            hovertemplate="%{x}: %{y:.0f} Mt<extra></extra>",
        ), row=row, col=col)
        # Marcador no pico
        idx_max = s["valor_mt"].idxmax()
        pico_ano  = s.loc[idx_max, "ano"]
        pico_val  = s.loc[idx_max, "valor_mt"]
        fig.add_trace(go.Scatter(
            x=[pico_ano], y=[pico_val],
            mode="markers+text",
            marker=dict(color="#D94F1E", size=7, line=dict(color=PANEL, width=1)),
            text=[f"{pico_val:.0f}"],
            textposition="top center",
            textfont=dict(size=9, color="#C8A07A"),
            showlegend=False,
            hoverinfo="skip",
        ), row=row, col=col)

    # Estilo dos eixos (todos os subplots)
    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(size=9, color=TXT),
        tickmode="array",
        tickvals=[1980, 2000, 2021],
        linecolor=GRID,
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=GRID,
        tickfont=dict(size=9, color=TXT),
        tickformat=".0f",
    )
    # Títulos dos subplots
    for ann in fig.layout.annotations:
        ann.font.size = 12
        ann.font.color = TXT_P

    fig.update_layout(
        paper_bgcolor=PANEL, plot_bgcolor=PANEL, font_color=TXT,
        margin=dict(l=10, r=10, t=50, b=10), height=440,
        font=dict(family="Inter, -apple-system, sans-serif"),
    )
    return fig


# ─────────────────────────────────────────────────────────────
# RANKING DELTA — quem melhorou vs. piorou (2003→2021)
# ─────────────────────────────────────────────────────────────
def ranking_delta(df_delta) -> go.Figure:
    """Barras horizontais: queda (âmbar) vs. alta (fogo) de 2003 a 2021.
    Só os 12 extremos (6 maiores quedas + 6 maiores altas)."""
    import pandas as pd
    d = pd.concat([df_delta.head(6), df_delta.tail(6)]).drop_duplicates()
    # Ordenar para visual mais limpo (quedas em cima, altas embaixo)
    d = d.sort_values("delta_mt")
    cores = ["#D94F1E" if v > 0 else "#E07C20" for v in d["delta_mt"]]

    fig = go.Figure(go.Bar(
        x=d["delta_mt"],
        y=d["nome"],
        orientation="h",
        marker_color=cores,
        marker_line_width=0,
        text=[f"{v:+.0f} Mt" for v in d["delta_mt"]],
        textposition="outside",
        textfont=dict(size=10, color=TXT),
        hovertemplate="<b>%{y}</b><br>%{x:+.0f} Mt CO₂e<extra></extra>",
    ))
    fig.add_vline(x=0, line_color="#6B4E35", line_width=1.5, line_dash="dot")
    fig.update_layout(
        xaxis=dict(
            title="Mt CO₂e (negativo = caiu, positivo = subiu)",
            color=TXT, gridcolor=GRID,
            zeroline=False,
        ),
        yaxis=dict(title="", color=TXT),
        font=dict(family="Inter, -apple-system, sans-serif"),
    )
    return _dark(fig, h=400)
