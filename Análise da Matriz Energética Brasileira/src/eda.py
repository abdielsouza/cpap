from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import polars as pl


# =============================================================================
# PATHS
# =============================================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs"

FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
TABLES_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# INPUT FILES
# =============================================================================

GENERATION_FILE = (
    DATA_DIR / "geracao_nacional_2011_2025.csv"
)

STATE_GENERATION_FILE = (
    DATA_DIR / "geracao_estadual_2011_2025.csv"
)

CAPACITY_FILE = (
    DATA_DIR / "capacidade_instalada_1974_2025.csv"
)


# =============================================================================
# GENERAL HELPERS
# =============================================================================

def print_section(title: str) -> None:
    print()
    print("=" * 80)
    print(title)
    print("=" * 80)


def save_csv(
    df: pl.DataFrame,
    filename: str,
) -> None:

    path = TABLES_DIR / filename

    df.write_csv(path)

    print(f"Saved: {path}")


def save_figure(filename: str) -> None:

    path = FIGURES_DIR / filename

    plt.tight_layout()

    plt.savefig(
        path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Saved: {path}")


# =============================================================================
# LOAD DATA
# =============================================================================

def load_data() -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
]:

    generation = pl.read_csv(
        GENERATION_FILE
    )

    state_generation = pl.read_csv(
        STATE_GENERATION_FILE
    )

    capacity = pl.read_csv(
        CAPACITY_FILE
    )

    return (
        generation,
        state_generation,
        capacity,
    )


# =============================================================================
# STRUCTURAL ANALYSIS
# =============================================================================

def dataset_summary(
    name: str,
    df: pl.DataFrame,
) -> None:

    print_section(name)

    print(
        f"Rows:       {df.height:,}"
    )

    print(
        f"Columns:    {df.width}"
    )

    print(
        f"Estimated memory: "
        f"{df.estimated_size() / 1024**2:.2f} MB"
    )

    print("\nSchema:")

    for column, dtype in df.schema.items():
        print(
            f"  {column}: {dtype}"
        )

    print("\nMissing values:")

    nulls = df.null_count()

    has_nulls = False

    for column in df.columns:

        value = nulls[column][0]

        if value > 0:

            has_nulls = True

            print(
                f"  {column}: {value:,}"
            )

    if not has_nulls:
        print("  None")

    print("\nDuplicated rows:")

    duplicated = (
        df.is_duplicated()
        .sum()
    )

    print(
        f"  {duplicated:,}"
    )


def structural_analysis(
    generation: pl.DataFrame,
    state_generation: pl.DataFrame,
    capacity: pl.DataFrame,
) -> None:

    dataset_summary(
        "NATIONAL GENERATION",
        generation,
    )

    dataset_summary(
        "STATE GENERATION",
        state_generation,
    )

    dataset_summary(
        "INSTALLED CAPACITY",
        capacity,
    )


# =============================================================================
# TEMPORAL ANALYSIS
# =============================================================================

def temporal_analysis(
    generation: pl.DataFrame,
    state_generation: pl.DataFrame,
    capacity: pl.DataFrame,
) -> None:

    print_section(
        "TEMPORAL COVERAGE"
    )

    datasets = {
        "National generation": generation,
        "State generation": state_generation,
        "Installed capacity": capacity,
    }

    for name, df in datasets.items():

        minimum = df["ano"].min()
        maximum = df["ano"].max()

        print(
            f"{name}: "
            f"{minimum} → {maximum}"
        )


# =============================================================================
# NATIONAL GENERATION
# =============================================================================

