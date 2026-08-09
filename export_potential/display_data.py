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

def data_for_piechart(df) -> pd.DataFrame:
    value_world = df["primaryValue"].sum()

    df_sorted = df.dropna(subset=["primaryValue"]).sort_values(
        by="primaryValue", ascending=False
    )

    top10 = df_sorted.head(20).copy()

    # Calculer la somme du reste du monde
    value_top10 = top10["primaryValue"].sum()
    value_other = value_world - value_top10

    # Créer un DataFrame complet pour le Pie Chart
    pie_df = pd.concat(
        [
            top10[["reporterCodeIsoAlpha3", "countryName", "primaryValue"]],
            pd.DataFrame(
                [{"reporterCodeIsoAlpha3": "Other", "countryName": "Other", "primaryValue": value_other}]
            ),
        ],
        ignore_index=True,
    )
    return pie_df


data = get_data()
data = exclude_total_export(data)

choloro_df = data.copy()
pie_df = data.copy()

choloro_df = format_value(choloro_df)
choloro_df = format_qty(choloro_df)

pie_df = data_for_piechart(pie_df)
pie_df = format_value(pie_df)

fig = make_subplots(
    rows=1,
    cols=2,
    column_widths=[0.6, 0.4],
    specs=[[{"type": "choropleth"}, {"type": "pie"}]],
    subplot_titles=(
        "Indice RSCA par pays",
        "Part dans les exportations mondiales (USD)",
    ),
)

# 4. Carte Choroplèthe (Gauche)
fig.add_trace(
    go.Choropleth(
        locations=choloro_df["reporterCodeIsoAlpha3"],
        z=choloro_df["RSCA"],
        colorscale="Haline",
        colorbar_title="RSCA",
        colorbar_x=0.53,
        customdata=choloro_df[["text", "qty", "primaryValue_str", "RSCA"]],
        hovertemplate="<b>%{hovertext}</b><br><br>"
        + "Product : %{customdata[0]}<br>"
        + "Quantity : %{customdata[1]}<br>"
        + "Value (USD) : %{customdata[2]}<br>"
        + "RSCA : %{customdata[3]:.2f}<extra></extra>",
        hovertext=choloro_df["countryName"],
    ),
    row=1,
    col=1,
)

# 5. Pie / Donut Chart exact (Droite)
fig.add_trace(
    go.Treemap(
        labels=pie_df["countryName"],
        parents=[""] * len(pie_df),
        values=pie_df["primaryValue"],
        customdata=pie_df[["primaryValue_str"]],
        texttemplate="<b>%{label}</b><br>%{percentEntry:.1%}",
        hovertemplate="<b>%{label}</b><br>"
        + "Total exportation : %{customdata[0]}<br>"
        + "Global share : %{percentEntry:.2%}<extra></extra>",
    ),
    row=1,
    col=2,
)

# 6. Configuration de la mise en page
fig.update_layout(
    margin={"r": 20, "t": 80, "l": 20, "b": 20},
    geo=dict(showframe=False, showcoastlines=True),
)

fig.show()
