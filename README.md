# 🌿 Por que o Brasil Emite Diferente do Mundo?

> Análise interativa de **52 anos de emissões de gases de efeito estufa** do Brasil (1970–2021), com dados oficiais do **SEEG / Observatório do Clima**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://brazil-beyond-fossil-fuelsgit-zmapnybwthcdk5qgxe6xmn.streamlit.app)

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red)
![Plotly](https://img.shields.io/badge/Plotly-choropleth-orange)
![Dados](https://img.shields.io/badge/SEEG-1970--2021-green)

<!-- TODO: inserir GIF do mapa animado aqui -->
<!-- ![Demo do dashboard](docs/demo.gif) -->

---

## A tese

Quando se fala em "descarbonizar", a imagem que vem à cabeça é fechar termelétricas e trocar carros a combustão por elétricos. Isso faz sentido para os **EUA, China e Europa — onde o setor de Energia domina as emissões**.

**O Brasil é diferente.** Analisando 52 anos de dados oficiais, os números mostram que:

> **53% das emissões históricas do Brasil vêm de Mudança de Uso da Terra (desmatamento) e 28% da Agropecuária.** Juntos, **81%**. Energia é apenas **13%**.

Isso muda completamente o que significa reduzir as emissões brasileiras — o problema não está principalmente nas fábricas e carros, mas na **floresta derrubada e no rebanho bovino**.

---

## Principais descobertas

| Descoberta | Dado |
|------------|------|
| 🌳 **Desmatamento domina** | Mudança de Uso da Terra = **53%** das emissões acumuladas (1970–2021) |
| 🐄 **Agropecuária é a 2ª maior** | **28%** do total — metano do gado + óxido nitroso de fertilizantes |
| ⚡ **Energia é minoria** | Apenas **13%** — o oposto do padrão de países desenvolvidos |
| 📉 **Pico em 2003** | **3.005 Mt CO₂e** — auge do desmatamento amazônico |
| 📈 **Mínimo em 2010** | **1.637 Mt** — efeito do PPCDAm (política de combate ao desmatamento), uma queda de 45% |
| 🗺️ **PA e MT lideram** | Estados de fronteira agrícola e amazônica concentram as emissões absolutas |
| 👥 **Per capita inverte tudo** | **RR, RO e MT** lideram per capita (MT chega a **94 t CO₂e/hab**) — estados pouco populosos com muito desmatamento |

> Todas as tendências setoriais são estatisticamente **crescentes** (teste de Mann-Kendall, p < 0.05), mas o desmatamento é o setor mais **volátil** — sobe e desce conforme políticas públicas, enquanto a agropecuária cresce de forma constante.

---

## O dashboard

Aplicação **Streamlit** com três visões interativas:

### 🗺️ Mapa Interativo (peça central)
Mapa coroplético do Brasil **animado de 1970 a 2021** — assista o desmatamento se espalhar pela Amazônia ao longo das décadas. Toggle entre emissão **absoluta** e **per capita**, e clique em qualquer estado para ver o detalhamento por setor.

### 📈 Série Histórica
Evolução das emissões por setor com anotações dos eventos-chave (pico de 2003, mínimo de 2010). Comparador lado a lado de quaisquer dois setores.

### 🏆 Ranking por Estado
Top 15 estados emissores, com slider de ano e alternância absoluto/per capita — revelando como o ranking muda drasticamente quando normalizado por população.

---

## Demo ao vivo

**[Acessar o dashboard](https://brazil-beyond-fossil-fuelsgit-zmapnybwthcdk5qgxe6xmn.streamlit.app)** — hospedado no Streamlit Community Cloud.

---

## Como executar localmente

```bash
# 1. Clonar e entrar na pasta
cd mudancas_climaticas

# 2. Instalar dependências
pip install -r requirements.txt

# 3. (Opcional) Preparar os dados a partir do Excel original
#    Só necessário se data/seeg_tidy.parquet não existir
python src/preparar_dados.py

# 4. Rodar o dashboard
streamlit run app.py
```

O app abre em `http://localhost:8501`.

> **Nota sobre os dados:** o dataset bruto do SEEG (~80 MB) não está versionado no repositório. O projeto inclui o **parquet processado** (`data/seeg_tidy.parquet`, ~2 MB) pronto para uso. Para reprocessar do zero, baixe o Excel oficial em [plataforma.seeg.eco.br](https://plataforma.seeg.eco.br/) e rode `python src/preparar_dados.py`.

---

## Dataset

- **Fonte:** [SEEG — Sistema de Estimativas de Emissões e Remoções de GEE](https://seeg.eco.br/) / Observatório do Clima
- **Versão:** SEEG 10 (2022)
- **Período:** 1970–2021 (52 anos)
- **Granularidade:** setor × subsetor × estado × ano
- **Métrica:** CO₂e em GWP-AR6 (padrão IPCC mais recente), emissão bruta
- **Cobertura:** 27 unidades federativas, 5 setores

**Decisões técnicas de tratamento:**
- Filtrado para o gás `CO₂e (t) GWP-AR6` — permite somar gases diferentes numa métrica única (CH₄ ≈ 28× CO₂, N₂O ≈ 273×)
- Separada apenas a `Emissão` bruta (exclui Remoção e Bunker para análise clara)
- Excluído o estado `NA` (emissões nacionais não atribuíveis a UF específica)
- Transformado de formato *wide* (52 colunas de ano) para *tidy* via `pd.melt`

---

## Stack técnica

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12 |
| Dados | Pandas, PyArrow (parquet) |
| Visualização | Plotly (choropleth animado, área empilhada) |
| Estatística | pymannkendall (teste de tendência não-paramétrico) |
| Interface | Streamlit |
| Mapa | GeoJSON das UFs do Brasil |

---

## Estrutura do projeto

```
mudancas_climaticas/
├── app.py                  # Dashboard Streamlit
├── requirements.txt
├── README.md
├── .gitignore
├── brasil_uf.geojson       # Geometria das UFs para o mapa
├── data/
│   └── seeg_tidy.parquet   # Dados processados (~2 MB)
├── src/
│   └── preparar_dados.py   # ETL: Excel → parquet tidy
└── docs/
    ├── data_card.md        # Documentação do dataset
    └── insights.md         # Análise completa das hipóteses
```

---

## Limitações

- A metodologia do SEEG pode mudar entre versões — comparações com outras edições exigem cautela
- **Correlação ≠ causalidade:** a queda de emissões pós-2004 coincide com o PPCDAm, mas outros fatores (preço de commodities, crise econômica) também influenciaram
- Dados de população per capita são de 2022 (IBGE) aplicados a todos os anos — a análise per capita histórica seria mais precisa com população por ano
- Análise de **emissão bruta**, não líquida (não desconta remoção por florestas em pé)

---

## Possíveis evoluções

- Incluir dados pós-2021 (o SEEG atualiza anualmente)
- Comparação internacional formal (Brasil vs. top emissores globais)
- Modelo de previsão de emissões por setor (ARIMA / Prophet)
- Decomposição de Kaya (população × PIB × intensidade)
- Cenário contrafactual: "e se o desmatamento zerasse?"

---

## Sobre

Projeto de portfólio de **Data Science** — análise exploratória, visualização geoespacial, séries temporais e storytelling com dados reais de relevância ambiental.

Desenvolvido por **Lucas Garrido**.
Dados: SEEG / Observatório do Clima (CC BY-SA).
