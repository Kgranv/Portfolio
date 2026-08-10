import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def get_data(filepath = "./data/clean_data.parquet") -> pd.DataFrame:
    return pd.read_parquet(filepath)

def exclude_total_export(df) -> pd.DataFrame:
    return df[df["cmdCode"]!="TOTAL"]


def format_qty(df) -> pd.DataFrame:
    df["qty"] = df.apply(
        lambda r: (
            f"{r['qty']:,.0f}".replace(",", " ") + f" {r['qtyUnit']}"
            if pd.notnull(r["qty"]) and r["qty"] > 0
            else "Not available"
        ),
        axis=1,
    )

    return df

def format_value(df) -> pd.DataFrame:
    df["primaryValue_str"] = df["primaryValue"].apply(
        lambda v: f"{v:,.0f}".replace(",", " ") + " $" if pd.notnull(v) else "N/A"
    )

    return df

def data_for_treemap(df) -> pd.DataFrame:
    value_world = df["primaryValue"].sum()

    df_sorted = df.dropna(subset=["primaryValue"]).sort_values(
        by="primaryValue", ascending=False
    )

    top20 = df_sorted.head(20).copy()

    value_top20 = top20["primaryValue"].sum()
    value_other = value_world - value_top20

    test_dict = dict(zip(top20["reporterCode"], top20["reporterCodeIsoAlpha3"]))
    print(f"reporterCode_Dict = {repr(test_dict)}")

    treemap_df = pd.concat(
        [
            top20[["reporterCodeIsoAlpha3", "countryName", "primaryValue"]],
            pd.DataFrame(
                [{"reporterCodeIsoAlpha3": "Other", "countryName": "Other", "primaryValue": value_other}]
            ),
        ],
        ignore_index=True,
    )
    return treemap_df

# 1. Vos fonctions d'affichage
def plot_map(df, fig, visible=True):
    fig.add_trace(
        go.Choropleth(
            locations=df["reporterCodeIsoAlpha3"],
            z=df["RSCA"],
            colorscale="Haline",
            colorbar_title="RSCA",
            colorbar_x=-0.13,
            customdata=df[["text", "qty", "primaryValue_str", "RSCA"]],
            hovertemplate="<b>%{hovertext}</b><br><br>"
            + "Product : %{customdata[0]}<br>"
            + "Quantity : %{customdata[1]}<br>"
            + "Value (USD) : %{customdata[2]}<br>"
            + "RSCA : %{customdata[3]:.2f}<extra></extra>",
            hovertext=df["countryName"],
            visible=visible,
        ),
        row=1,
        col=1,
    )


def plot_treemap(df, fig, visible=True):
    fig.add_trace(
        go.Treemap(
            labels=df["countryName"],
            parents=[""] * len(df),
            values=df["primaryValue"],
            customdata=df[["primaryValue_str"]],
            texttemplate="<b>%{label}</b><br>%{percentEntry:.1%}",
            hovertemplate="<b>%{label}</b><br>"
            + "Total exportation : %{customdata[0]}<br>"
            + "Global share : %{percentEntry:.2%}<extra></extra>",
            visible=visible,
        ),
        row=1,
        col=2,
    )


# 2. Vos fichiers et chargements
filepaths = [
    "./data/clean/COMTRADE_OILS_2022.parquet",
    "./data/clean/COMTRADE_COPPER_2022.parquet",
    "./data/clean/COMTRADE_LITHIUM_2022.parquet",
    "./data/clean/COMTRADE_WOOD_2022.parquet",
    "./data/clean/COMTRADE_COCOA_2022.parquet",
    "./data/clean/COMTRADE_WHEAT_2022.parquet",
]

# Noms personnalisés pour les boutons (ex: extraits du fichier ou manuels)
labels_boutons = ["Oils"," Copper", "Lithium", "Wood", "Cocoa", "WHEAT"]  # Ajoutez un libellé par fichier dans filepaths

chloro_df_list = []
treemap_df_list = []

for path in filepaths:
    data = get_data(path)
    data = exclude_total_export(data)

    chloro_df = data.copy()
    treemap_df = data.copy()

    chloro_df = format_value(chloro_df)
    chloro_df = format_qty(chloro_df)

    treemap_df = data_for_treemap(treemap_df)
    treemap_df = format_value(treemap_df)

    chloro_df_list.append(chloro_df)
    treemap_df_list.append(treemap_df)

# 3. Structure Subplots (ATTENTION : {"type": "treemap"} au lieu de "pie")
fig = make_subplots(
    rows=1,
    cols=2,
    column_widths=[0.7, 0.3],
    specs=[[{"type": "choropleth"}, {"type": "treemap"}]],
    subplot_titles=(
        "Indice RSCA par pays",
        "Part dans les exportations mondiales (USD)",
    ),
)

# 4. Ajout alterné des traces (Carte i, Treemap i)
# De cette façon :
# Jeu 0 -> Traces 0 et 1
# Jeu 1 -> Traces 2 et 3
# Jeu 2 -> Traces 4 et 5, etc.
num_datasets = len(chloro_df_list)

for i in range(num_datasets):
    is_visible = i == 0  # Seul le premier jeu est visible par défaut (True)
    plot_map(chloro_df_list[i], fig, visible=is_visible)
    plot_treemap(treemap_df_list[i], fig, visible=is_visible)

# 5. Construction DYNAMIQUE du masque de visibilité pour les boutons
buttons = []
for i in range(num_datasets):
    # Génère une liste de False de taille (2 * num_datasets)
    visibility_mask = [False] * (2 * num_datasets)

    # Active uniquement la paire (Carte + Treemap) du jeu i
    visibility_mask[2 * i] = True
    visibility_mask[2 * i + 1] = True

    # Nom du bouton
    label = labels_boutons[i] if i < len(labels_boutons) else f"Jeu {i+1}"

    buttons.append(
        dict(
            label=label,
            method="update",
            args=[
                {"visible": visibility_mask},
                {"title": f"Analyse - {label}"},
            ],
        )
    )

# 6. Configuration du Layout avec les boutons
fig.update_layout(
    margin={"r": 20, "t": 80, "l": 20, "b": 20},
    geo=dict(showframe=False, showcoastlines=True),
    updatemenus=[
        dict(
            type="buttons",  # Vous pouvez mettre "dropdown" pour un menu déroulant
            direction="right",
            x=0.0,
            y=1.15,
            showactive=True,
            buttons=buttons,
        )
    ],
)

# 7. Afficher la figure
fig.show()