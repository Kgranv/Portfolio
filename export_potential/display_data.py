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

def plot_map(df, fig):
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
        ),
        row=1,
        col=1,
    )

def plot_treemap(df, fig):
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
        ),
        row=1,
        col=2,
    )



data = get_data()
data = exclude_total_export(data)

choloro_df = data.copy()
treemap_df = data.copy()

choloro_df = format_value(choloro_df)
choloro_df = format_qty(choloro_df)

treemap_df = data_for_treemap(treemap_df)
treemap_df = format_value(treemap_df)

fig = make_subplots(
    rows=1,
    cols=2,
    column_widths=[0.7, 0.3],
    specs=[[{"type": "choropleth"}, {"type": "pie"}]],
    subplot_titles=(
        "Indice RSCA par pays",
        "Part dans les exportations mondiales (USD)",
    ),
)

plot_map(choloro_df,fig)
plot_treemap(treemap_df,fig)

# 6. Configuration de la mise en page
fig.update_layout(
    margin={"r": 20, "t": 80, "l": 20, "b": 20},
    geo=dict(showframe=False, showcoastlines=True),
)

fig.show()