def analyze_generation(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "NATIONAL GENERATION"
    )

    print("\nSources:")

    sources = (
        generation
        .select("fonte")
        .unique()
        .sort("fonte")
    )

    for source in sources["fonte"].to_list():

        print(
            f"  - {source}"
        )

    statistics = (
        generation
        .group_by("fonte")
        .agg(
            pl.col("geracao_gwh")
            .count()
            .alias("count"),

            pl.col("geracao_gwh")
            .min()
            .alias("min"),

            pl.col("geracao_gwh")
            .mean()
            .alias("mean"),

            pl.col("geracao_gwh")
            .median()
            .alias("median"),

            pl.col("geracao_gwh")
            .max()
            .alias("max"),

            pl.col("geracao_gwh")
            .std()
            .alias("std"),
        )
        .sort("fonte")
        .with_columns(
            pl.col("min").round(2),
            pl.col("mean").round(2),
            pl.col("median").round(2),
            pl.col("max").round(2),
            pl.col("std").round(2),
        )
    )

    print("\nDescriptive statistics:")

    print(statistics)

    save_csv(
        statistics,
        "generation_descriptive_statistics.csv",
    )

    first_year = generation["ano"].min()
    last_year = generation["ano"].max()

    print(
        f"\nGeneration in {first_year}:"
    )

    print(
        generation
        .filter(
            pl.col("ano") == first_year
        )
        .select(
            "fonte",
            "geracao_gwh",
        )
        .sort(
            "geracao_gwh",
            descending=True,
        )
    )

    print(
        f"\nGeneration in {last_year}:"
    )

    print(
        generation
        .filter(
            pl.col("ano") == last_year
        )
        .select(
            "fonte",
            "geracao_gwh",
        )
        .sort(
            "geracao_gwh",
            descending=True,
        )
    )


# =============================================================================
# GENERATION GROWTH
# =============================================================================

def analyze_generation_growth(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "GENERATION GROWTH"
    )

    """
    Growth is calculated independently for each source.

    We deliberately avoid comparing every source with 2011 because:

    - Solar starts at zero / effectively absent.
    - Thermal generation does not have a valid positive baseline in 2011.

    Therefore each source uses:

        first year with generation > 0
        last year with generation > 0
    """

    positive = (
        generation
        .filter(
            pl.col("geracao_gwh") > 0
        )
        .sort(
            ["fonte", "ano"]
        )
    )

    first = (
        positive
        .group_by("fonte")
        .agg(
            pl.col("ano")
            .first()
            .alias("primeiro_ano"),

            pl.col("geracao_gwh")
            .first()
            .alias("geracao_inicial_gwh"),
        )
    )

    last = (
        positive
        .group_by("fonte")
        .agg(
            pl.col("ano")
            .last()
            .alias("ultimo_ano"),

            pl.col("geracao_gwh")
            .last()
            .alias("geracao_final_gwh"),
        )
    )

    growth = (
        first
        .join(
            last,
            on="fonte",
        )
        .with_columns(

            (
                pl.col("geracao_final_gwh")
                -
                pl.col("geracao_inicial_gwh")
            )
            .alias(
                "crescimento_absoluto_gwh"
            ),

            (
                pl.col("ultimo_ano")
                -
                pl.col("primeiro_ano")
            )
            .alias(
                "anos"
            ),
        )
        .with_columns(

            pl.when(
                pl.col(
                    "geracao_inicial_gwh"
                ) > 0
            )
            .then(
                (
                    (
                        pl.col(
                            "geracao_final_gwh"
                        )
                        /
                        pl.col(
                            "geracao_inicial_gwh"
                        )
                    )
                    - 1
                )
                * 100
            )
            .otherwise(None)
            .alias(
                "crescimento_percentual"
            ),

            pl.when(
                (
                    pl.col("anos") > 0
                )
                &
                (
                    pl.col(
                        "geracao_inicial_gwh"
                    ) > 0
                )
            )
            .then(
                (
                    (
                        (
                            pl.col(
                                "geracao_final_gwh"
                            )
                            /
                            pl.col(
                                "geracao_inicial_gwh"
                            )
                        )
                        **
                        (
                            1
                            /
                            pl.col("anos")
                        )
                    )
                    - 1
                )
                * 100
            )
            .otherwise(None)
            .alias(
                "cagr_percentual"
            ),
        )
        .sort(
            "crescimento_percentual",
            descending=True,
        )
        .with_columns(
            pl.col(
                "geracao_inicial_gwh"
            ).round(2),

            pl.col(
                "geracao_final_gwh"
            ).round(2),

            pl.col(
                "crescimento_absoluto_gwh"
            ).round(2),

            pl.col(
                "crescimento_percentual"
            ).round(2),

            pl.col(
                "cagr_percentual"
            ).round(2),
        )
    )

    print(
        growth
    )

    save_csv(
        growth,
        "generation_growth.csv",
    )


