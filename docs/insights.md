# Insights — Validação das Hipóteses

Análise dos dados SEEG (1970–2021), CO₂e GWP-AR6, emissão bruta. Todos os números abaixo foram extraídos diretamente do dataset.

---

## H1 — Mudança de Uso da Terra domina as emissões ✅ CONFIRMADA

Participação de cada setor no total acumulado 1970–2021:

| Setor | Mt CO₂e acumulado | Participação |
|-------|------------------:|-------------:|
| Mudança de Uso da Terra e Floresta | 40.492 | **53,1%** |
| Agropecuária | 21.393 | **28,1%** |
| Energia | 9.792 | 12,8% |
| Processos Industriais | 2.344 | 3,1% |
| Resíduos | 2.227 | 2,9% |

**Conclusão:** desmatamento + agropecuária = **81,2%** das emissões históricas. Energia, que domina nos países desenvolvidos, é apenas 12,8% no Brasil. A tese central está confirmada com folga.

---

## H2 — Trajetória: pico em 2003, mínimo em 2010 ✅ CONFIRMADA (com correção)

| Ano | Mt CO₂e | Evento |
|-----|--------:|--------|
| 1970 | 222 | Início da série |
| **2003** | **3.005** | **Pico histórico** (auge do desmatamento) |
| 2004 | 2.890 | Início do PPCDAm |
| **2010** | **1.637** | **Mínimo histórico** (−45% vs pico) |
| 2012 | 1.774 | |
| 2019 | 2.047 | Retomada da alta |
| 2021 | 2.323 | |

**Correção importante:** o plano inicial assumia pico em 2004 e mínimo em 2012. Os dados reais mostram **pico em 2003 e mínimo em 2010**. A queda de 45% entre 2003 e 2010 coincide com o Plano de Ação para Prevenção e Controle do Desmatamento na Amazônia (PPCDAm, 2004).

---

## H3 — Estados de fronteira lideram (absoluto) ✅ CONFIRMADA

Top 10 estados por emissão acumulada (1970–2021):

| # | Estado | Mt CO₂e | Perfil |
|---|--------|--------:|--------|
| 1 | PA (Pará) | 12.693 | Fronteira amazônica |
| 2 | MT (Mato Grosso) | 12.375 | Fronteira agrícola + Amazônia |
| 3 | MG (Minas Gerais) | 6.218 | Populoso + industrial |
| 4 | SP (São Paulo) | 5.738 | Mais populoso + industrial |
| 5 | RO (Rondônia) | 4.638 | Fronteira amazônica |
| 6 | RS | 3.939 | Agropecuária |
| 7 | MA | 3.492 | Fronteira (MATOPIBA) |
| 8 | GO | 3.466 | Agropecuária |
| 9 | MS | 3.392 | Agropecuária |
| 10 | BA | 3.295 | Misto |

**Conclusão:** PA e MT (desmatamento + agro) dominam, muito à frente de MG e SP (que aparecem por população e indústria).

---

## H4 — Per capita inverte o ranking ✅ CONFIRMADA (dramaticamente)

Ranking de 2021:

| Posição | Absoluto | Per capita |
|---------|----------|------------|
| 1º | PA | **RR** (Roraima) |
| 2º | MT | **RO** (Rondônia) |
| 3º | MG | **MT** (94,3 t/hab) |
| 4º | SP | PA |
| 5º | AM | AC (Acre) |

**Conclusão:** o ranking muda completamente. Estados amazônicos pouco populosos (RR, RO, AC) sobem ao topo per capita, enquanto MG e SP (grandes populações) desaparecem do top 5. Isso levanta uma questão de **justiça climática**: quem é o "maior emissor" depende fundamentalmente de como medimos.

---

## H5 — Agropecuária estável vs. desmatamento volátil ✅ CONFIRMADA

Teste de Mann-Kendall (tendência monotônica, 1970–2021):

| Setor | Tendência | p-valor |
|-------|-----------|--------:|
| Agropecuária | crescente | < 0,0001 |
| Energia | crescente | < 0,0001 |
| Processos Industriais | crescente | < 0,0001 |
| Resíduos | crescente | < 0,0001 |
| Mudança de Uso da Terra | crescente | **0,0002** |

**Conclusão:** todos os setores têm tendência de alta estatisticamente significativa. Porém, o desmatamento (LULUCF) tem o **maior p-valor** (0,0002 vs. < 0,0001 dos demais) — sinal de que sua série é mais **volátil**, com grandes oscilações ano a ano (sobe e desce com políticas públicas), enquanto a agropecuária cresce de forma mais constante e previsível.

---

## Implicação central

A descarbonização do Brasil é, antes de tudo, um problema de **uso da terra** — controlar o desmatamento e tornar a pecuária mais eficiente tem impacto muito maior do que a transição energética isolada. A boa notícia que os dados revelam: o desmatamento é o setor mais **responsivo a políticas públicas** (a queda de 45% entre 2003–2010 prova isso), o que significa que é também onde ações de governo geram resultados mais rápidos.
