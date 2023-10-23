import dash
from dash import dcc
from dash import html
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json
import numpy as np
import plotly.graph_objects as go

map_box_access_token = "pk.eyJ1Ijoic2hhbmtzLXQiLCJhIjoiY2xvMzl2aDFkMGcxbjJpbW5mcnZhNDd4dSJ9.BUHTrMtgxWdtNy78qm98KQ"

DEFAULT_COLORSCALE = [
    "#f2fffb",
    "#bbffeb",
    "#98ffe0",
    "#79ffd6",
    "#6df0c8",
    "#69e7c0",
    "#59dab2",
    "#45d0a5",
    "#31c194",
    "#2bb489",
    "#25a27b",
    "#1e906d",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]

# Read in the data
df_election = pd.read_csv('./data/fips_df.csv')
gdf = gpd.read_file('./data/Congressional_Districts.geojson')  # replace with your geojson file path

# Convert all Timestamp objects to strings
gdf = gdf.map(lambda x: str(x) if isinstance(x, pd.Timestamp) else x)

# ...Data Processing...
# Update '00' districts to '01' in GeoJSON data
gdf['DISTRICT'] = gdf['DISTRICT'].replace('00', '01')
df_election['District'] = df_election['District'].apply(lambda x: str(x).zfill(2))

# Convert the STATEFP20 columns to string in both DataFrames
gdf['STATEFP20'] = gdf['STATEFP20'].astype(str).str.zfill(2)
df_election['STATEFP20'] = df_election['STATEFP20'].astype(str).str.zfill(2)

# Convert STATEFP20 columns to string
gdf['STATEFP20'] = gdf['STATEFP20'].astype(str)
df_election['STATEFP20'] = df_election['STATEFP20'].astype(str)
gdf['DISTRICT'] = gdf['DISTRICT'].astype(str)
df_election['District'] = df_election['District'].astype(str)


# Remove any leading or trailing whitespace
gdf['DISTRICT'] = gdf['DISTRICT'].str.strip()
df_election['District'] = df_election['District'].str.strip()

merged_gdf = gdf.merge(df_election, left_on=['STATEFP20', 'DISTRICT'], right_on=['STATEFP20', 'District'], how='left')

geojson = json.loads(merged_gdf.to_json())

# Use Choroplethmapbox for simplicity
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson,
    locations=merged_gdf.index,
    z=merged_gdf["Total_Spent_Per_District"],
    colorscale=DEFAULT_COLORSCALE,
    marker_opacity=0.5,
    marker_line_width=0,
    customdata=merged_gdf["Name"],
    hovertemplate="%{customdata}<br>Total Spent: %{z:$}"
))

fig.update_layout(mapbox_style="carto-positron", 
                  mapbox_zoom=3, 
                  mapbox_center={"lat": 37.0902, "lon": -95.7129},
                  margin={"r":0,"t":0,"l":0,"b":0})


# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Election Data Visualization"),
    dcc.Graph(figure=fig, style={'height': '80vh', 'width': '100%'})
])

if __name__ == '__main__':
    app.run_server(debug=True)