# =============================================================================
# ANNUAL VARIATION
# =============================================================================

def analyze_annual_variation(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "ANNUAL GENERATION VARIATION"
    )

    result = (
        generation
        .sort(
            ["fonte", "ano"]
        )
        .with_columns(

            (
                pl.col("geracao_gwh")
                .pct_change()
                .over("fonte")
                * 100
            )
            .alias(
                "variacao_anual_pct"
            )
        )
        .with_columns(
            pl.col(
                "variacao_anual_pct"
            ).round(2)
        )
    )

    print(
        result
        .select(
            [
                "ano",
                "fonte",
                "geracao_gwh",
                "variacao_anual_pct",
            ]
        )
        .tail(20)
    )

    save_csv(
        result,
        "generation_annual_variation.csv",
    )


# =============================================================================
# INSTALLED CAPACITY
# =============================================================================

def analyze_capacity(
    capacity: pl.DataFrame,
) -> None:

    print_section(
        "INSTALLED CAPACITY"
    )

    print("\nSources:")

    sources = (
        capacity
        .select("fonte")
        .unique()
        .sort("fonte")
    )

    for source in sources["fonte"].to_list():

        print(
            f"  - {source}"
        )

    statistics = (
        capacity
        .group_by("fonte")
        .agg(
            pl.col("capacidade_mw")
            .count()
            .alias("count"),

            pl.col("capacidade_mw")
            .min()
            .alias("min"),

            pl.col("capacidade_mw")
            .mean()
            .alias("mean"),

            pl.col("capacidade_mw")
            .median()
            .alias("median"),

            pl.col("capacidade_mw")
            .max()
            .alias("max"),

            pl.col("capacidade_mw")
            .std()
            .alias("std"),
        )
        .sort("fonte")
        .with_columns(
            pl.col("min").round(2),
            pl.col("mean").round(2),
            pl.col("median").round(2),
            pl.col("max").round(2),
            pl.col("std").round(2),
        )
    )

    print(
        statistics
    )

    save_csv(
        statistics,
        "capacity_descriptive_statistics.csv",
    )


# =============================================================================
# GENERATION × CAPACITY
# =============================================================================

def analyze_generation_vs_capacity(
    generation: pl.DataFrame,
    capacity: pl.DataFrame,
) -> pl.DataFrame:

    print_section(
        "GENERATION × INSTALLED CAPACITY"
    )

    merged = (
        generation
        .join(
            capacity.select(
                [
                    "ano",
                    "fonte",
                    "capacidade_mw",
                ]
            ),
            on=[
                "ano",
                "fonte",
            ],
            how="left",
        )
        .with_columns(

            pl.when(
                pl.col(
                    "capacidade_mw"
                ) > 0
            )
            .then(
                pl.col("geracao_gwh")
                /
                pl.col("capacidade_mw")
            )
            .otherwise(None)
            .alias(
                "geracao_por_mw"
            ),
        )
        .with_columns(
            pl.col(
                "geracao_por_mw"
            ).round(4)
        )
    )

    print(
        merged.head(15)
    )

    save_csv(
        merged,
        "generation_capacity_merged.csv",
    )

    return merged


# =============================================================================
# RENEWABLES
# =============================================================================

def analyze_renewables(
    generation: pl.DataFrame,
) -> pl.DataFrame:

    print_section(
        "RENEWABLE GENERATION"
    )

    renewable = (
        generation
        .filter(
            pl.col("renovavel")
        )
        .group_by("ano")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "renewable_generation_gwh"
            )
        )
    )

    total = (
        generation
        .group_by("ano")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "total_generation_gwh"
            )
        )
    )

    result = (
        renewable
        .join(
            total,
            on="ano",
        )
        .with_columns(

            (
                pl.col(
                    "renewable_generation_gwh"
                )
                /
                pl.col(
                    "total_generation_gwh"
                )
                * 100
            )
            .alias(
                "renewable_share_pct"
            ),
        )
        .sort("ano")
        .with_columns(
            pl.col(
                "renewable_generation_gwh"
            ).round(2),

            pl.col(
                "total_generation_gwh"
            ).round(2),

            pl.col(
                "renewable_share_pct"
            ).round(2),
        )
    )

    print(
        result
    )

    save_csv(
        result,
        "renewable_generation.csv",
    )

    return result


