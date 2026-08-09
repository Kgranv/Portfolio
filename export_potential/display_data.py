import plotly.express as px
import pandas as pd

# 1. Charger les données d'exemple (Gapminder)
df = pd.read_parquet("./data/clean_data.parquet")

df = df[df["cmdCode"]!="TOTAL"]
print(df.head())

df['RSCA'] = (df['RCA'] - 1) / (df['RCA'] + 1)

# 2. Créer la carte choroplèthe
fig = px.choropleth(
    df,
    locations="reporterCodeIsoAlpha3",
    color="RSCA",            # La colonne qui définit la couleur
    hover_name="text",       
    color_continuous_scale=px.colors.sequential.haline, # Palette de couleurs
    title="RSCA by country for copper product"
)

# 3. Personnaliser la mise en page (optionnel)
fig.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0}, # Réduire les marges
    geo=dict(showframe=False, showcoastlines=True)
)

# 4. Afficher dans le navigateur web
fig.show()

# 5. Si vous souhaitez l'enregistrer directement en HTML autonome :
# fig.write_html("carte_interactive.html")