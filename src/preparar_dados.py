"""
preparar_dados.py — ETL do dataset SEEG (Excel → Parquet tidy)

Lê a aba 'GEE Estados' do Excel oficial do SEEG (~80 MB), filtra para
emissões em CO2e GWP-AR6, transforma de formato wide (um ano por coluna)
para tidy (uma linha por estado/setor/ano), e salva um parquet leve (~2 MB).

Uso:
    python src/preparar_dados.py

O app.py carrega o parquet resultante instantaneamente. Rodar este script
uma única vez evita os ~36s de leitura do Excel a cada inicialização do app.
"""

from pathlib import Path
import sys
import pandas as pd

# Caminhos
AQUI = Path(__file__).parent.parent  # pasta do projeto
EXCEL = AQUI.parent.parent.parent / "dados" / "-SEEG10_GERAL-BR_UF_2022.10.27-FINAL-SITE.xlsx"
SAIDA = AQUI / "data" / "seeg_tidy.parquet"


def preparar() -> pd.DataFrame:
    if not EXCEL.exists():
        sys.exit(
            f"❌ Excel do SEEG não encontrado em:\n   {EXCEL}\n\n"
            "Baixe em https://plataforma.seeg.eco.br/ e coloque na pasta dados/."
        )

    print(f"⏳ Lendo aba 'GEE Estados' de {EXCEL.name} (~80 MB, pode levar ~40s)…")
    df = pd.read_excel(EXCEL, sheet_name="GEE Estados", engine="openpyxl")
    print(f"   Shape bruto: {df.shape}")

    df = df.rename(columns={
        "Nível 1 - Setor": "setor",
        "Nível 2": "nivel2",
        "Emissão / Remoção / Bunker": "tipo",
        "Gás": "gas",
        "Estado": "estado",
    })

    # Filtro: CO2e padrão IPCC AR6, apenas Emissão bruta, estados válidos
    df = df[
        (df["gas"] == "CO2e (t) GWP-AR6") &
        (df["tipo"] == "Emissão") &
        (df["estado"] != "NA") &
        (df["estado"].notna())
    ].copy()
    print(f"   Após filtro CO2e GWP-AR6 + Emissão: {df.shape}")

    # Wide → tidy
    anos = [c for c in df.columns if isinstance(c, int) and 1970 <= c <= 2021]
    tidy = df.melt(
        id_vars=["setor", "nivel2", "estado"],
        value_vars=anos,
        var_name="ano",
        value_name="valor_t",
    )
    tidy["ano"] = tidy["ano"].astype(int)
    tidy["valor_mt"] = tidy["valor_t"] / 1_000_000  # toneladas → Mt CO2e
    tidy["setor"] = tidy["setor"].str.strip()  # corrige "Resíduos " com espaço final
    tidy = tidy.dropna(subset=["valor_mt"]).drop(columns=["valor_t"])

    SAIDA.parent.mkdir(exist_ok=True)
    tidy.to_parquet(SAIDA, index=False)
    print(f"✅ Salvo: {SAIDA} ({SAIDA.stat().st_size/1024:.0f} KB, {tidy.shape[0]:,} linhas)")
    return tidy


if __name__ == "__main__":
    df = preparar()
    print("\n📊 Resumo:")
    print(f"   Setores: {sorted(df['setor'].unique())}")
    print(f"   Estados: {df['estado'].nunique()}  |  Anos: {df['ano'].min()}–{df['ano'].max()}")
    print(f"   Total acumulado: {df['valor_mt'].sum():,.0f} Mt CO2e")