# =============================================================================
# SOURCE SHARES
# =============================================================================

def analyze_source_shares(
    generation: pl.DataFrame,
) -> pl.DataFrame:

    print_section(
        "SOURCE GENERATION SHARE"
    )

    total = (
        generation
        .group_by("ano")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "total_generation_gwh"
            )
        )
    )

    result = (
        generation
        .join(
            total,
            on="ano",
        )
        .with_columns(

            (
                pl.col("geracao_gwh")
                /
                pl.col(
                    "total_generation_gwh"
                )
                * 100
            )
            .alias(
                "participacao_pct"
            ),
        )
        .sort(
            [
                "ano",
                "geracao_gwh",
            ],
            descending=[
                False,
                True,
            ],
        )
        .with_columns(
            pl.col(
                "geracao_gwh"
            ).round(2),

            pl.col(
                "total_generation_gwh"
            ).round(2),

            pl.col(
                "participacao_pct"
            ).round(2),
        )
    )

    save_csv(
        result,
        "source_generation_share.csv",
    )

    return result


# =============================================================================
# HYDRAULIC DEPENDENCY
# =============================================================================

def analyze_hydraulic_dependency(
    generation: pl.DataFrame,
) -> pl.DataFrame:

    print_section(
        "HYDRAULIC DEPENDENCY"
    )

    total = (
        generation
        .group_by("ano")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "total_generation_gwh"
            )
        )
    )

    hydraulic = (
        generation
        .filter(
            pl.col("fonte")
            == "Hidráulica"
        )
        .select(
            [
                "ano",

                pl.col(
                    "geracao_gwh"
                ).alias(
                    "hydraulic_generation_gwh"
                ),
            ]
        )
    )

    result = (
        hydraulic
        .join(
            total,
            on="ano",
        )
        .with_columns(

            (
                pl.col(
                    "hydraulic_generation_gwh"
                )
                /
                pl.col(
                    "total_generation_gwh"
                )
                * 100
            )
            .alias(
                "hydraulic_share_pct"
            ),
        )
        .sort("ano")
        .with_columns(
            pl.col(
                "hydraulic_generation_gwh"
            ).round(2),

            pl.col(
                "total_generation_gwh"
            ).round(2),

            pl.col(
                "hydraulic_share_pct"
            ).round(2),
        )
    )

    print(
        result
    )

    save_csv(
        result,
        "hydraulic_dependency.csv",
    )

    return result


# =============================================================================
# WIND + SOLAR
# =============================================================================

def analyze_wind_solar(
    generation: pl.DataFrame,
) -> pl.DataFrame:

    print_section(
        "WIND + SOLAR"
    )

    combined = (
        generation
        .filter(
            pl.col("fonte").is_in(
                [
                    "Eólica",
                    "Solar fotovoltaica",
                ]
            )
        )
        .group_by("ano")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "wind_solar_generation_gwh"
            )
        )
    )

    total = (
        generation
        .group_by("ano")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "total_generation_gwh"
            )
        )
    )

    result = (
        combined
        .join(
            total,
            on="ano",
        )
        .with_columns(

            (
                pl.col(
                    "wind_solar_generation_gwh"
                )
                /
                pl.col(
                    "total_generation_gwh"
                )
                * 100
            )
            .alias(
                "wind_solar_share_pct"
            ),
        )
        .sort("ano")
        .with_columns(
            pl.col(
                "wind_solar_generation_gwh"
            ).round(2),

            pl.col(
                "total_generation_gwh"
            ).round(2),

            pl.col(
                "wind_solar_share_pct"
            ).round(2),
        )
    )

    print(
        result
    )

    save_csv(
        result,
        "wind_solar_generation.csv",
    )

    return result


# =============================================================================
# STATE ANALYSIS
# =============================================================================

