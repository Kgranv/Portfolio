import plotly.express as px

# 1. Charger les données d'exemple (Gapminder)
df = px.data.gapminder().query("year == 2007")

# 2. Créer la carte choroplèthe
fig = px.choropleth(
    df,
    locations="iso_alpha",       # Code ISO du pays (ex: 'FRA', 'USA')
    color="lifeExp",            # La colonne qui définit la couleur
    hover_name="country",       # Le nom du pays affiché au survol
    color_continuous_scale=px.colors.sequential.Plasma, # Palette de couleurs
    title="Espérance de vie mondiale (2007)"
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