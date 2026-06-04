"""
Por que o Brasil Emite Diferente do Mundo?
Dashboard interativo das emissões de GEE do Brasil (1970–2021) — SEEG / Observatório do Clima.

Rodar:  streamlit run app.py
"""

import streamlit as st

from src import dados as d
from src import graficos as g

# ─────────────────────────────────────────────────────────────
# CONFIG + TEMA
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Por que o Brasil emite diferente",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  /* ── Fonte ─────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }

  /* ── Backgrounds — paleta FOGO ─────────────────────────── */
  .main, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0F0A06 !important;
  }
  section[data-testid="stSidebar"] { background-color: #1A1109 !important; }
  .block-container { padding-top: 0; padding-bottom: 2rem; max-width: 1300px; }

  /* ── Cor de texto global ────────────────────────────────── */
  p, span, div, li { color: #B8967A; }

  /* ── Tabs: underline âmbar ──────────────────────────────── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #2E1E10;
    margin-bottom: 24px;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-bottom: 2px solid transparent;
    border-radius: 0;
    padding: 10px 20px;
    color: #6B4E35;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.02em;
  }
  .stTabs [aria-selected="true"] {
    background: transparent !important;
    border-bottom: 2px solid #E07C20 !important;
    color: #F0D8B8 !important;
  }

  /* ── Metric: sem background, sem delta pills coloridas ──── */
  div[data-testid="stMetric"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    border-right: 1px solid #2E1E10;
  }
  div[data-testid="stMetric"]:last-child { border-right: none !important; }
  div[data-testid="stMetricValue"] {
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #F0D8B8 !important;
    letter-spacing: -0.02em !important;
  }
  div[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: #6B4E35 !important;
  }
  /* Remover o pill colorido do delta — substituir por texto simples */
  div[data-testid="stMetricDelta"] > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
  }
  div[data-testid="stMetricDelta"] {
    font-size: 12px !important;
    color: #8B6748 !important;
  }
  /* Setas do delta */
  div[data-testid="stMetricDelta"] svg { display: none !important; }

  /* ── Slider ─────────────────────────────────────────────── */
  .stSlider label { font-size: 11px !important; text-transform: uppercase;
                    letter-spacing: 0.08em; color: #6B4E35 !important; }

  /* ── Toggle ─────────────────────────────────────────────── */
  .stToggle label { font-size: 12px !important; color: #8B6748 !important; }

  /* ── Caption ────────────────────────────────────────────── */
  .stCaption, [data-testid="stCaptionContainer"] {
    color: #6B4E35 !important; font-size: 12px !important;
  }

  /* ── Divider ────────────────────────────────────────────── */
  hr { border-color: #2E1E10 !important; margin: 32px 0 !important; }

  /* ── Info box ───────────────────────────────────────────── */
  .stAlert { background: #1A1109 !important; border: 1px solid #2E1E10 !important;
             color: #B8967A !important; border-radius: 6px !important; }

  /* ── Scrollbar ──────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: #0F0A06; }
  ::-webkit-scrollbar-thumb { background: #3A2015; border-radius: 3px; }

  /* ── Info box ───────────────────────────────────────────── */
  .stAlert { background: #111113 !important; border: 1px solid #27272A !important;
             color: #A1A1AA !important; border-radius: 6px !important; }

  /* ── Divider ────────────────────────────────────────────── */
  hr { border-color: #27272A !important; margin: 32px 0 !important; }

  /* ── Scrollbar ──────────────────────────────────────────── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #09090B; }
  ::-webkit-scrollbar-thumb { background: #27272A; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# HELPERS DE TIPOGRAFIA
# ─────────────────────────────────────────────────────────────
def story(html: str):
    """Texto narrativo — fluido, pergaminho âmbar."""
    st.markdown(
        f'<p style="font-size:15px; line-height:1.75; color:#B8967A; '
        f'margin:0 0 20px 0; max-width:780px;">{html}</p>',
        unsafe_allow_html=True,
    )


def insight(html: str):
    """Conclusão analítica — linha âmbar, texto mais claro."""
    st.markdown(
        f'<div style="border-left:2px solid #6B3A14; padding-left:16px; '
        f'margin:20px 0 24px 0; font-size:14px; line-height:1.7; color:#C8A07A;">'
        f'{html}</div>',
        unsafe_allow_html=True,
    )


def label(txt: str):
    """Label uppercase âmbar escuro."""
    st.markdown(
        f'<p style="font-size:11px; font-weight:500; text-transform:uppercase; '
        f'letter-spacing:0.1em; color:#6B4E35; margin:0 0 8px 0;">{txt}</p>',
        unsafe_allow_html=True,
    )


def section_title(txt: str, sub: str = ""):
    """Título de seção com subtítulo."""
    st.markdown(
        f'<h2 style="font-size:22px; font-weight:600; color:#F0D8B8; '
        f'margin:0 0 4px 0; letter-spacing:-0.01em;">{txt}</h2>'
        + (f'<p style="font-size:13px; color:#6B4E35; margin:0 0 20px 0;">{sub}</p>' if sub else '<div style="margin-bottom:20px;"></div>'),
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# CARGA
# ─────────────────────────────────────────────────────────────
df     = d.carregar_seeg()
geojson = d.carregar_geojson()
df_int  = d.carregar_internacional()
k       = d.kpis_nacionais(df)

if "uf_sel" not in st.session_state:
    st.session_state.uf_sel = None

# ─────────────────────────────────────────────────────────────
# HEADER EDITORIAL
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:48px 0 32px 0; border-bottom:1px solid #2E1E10; margin-bottom:32px;">
  <p style="font-size:11px; font-weight:500; text-transform:uppercase;
            letter-spacing:0.12em; color:#6B4E35; margin:0 0 16px 0;">
    SEEG &nbsp;·&nbsp; Observatório do Clima &nbsp;·&nbsp; 1970–2021
  </p>
  <h1 style="font-size:44px; font-weight:700; color:#F0D8B8; margin:0 0 12px 0;
             line-height:1.08; letter-spacing:-0.025em;">
    Por que o Brasil Emite<br>
    <span style="color:#E07C20;">Diferente do Mundo</span>
  </h1>
  <p style="font-size:16px; color:#8B6748; margin:0; max-width:580px; line-height:1.65;">
    Análise de 52 anos de gases de efeito estufa. No Brasil, o problema
    não está nas chaminés — está na floresta derrubada.
  </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# KPIs — tipografia pura, sem containers
# ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Emissão em 2021",
          f"{k['mt_2021']:.0f} Mt",
          f"{k['delta_pct']:+.0f}% vs pico")
c2.metric("Pico histórico",
          f"{k['mt_pico']:.0f} Mt",
          f"ano {k['ano_pico']}")
c3.metric("Desmatamento + Agro",
          f"{k['pct_top2']:.0f}%",
          "do total histórico")
c4.metric("Maior setor",
          d.SETOR_CURTO.get(k['maior_setor'], k['maior_setor']),
          f"{k['pct_maior']:.0f}% do total")

st.markdown("<div style='margin:32px 0;'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs([
    "Mapa",
    "Histórico",
    "A Queda de 2003",
    "Composição",
    "Brasil vs. Mundo",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — MAPA CLICÁVEL + DRILL-DOWN
# ══════════════════════════════════════════════════════════════
with t1:
    story(
        "Diferente de países industrializados — onde as emissões se concentram em polos urbanos "
        "e industriais — no Brasil elas seguem a <b>fronteira agrícola</b> e o arco do "
        "desmatamento na Amazônia. Clique em qualquer estado para destrinchar a composição setorial."
    )

    # ── Controles ──────────────────────────────────────────────
    col_s, col_acum, col_pc = st.columns([3, 1, 1])
    acumulado  = col_acum.toggle("Acumulado 1970–2021", value=False, key="acum_mapa")
    ano        = col_s.slider("Ano", 1970, 2021, 2021, key="ano_mapa", disabled=acumulado)
    per_capita = col_pc.toggle("Per capita", value=False, key="pc_mapa")

    # ── Dados ──────────────────────────────────────────────────
    if acumulado:
        df_estado = d.mapa_acumulado(df, per_capita)
        ano_label = "1970–2021 (acumulado)"
    else:
        df_estado = d.mapa_por_estado(df, ano, per_capita)
        ano_label = str(ano)

    unidade       = df_estado["unidade"].iloc[0]
    _total_brasil = df[df.ano == ano]["valor_mt"].sum() if not acumulado else df["valor_mt"].sum()

    col_mapa, col_drill = st.columns([3, 2])

    with col_mapa:
        fig_mapa = g.mapa_brasil(df_estado, geojson, unidade)
        evento   = st.plotly_chart(
            fig_mapa, use_container_width=True,
            on_select="rerun", key="mapa_click",
            selection_mode="points",
        )
        pts = (evento.get("selection", {}) or {}).get("points", []) if evento else []
        if pts:
            loc = pts[0].get("location") or (pts[0].get("customdata") or [None])[0]
            if loc:
                st.session_state.uf_sel = loc
        st.caption(f"Selecione um estado · {ano_label} · {unidade}")

    with col_drill:
        uf = st.session_state.uf_sel
        if uf:
            _ano_drill = ano if not acumulado else 2021
            info     = d.drill_estado(df, uf, _ano_drill)
            nome_uf  = d.SIGLA_NOME.get(uf, uf)
            pct_pais = (info["total_ano"] / _total_brasil * 100) if _total_brasil > 0 else 0
            top_sub  = info["subsetores"].iloc[0] if len(info["subsetores"]) > 0 else None

            # Nome do estado
            st.markdown(
                f'<h2 style="font-size:22px; font-weight:600; color:#F0D8B8; '
                f'margin:0 0 4px 0;">{nome_uf}</h2>'
                f'<p style="font-size:13px; color:#6B4E35; margin:0 0 16px 0;">'
                f'{uf} &nbsp;·&nbsp; {pct_pais:.1f}% das emissões do Brasil em {_ano_drill}</p>',
                unsafe_allow_html=True,
            )

            st.plotly_chart(g.mapa_estado_zoom(geojson, uf), use_container_width=True,
                            config={"displayModeBar": False})

            # Maior fonte (sem caixa colorida)
            if top_sub is not None:
                st.markdown(
                    f'<p style="font-size:13px; color:#6B4E35; margin:8px 0 16px 0;">'
                    f'Maior fonte: <span style="color:#C8A07A; font-weight:500;">'
                    f'{top_sub["nivel2"]}</span> &nbsp;({top_sub["valor_mt"]:.0f} Mt)</p>',
                    unsafe_allow_html=True,
                )

            # KPIs do estado
            cc1, cc2 = st.columns(2)
            cc1.metric(f"Emissão {_ano_drill}", f"{info['total_ano']:.1f} Mt")
            cc2.metric("Per capita", f"{info['per_capita_ano']:.1f} t/hab")

            # Composição
            st.markdown(
                f'<p style="font-size:11px; font-weight:500; text-transform:uppercase; '
                f'letter-spacing:0.08em; color:#6B4E35; margin:16px 0 6px 0;">'
                f'Composição por setor — {_ano_drill}</p>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                g.drill_composicao(info["composicao"], info["total_ano"], _ano_drill),
                use_container_width=True, config={"displayModeBar": False},
            )
        else:
            st.markdown(
                '<div style="padding:40px 0; text-align:center;">'
                '<p style="font-size:13px; color:#52525B;">Clique em um estado no mapa</p>'
                '<p style="font-size:12px; color:#3F3F46; margin-top:8px;">'
                'Zoom na região · composição setorial · emissão e per capita</p>'
                '</div>',
                unsafe_allow_html=True,
            )

    # Evolução histórica
    if st.session_state.uf_sel:
        uf = st.session_state.uf_sel
        st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
        label("Evolução histórica — 1970–2021")
        st.markdown(
            f'<h3 style="font-size:18px; font-weight:600; color:#E0E0E0; margin:0 0 16px 0;">'
            f'{d.SIGLA_NOME.get(uf, uf)}</h3>',
            unsafe_allow_html=True,
        )
        _ano_drill = ano if not acumulado else 2021
        st.plotly_chart(
            g.drill_serie(d.drill_estado(df, uf, _ano_drill)["serie"]),
            use_container_width=True,
        )

# ══════════════════════════════════════════════════════════════
# TAB 2 — HEATMAP estados × anos
# ══════════════════════════════════════════════════════════════
with t2:
    section_title("27 estados, 52 anos",
                  "Cada célula é uma combinação de estado × ano. Vermelho intenso = emissão alta.")
    story(
        "Note a faixa quente em <b>PA, MT e RO</b> no início dos anos 2000 — o auge do "
        "desmatamento amazônico — e como ela <b>esfria após 2005</b>, quando a fiscalização "
        "ambiental se intensificou com o PPCDAm."
    )
    st.plotly_chart(g.heatmap_estados_anos(d.heatmap_estados(df)), use_container_width=True)
    insight(
        "O padrão visual conta a história: o problema do Brasil é geograficamente concentrado "
        "(Amazônia Legal) e temporalmente responsivo a políticas públicas — a maior evidência "
        "de que controlar o desmatamento é a alavanca mais eficaz para reduzir emissões."
    )

    # ── Small Multiples ─────────────────────────────────────────
    st.divider()
    section_title(
        "Trajetória dos 6 maiores emissores",
        "Cada mini-gráfico mostra 52 anos de emissão total do estado. O ponto vermelho marca o pico histórico.",
    )
    story(
        "O heatmap mostra a <b>intensidade relativa</b> de todos os estados. Aqui, os 6 maiores "
        "emissores ganham seu próprio gráfico para revelar a trajetória individual: "
        "<b>Pará e Mato Grosso</b> tiveram quedas dramáticas após 2003; <b>São Paulo e Minas</b> "
        "crescem gradualmente por conta da energia e da pecuária intensiva."
    )
    _top = d.top_estados_serie(df, n=6)
    st.plotly_chart(
        g.small_multiples_estados(_top["series"], d.SIGLA_NOME),
        use_container_width=True,
    )

    # ── Ranking Delta ────────────────────────────────────────────
    st.divider()
    section_title(
        "Quem melhorou e quem piorou",
        "Variação de emissão entre o pico histórico (2003) e 2021.",
    )
    story(
        "Queda em âmbar, alta em vermelho. Os estados que mais caíram são justamente os que mais "
        "desmataram — <b>Pará e Mato Grosso</b> lideram a redução em termos absolutos. "
        "Quem subiu são estados com pecuária crescente ou industrialização acelerada."
    )
    _delta = d.delta_estados(df, 2003, 2021)
    st.plotly_chart(g.ranking_delta(_delta), use_container_width=True)
    insight(
        "A queda dos maiores emissores não foi espontânea — foi resultado direto das políticas "
        "de comando e controle iniciadas em 2004 (PPCDAm). Estados que não tinham "
        "pressão de desmatamento (SP, MG, RS) continuaram subindo continuamente."
    )

# ══════════════════════════════════════════════════════════════
# TAB 3 — A QUEDA DE 2003 (decomposição)
# ══════════════════════════════════════════════════════════════
with t3:
    section_title("A queda de 45% entre 2003 e 2010",
                  "Uma das maiores reduções de emissão já registradas por um país.")

    # ── Contexto: o que estava acontecendo em 2003 ───────────────
    story(
        "Em 2003, o Brasil registrou <b>3.005 Mt CO₂e</b> — o maior valor de sua história. "
        "Não foi coincidência: a fronteira agrícola avançava sobre a Amazônia em ritmo acelerado, "
        "impulsionada pelo boom das commodities internacionais. O arco do desmatamento — "
        "faixa que vai do Pará ao Mato Grosso — desmatava em média <b>27.000 km² por ano</b>, "
        "equivalente a perder o estado de Alagoas inteiro a cada 12 meses. "
        "O governo federal não tinha mecanismos eficazes de monitoramento em tempo real."
    )
    story(
        "Em 2004, o governo lançou o <b>PPCDAm</b> (Plano de Ação para Prevenção e Controle do "
        "Desmatamento na Amazônia) — a primeira política sistemática e coordenada contra o desmatamento. "
        "A estratégia tinha três pilares: ordenamento territorial (criação de áreas protegidas), "
        "monitoramento (sistema DETER com imagens de satélite a cada 15 dias) e controle e fiscalização "
        "(IBAMA com autoridade reforçada). Os gráficos abaixo mostram o impacto direto dessa mudança."
    )

    cesq, cdir = st.columns([1, 1])
    with cesq:
        st.plotly_chart(g.decomposicao_queda(df, 2003, 2010), use_container_width=True)
    with cdir:
        st.plotly_chart(g.serie_normalizada(d.serie_setor_nacional(df)), use_container_width=True)
        st.caption("Participação relativa (%) de cada setor — 1970–2021")

    # ── As 5 intervenções que explicam a queda ───────────────────
    label("As 5 intervenções que explicam a queda")
    story(
        "<b>1. PPCDAm (2004):</b> Coordenou ações entre 13 ministérios. "
        "Tornou o desmatamento punível com multas, embargo de crédito rural e bloqueio de licenças — "
        "desmatar virou risco financeiro real para fazendeiros e bancos."
    )
    story(
        "<b>2. DETER — Detecção em Tempo Real (2004):</b> Sistema do INPE que produzia alertas de "
        "desmatamento a cada 15 dias via satélite. Pela primeira vez, o IBAMA sabia <i>onde</i> "
        "agir antes que a floresta sumisse. Entre 2004 e 2012, os embargos do IBAMA aumentaram 10×."
    )
    story(
        "<b>3. Moratória da Soja (2006):</b> Gigantes do agronegócio (Cargill, ADM, Bunge) se "
        "comprometeram a não comprar soja plantada em áreas desmatadas após julho de 2006. "
        "Desmatar virou risco de mercado: produtores sem certificação perdiam acesso às exportações."
    )
    story(
        "<b>4. Acordo da Carne (2009):</b> Os 4 maiores frigoríficos do Brasil (JBS, Marfrig, "
        "Minerva, Bertin) se comprometeram a não comprar gado de áreas desmatadas. Resultado direto "
        "de campanha do Greenpeace que expôs a cadeia pecuária como financiadora do desmatamento."
    )
    story(
        "<b>5. Criação de áreas protegidas:</b> Entre 2003 e 2010, o Brasil criou mais de "
        "<b>60 milhões de hectares</b> de novas unidades de conservação e terras indígenas na Amazônia "
        "— equivalente a quase o dobro do território do Mato Grosso. Áreas demarcadas têm taxas de "
        "desmatamento 10× menores do que áreas sem proteção formal."
    )

    insight(
        "O conjunto dessas cinco intervenções explica por que o desmatamento caiu 80% entre 2004 e 2012. "
        "Nenhuma isolada teria funcionado — foi a <b>combinação de monitoramento satelital, "
        "fiscalização com dentes e pressão de mercado</b> que criou o efeito. "
        "É o maior case do mundo de redução de emissões sem desaceleração econômica."
    )

    # ── Trajetória completa ──────────────────────────────────────
    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    label("Trajetória completa — 1970 a 2021")
    st.plotly_chart(g.serie_empilhada(d.serie_setor_nacional(df)), use_container_width=True)

    # ── Por que subiu depois de 2010? ────────────────────────────
    st.divider()
    section_title("Por que as emissões voltaram a subir depois de 2010?",
                  "A trajetória acima mostra uma queda seguida de nova alta — o que aconteceu?")
    story(
        "Após o mínimo histórico de 2010 (<b>1.637 Mt</b>), as emissões voltaram a crescer. "
        "Três fatores explicam a reversão:"
    )
    story(
        "<b>Código Florestal de 2012:</b> A reforma do Código Florestal anistiou desmatadores com "
        "passivos ambientais anteriores a 2008 (via Programa de Regularização Ambiental) e reduziu "
        "as Áreas de Preservação Permanente em pequenas propriedades. Enviou o sinal errado ao mercado: "
        "desmatar e esperar anistia podia ser uma estratégia viável."
    )
    story(
        "<b>Enfraquecimento institucional (2013–2018):</b> O orçamento do IBAMA foi progressivamente "
        "cortado, reduzindo operações de fiscalização. O número de autuações de desmatamento ilegal "
        "caiu pela metade entre 2012 e 2018, apesar de os alertas do DETER mostrarem recuperação do desmatamento."
    )
    story(
        "<b>Retrocesso político (2019–2022):</b> O período foi marcado por pressão institucional "
        "direta contra órgãos de controle ambiental, substituição de lideranças técnicas do IBAMA "
        "e do ICMBio, e discurso político que tratou a fiscalização como obstáculo ao desenvolvimento. "
        "O desmatamento na Amazônia atingiu em 2021 o maior nível desde 2006."
    )
    insight(
        "Desmatamento é uma <b>escolha política, não uma consequência inevitável do desenvolvimento</b>. "
        "Em 7 anos (2003–2010), o Brasil reduziu suas emissões em 45% — a maior queda absoluta "
        "já registrada por qualquer país no mundo. Sem crescer menos. Sem desindustrializar. "
        "Apenas com fiscalização, acordos setoriais e monitoramento satelital. "
        "A mesma alavanca que funcionou de 2004 a 2010 poderia funcionar de novo — "
        "se as condições políticas permitissem."
    )

# ══════════════════════════════════════════════════════════════
# TAB 4 — COMPOSIÇÃO (treemap) + RANKING + scatter
# ══════════════════════════════════════════════════════════════
with t4:
    section_title("Hierarquia das emissões",
                  "Setor → subsetor → estado. O tamanho de cada retângulo é proporcional à emissão.")
    story(
        "As fontes de emissão do Brasil são incomuns para uma grande economia. Em vez de chaminés "
        "de usinas e escapamentos de carros — as principais fontes de EUA, China e Europa — "
        "no Brasil as maiores fontes são a <b>digestão de bovinos</b> e o <b>corte de árvores</b>. "
        "Isso explica por que descarbonizar o Brasil requer políticas completamente diferentes "
        "das que funcionaram na Europa: aqui não adianta só trocar carro a gasolina por elétrico."
    )
    story(
        "Dentro de <b>Agropecuária</b>, a maior fonte é a <b>Fermentação Entérica</b> — "
        "literalmente a digestão do rebanho bovino (arroto + flatulência), que libera metano "
        "(CH₄, 28× mais potente que CO₂ em 100 anos). "
        "Dentro de <b>Mudança de Uso da Terra</b>, são as <b>Alterações de Uso</b> que dominam "
        "— cada hectare de floresta derrubado libera o carbono armazenado nas árvores de uma vez."
    )
    ano_tree = st.slider("Ano", 1970, 2021, 2021, key="ano_tree",
                         label_visibility="collapsed")
    label(f"Treemap — {ano_tree}")
    st.plotly_chart(g.treemap(d.treemap_data(df, ano_tree), ano_tree), use_container_width=True)

    st.divider()
    section_title("Ranking de estados",
                  "O maior emissor depende de como medimos — absoluto ou per capita.")
    story(
        "Em valor absoluto, <b>PA e MT</b> lideram por serem os estados do arco do desmatamento. "
        "Per capita, <b>RR, RO e AC</b> disparam — estados pouco populosos onde "
        "cada habitante 'carrega' uma emissão enorme. Isso é central no debate de justiça climática."
    )
    cr1, cr2 = st.columns(2)
    df_abs = d.mapa_por_estado(df, 2021, per_capita=False)
    df_pc  = d.mapa_por_estado(df, 2021, per_capita=True)
    with cr1:
        label("Absoluto — Mt CO₂e (2021)")
        st.plotly_chart(g.ranking_estados(df_abs, "Mt CO₂e"), use_container_width=True)
    with cr2:
        label("Per capita — t CO₂e/hab (2021)")
        st.plotly_chart(g.ranking_estados(df_pc, "t CO₂e/hab"), use_container_width=True)

    label("Dispersão: absoluto × per capita")
    st.plotly_chart(g.scatter_abs_percapita(df_abs, df_pc, d.POP_2022),
                    use_container_width=True)
    insight(
        "Estados no canto superior esquerdo (baixo absoluto, alto per capita) são os "
        "amazônicos pouco povoados — emitem muito por pessoa mesmo com população pequena. "
        "A distinção absoluto vs. per capita é central nas negociações climáticas: o Brasil "
        "argumenta que estados como PA e MT têm alta responsabilidade histórica e baixa população "
        "— colocando a questão de quem deve pagar pelo custo da proteção florestal."
    )

# ══════════════════════════════════════════════════════════════
# TAB 5 — BRASIL vs MUNDO
# ══════════════════════════════════════════════════════════════
with t5:
    section_title("O Brasil emite diferente",
                  "Dois gráficos. Dois mundos. A mesma pergunta respondida de formas opostas.")

    # ── Setup: o argumento brasileiro nas negociações ────────────
    story(
        "Quando delegações brasileiras vão a negociações climáticas internacionais, "
        "elas carregam um argumento poderoso: em <b>CO₂ de combustíveis fósseis</b> per capita, "
        "o Brasil é um dos menores emissores do mundo. Um brasileiro emite ~2,3 t de CO₂ fóssil "
        "por ano — a mesma quantidade que um norte-americano produz em <b>menos de 7 semanas</b>."
    )
    st.plotly_chart(g.brasil_vs_mundo(), use_container_width=True)

    # ── Tensão: a limitação da métrica ───────────────────────────
    st.divider()
    section_title("Mas esse gráfico está incompleto",
                  "CO₂ fóssil é a métrica certa para países industrializados — não para o Brasil.")
    story(
        "CO₂ de combustíveis fósseis é a fonte dominante de emissões nos países industrializados "
        "— por isso tornou-se a métrica padrão dos acordos climáticos. "
        "Para o Brasil, ela simplesmente <b>não conta o que mais importa</b>: "
        "o desmatamento libera CO₂ estocado em árvores (não fóssil), "
        "e o gado emite metano (CH₄) — nenhum dos dois aparece no gráfico acima."
    )
    story(
        "Quando incluímos todas as emissões de gases de efeito estufa "
        "(CO₂ de qualquer fonte, metano, óxido nitroso), "
        "convertidos para CO₂ equivalente pelo mesmo padrão que o SEEG usa — "
        "o quadro muda completamente."
    )

    # ── Plot twist: total GEE per capita ─────────────────────────
    _brasil_pc = d.brasil_gee_per_capita_2021(df)
    st.plotly_chart(g.brasil_total_vs_mundo(_brasil_pc), use_container_width=True)
    st.caption(
        "Fontes: EDGAR v8 (2022) para demais países — total GHG per capita incluindo uso da terra. "
        f"Brasil calculado do SEEG 2022: {_brasil_pc:.1f} t CO₂e/pessoa."
    )

    # ── Resolução: a conclusão analítica ─────────────────────────
    insight(
        f"Com todas as emissões incluídas, o Brasil emite <b>~{_brasil_pc:.0f} t CO₂e por pessoa</b> "
        f"— acima da China (9,5 t), acima da média da União Europeia (7,5 t), "
        f"e mais de 50% acima da média mundial (6,8 t). "
        "O argumento de que o Brasil tem 'baixa pegada climática' só vale "
        "se você ignorar deliberadamente o desmatamento. "
        "E é exatamente por isso que este projeto existe: "
        "<b>o Brasil emite diferente, mas não emite pouco</b>. "
        "A solução não é eletrificar a frota — é parar de derrubar a floresta."
    )

# ─────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="font-size:12px; color:#3F3F46;">'
    'Fonte: SEEG 10 — Observatório do Clima (2022) &nbsp;·&nbsp; '
    'CO₂ fóssil: Global Carbon Project &nbsp;·&nbsp; '
    'Desenvolvido por Lucas Garrido'
    '</p>',
    unsafe_allow_html=True,
)