def analyze_states(
    state_generation: pl.DataFrame,
) -> None:

    print_section(
        "STATE GENERATION"
    )

    latest_year = (
        state_generation["ano"].max()
    )

    print(
        f"\nTop states in {latest_year}:"
    )

    ranking = (
        state_generation
        .filter(
            pl.col("ano")
            == latest_year
        )
        .filter(
            pl.col("fonte")
            != "Total"
        )
        .group_by("estado")
        .agg(
            pl.col("geracao_gwh")
            .sum()
            .alias(
                "geracao_gwh"
            )
        )
        .sort(
            "geracao_gwh",
            descending=True,
        )
        .with_columns(
            pl.col(
                "geracao_gwh"
            ).round(2)
        )
    )

    print(
        ranking.head(15)
    )

    save_csv(
        ranking,
        "state_generation_ranking_latest.csv",
    )


# =============================================================================
# INFLECTION POINTS
# =============================================================================

def analyze_inflection_points(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "INFLECTION POINTS"
    )

    annual = (
        generation
        .sort(
            [
                "fonte",
                "ano",
            ]
        )
        .with_columns(

            (
                pl.col(
                    "geracao_gwh"
                )
                .pct_change()
                .over("fonte")
                * 100
            )
            .alias(
                "variation_pct"
            )
        )
    )

    increases = (
        annual
        .filter(
            pl.col(
                "variation_pct"
            ).is_not_null()
        )
        .sort(
            "variation_pct",
            descending=True,
        )
        .group_by("fonte")
        .head(3)
        .sort(
            [
                "fonte",
                "variation_pct",
            ],
            descending=[
                False,
                True,
            ],
        )
        .with_columns(
            pl.col(
                "variation_pct"
            ).round(2)
        )
    )

    decreases = (
        annual
        .filter(
            pl.col(
                "variation_pct"
            ).is_not_null()
        )
        .sort(
            "variation_pct"
        )
        .group_by("fonte")
        .head(3)
        .sort(
            [
                "fonte",
                "variation_pct",
            ],
            descending=[
                False,
                False,
            ],
        )
        .with_columns(
            pl.col(
                "variation_pct"
            ).round(2)
        )
    )

    print(
        "\nStrongest annual increases:"
    )

    print(
        increases
    )

    print(
        "\nStrongest annual decreases:"
    )

    print(
        decreases
    )

    save_csv(
        increases,
        "strongest_annual_increases.csv",
    )

    save_csv(
        decreases,
        "strongest_annual_decreases.csv",
    )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_generation(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "DATA VALIDATION"
    )

    expected_sources = {
        "Hidráulica",
        "Eólica",
        "Solar fotovoltaica",
        "Nuclear",
        "Térmica",
    }

    actual_sources = set(
        generation["fonte"]
        .unique()
        .to_list()
    )

    print(
        "Expected sources:"
    )

    print(
        expected_sources
    )

    print(
        "\nActual sources:"
    )

    print(
        actual_sources
    )

    unexpected = (
        actual_sources
        -
        expected_sources
    )

    if unexpected:

        print(
            "\nWARNING: unexpected sources:"
        )

        print(
            unexpected
        )

    else:

        print(
            "\nSource validation: OK"
        )

    duplicate_keys = (
        generation
        .group_by(
            [
                "ano",
                "fonte",
            ]
        )
        .agg(
            pl.len().alias("n")
        )
        .filter(
            pl.col("n") > 1
        )
    )

    if duplicate_keys.height:

        print(
            "\nWARNING: duplicate "
            "year/source combinations:"
        )

        print(
            duplicate_keys
        )

    else:

        print(
            "Year/source uniqueness: OK"
        )

    negative = (
        generation
        .filter(
            pl.col(
                "geracao_gwh"
            ) < 0
        )
    )

    if negative.height:

        print(
            "\nWARNING: negative "
            "generation values:"
        )

        print(
            negative
        )

    else:

        print(
            "Negative generation values: OK"
        )


# =============================================================================
# PLOT: GENERATION BY SOURCE
# =============================================================================

