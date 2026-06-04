# Data Card — SEEG 10 (Emissões de GEE)

## Identificação

| Campo | Valor |
|-------|-------|
| **Nome** | SEEG 10 — Sistema de Estimativas de Emissões e Remoções de Gases de Efeito Estufa |
| **Mantenedor** | Observatório do Clima |
| **Versão** | 10 (lançamento 2022) |
| **Link** | https://seeg.eco.br/ · https://plataforma.seeg.eco.br/ |
| **Licença** | Creative Commons BY-SA (uso livre com atribuição) |
| **Arquivo** | `-SEEG10_GERAL-BR_UF_2022.10.27-FINAL-SITE.xlsx` (~80 MB) |
| **Período** | 1970–2021 (52 anos) |

## Estrutura

O Excel tem 13 abas. Este projeto usa a aba **`GEE Estados`** (~103.000 linhas, 63 colunas).

### Esquema da aba GEE Estados (formato wide)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `Nível 1 - Setor` | texto | Setor principal (5 valores) |
| `Nível 2` … `Nível 6` | texto | Hierarquia de subsetores |
| `Emissão / Remoção / Bunker` | categórico | Tipo: Emissão, Remoção, Bunker, NCI |
| `Gás` | categórico | 23 gases (CO₂, CH₄, N₂O, CO₂e em vários padrões) |
| `Estado` | categórico | Sigla da UF (27 + `NA`) |
| `Atividade Econômica` | texto | Setor econômico associado |
| `Produto` | texto | Produto específico |
| `1970` … `2021` | numérico | Emissão em toneladas, uma coluna por ano |

### Valores categóricos relevantes

- **Setores (Nível 1):** Agropecuária, Energia, Mudança de Uso da Terra e Floresta, Processos Industriais, Resíduos
- **Tipos:** Emissão, Emissão NCI, Remoção, Remoção NCI, Bunker
- **Gases CO₂e:** GWP/GTP nas versões AR2, AR4, AR5, AR6

## Tratamento aplicado neste projeto

1. **Filtro de gás:** apenas `CO2e (t) GWP-AR6` — converte todos os gases para uma métrica comparável usando os fatores de aquecimento global do IPCC AR6 (CH₄ ≈ 28×, N₂O ≈ 273×)
2. **Filtro de tipo:** apenas `Emissão` (exclui Remoção/Bunker para análise de emissão bruta)
3. **Filtro de estado:** exclui `NA` (emissões nacionais não atribuíveis a UF)
4. **Reshape:** wide → tidy via `pd.melt` (52 colunas de ano → coluna única `ano` + `valor`)
5. **Conversão de unidade:** toneladas → Mt CO₂e (÷ 1.000.000)
6. **Limpeza:** `.str.strip()` no setor (corrige "Resíduos " com espaço final)

**Resultado:** 417.664 linhas tidy, colunas `[setor, nivel2, estado, ano, valor_mt]`, salvo em `data/seeg_tidy.parquet` (~2,3 MB).

## Qualidade e limitações

- ⚠️ Metodologia pode mudar entre versões do SEEG — não comparar diretamente com outras edições
- ⚠️ Análise de emissão **bruta**, não líquida (não desconta remoção florestal)
- ⚠️ O `NA` em estado representa emissões reais (nacionais), apenas não atribuíveis a UF — foram excluídas da análise estadual mas não são erro
- ✅ Sem dados faltantes nas colunas de ano após o filtro
- ✅ Cobertura completa: 27 UFs × 5 setores × 52 anos

## Dados auxiliares

- **População por estado (IBGE 2022):** embutida no código para análise per capita. Fonte original: `dados/POP2022_Municipios.xls`
- **GeoJSON das UFs:** `brasil_uf.geojson` — geometria dos 27 estados, chave `properties.sigla`