def plot_generation_by_source(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "PLOT — GENERATION BY SOURCE"
    )

    sources = (
        generation
        .select("fonte")
        .unique()
        .sort("fonte")
        ["fonte"]
        .to_list()
    )

    years = (
        generation
        .select("ano")
        .unique()
        .sort("ano")
        ["ano"]
        .to_list()
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    for source in sources:

        values = []

        for year in years:

            row = (
                generation
                .filter(
                    (
                        pl.col("ano")
                        == year
                    )
                    &
                    (
                        pl.col("fonte")
                        == source
                    )
                )
                .select("geracao_gwh")
            )

            if row.height:

                values.append(
                    row.item()
                )

            else:

                values.append(
                    0.0
                )

        ax.plot(
            years,
            values,
            label=source,
        )

    ax.set_title(
        "Geração de eletricidade no Brasil por fonte"
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Geração (GWh)"
    )

    ax.grid(
        alpha=0.25
    )

    ax.legend()

    save_figure(
        "generation_by_source.png"
    )


# =============================================================================
# PLOT: SOURCE SHARE
# =============================================================================

def plot_source_share(
    generation: pl.DataFrame,
) -> None:

    print_section(
        "PLOT — SOURCE SHARE"
    )

    shares = analyze_source_shares(
        generation
    )

    sources = (
        shares
        .select("fonte")
        .unique()
        .sort("fonte")
        ["fonte"]
        .to_list()
    )

    years = (
        shares
        .select("ano")
        .unique()
        .sort("ano")
        ["ano"]
        .to_list()
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    for source in sources:

        values = []

        for year in years:

            row = (
                shares
                .filter(
                    (
                        pl.col("ano")
                        == year
                    )
                    &
                    (
                        pl.col("fonte")
                        == source
                    )
                )
                .select(
                    "participacao_pct"
                )
            )

            if row.height:

                values.append(
                    row.item()
                )

            else:

                values.append(
                    0.0
                )

        ax.plot(
            years,
            values,
            label=source,
        )

    ax.set_title(
        "Participação das fontes na geração elétrica"
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Participação (%)"
    )

    ax.set_ylim(
        0,
        100
    )

    ax.grid(
        alpha=0.25
    )

    ax.legend()

    save_figure(
        "source_generation_share.png"
    )


# =============================================================================
# PLOT: RENEWABLE SHARE
# =============================================================================

def plot_renewable_share(
    renewable: pl.DataFrame,
) -> None:

    print_section(
        "PLOT — RENEWABLE SHARE"
    )

    years = (
        renewable["ano"]
        .to_list()
    )

    values = (
        renewable[
            "renewable_share_pct"
        ]
        .to_list()
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.plot(
        years,
        values,
    )

    ax.set_title(
        "Participação das fontes renováveis na geração elétrica"
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Participação (%)"
    )

    ax.set_ylim(
        0,
        100
    )

    ax.grid(
        alpha=0.25
    )

    save_figure(
        "renewable_share.png"
    )


# =============================================================================
# PLOT: HYDRAULIC DEPENDENCY
# =============================================================================

def plot_hydraulic_dependency(
    hydraulic: pl.DataFrame,
) -> None:

    print_section(
        "PLOT — HYDRAULIC DEPENDENCY"
    )

    years = (
        hydraulic["ano"]
        .to_list()
    )

    values = (
        hydraulic[
            "hydraulic_share_pct"
        ]
        .to_list()
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.plot(
        years,
        values,
    )

    ax.set_title(
        "Dependência da geração hidráulica"
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Participação hidráulica (%)"
    )

    ax.set_ylim(
        0,
        100
    )

    ax.grid(
        alpha=0.25
    )

    save_figure(
        "hydraulic_dependency.png"
    )


# =============================================================================
# PLOT: WIND + SOLAR
# =============================================================================

def plot_wind_solar(
    wind_solar: pl.DataFrame,
) -> None:

    print_section(
        "PLOT — WIND + SOLAR"
    )

    years = (
        wind_solar["ano"]
        .to_list()
    )

    values = (
        wind_solar[
            "wind_solar_share_pct"
        ]
        .to_list()
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    ax.plot(
        years,
        values,
    )

    ax.set_title(
        "Participação de eólica + solar na geração elétrica"
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Participação (%)"
    )

    ax.grid(
        alpha=0.25
    )

    save_figure(
        "wind_solar_share.png"
    )


# =============================================================================
# PLOT: INSTALLED CAPACITY
# =============================================================================

def plot_installed_capacity(
    capacity: pl.DataFrame,
) -> None:

    print_section(
        "PLOT — INSTALLED CAPACITY"
    )

    sources = (
        capacity
        .select("fonte")
        .unique()
        .sort("fonte")
        ["fonte"]
        .to_list()
    )

    years = (
        capacity
        .select("ano")
        .unique()
        .sort("ano")
        ["ano"]
        .to_list()
    )

    fig, ax = plt.subplots(
        figsize=(12, 6)
    )

    for source in sources:

        values = []

        for year in years:

            row = (
                capacity
                .filter(
                    (
                        pl.col("ano")
                        == year
                    )
                    &
                    (
                        pl.col("fonte")
                        == source
                    )
                )
                .select(
                    "capacidade_mw"
                )
            )

            if row.height:

                values.append(
                    row.item()
                )

            else:

                values.append(
                    0.0
                )

        ax.plot(
            years,
            values,
            label=source,
        )

    ax.set_title(
        "Capacidade instalada de geração elétrica"
    )

    ax.set_xlabel(
        "Ano"
    )

    ax.set_ylabel(
        "Capacidade (MW)"
    )

    ax.grid(
        alpha=0.25
    )

    ax.legend()

    save_figure(
        "installed_capacity.png"
    )


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print_section(
        "BRAZILIAN ELECTRICITY MATRIX"
    )

    print(
        "EXPLORATORY DATA ANALYSIS"
    )

    print(
        "\nLoading datasets..."
    )

    (
        generation,
        state_generation,
        capacity,
    ) = load_data()

    print(
        "Datasets loaded successfully."
    )

    # -------------------------------------------------------------------------
    # Structure
    # -------------------------------------------------------------------------

    structural_analysis(
        generation,
        state_generation,
        capacity,
    )

    temporal_analysis(
        generation,
        state_generation,
        capacity,
    )

    # -------------------------------------------------------------------------
    # Generation
    # -------------------------------------------------------------------------

    analyze_generation(
        generation
    )

    analyze_generation_growth(
        generation
    )

    analyze_annual_variation(
        generation
    )

    # -------------------------------------------------------------------------
    # Capacity
    # -------------------------------------------------------------------------

    analyze_capacity(
        capacity
    )

    analyze_generation_vs_capacity(
        generation,
        capacity,
    )

    # -------------------------------------------------------------------------
    # Composition
    # -------------------------------------------------------------------------

    renewable = analyze_renewables(
        generation
    )

    analyze_source_shares(
        generation
    )

    hydraulic = (
        analyze_hydraulic_dependency(
            generation
        )
    )

    wind_solar = (
        analyze_wind_solar(
            generation
        )
    )

    # -------------------------------------------------------------------------
    # Geography
    # -------------------------------------------------------------------------

    analyze_states(
        state_generation
    )

    # -------------------------------------------------------------------------
    # Temporal behavior
    # -------------------------------------------------------------------------

    analyze_inflection_points(
        generation
    )

    # -------------------------------------------------------------------------
    # Validation
    # -------------------------------------------------------------------------

    validate_generation(
        generation
    )

    # -------------------------------------------------------------------------
    # Figures
    # -------------------------------------------------------------------------

    plot_generation_by_source(
        generation
    )

    plot_source_share(
        generation
    )

    plot_renewable_share(
        renewable
    )

    plot_hydraulic_dependency(
        hydraulic
    )

    plot_wind_solar(
        wind_solar
    )

    plot_installed_capacity(
        capacity
    )

    # -------------------------------------------------------------------------
    # Finish
    # -------------------------------------------------------------------------

    print_section(
        "EDA COMPLETED"
    )

    print(
        f"\nTables:"
        f"  {TABLES_DIR}"
    )

    print(
        f"Figures:"
        f" {FIGURES_DIR}"
    )


if __name__ == "__main__":
    main()