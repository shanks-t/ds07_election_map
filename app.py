import dash
from dash import dcc
from dash import html
import pandas as pd
import geopandas as gpd
import plotly.express as px
import json
import numpy as np
import plotly.graph_objects as go
from shapely import wkb

merged_gdf = pd.read_parquet('./data/merged_gdf.parquet')

# Replace NaN values with a default value or remove rows with NaN values
merged_gdf = merged_gdf.dropna(subset=['Percent_Spent'])

# Round 'Percent_Spent' to 2 decimals
merged_gdf["Percent_Spent"] = merged_gdf["Percent_Spent"].round(2)

CUSTOM_COLORSCALE = [
    [0.0,   'rgb(255,250,240)'],   # Corresponds to 0%   - Lightest Peach
    [0.2,   'rgb(255,245,230)'],   # Corresponds to 20%
    [0.4,   'rgb(255,235,215)'],   # Corresponds to 40%
    [0.5,   'rgb(255,220,195)'],   # Corresponds to 50%
    [0.55,  'rgb(255,210,185)'],   # Corresponds to 55%
    [0.6,   'rgb(255,195,165)'],   # Corresponds to 60%
    [0.65,  'rgb(255,180,150)'],   # Corresponds to 65%
    [0.7,   'rgb(255,165,130)'],   # Corresponds to 70%
    [0.75,  'rgb(255,150,115)'],   # Corresponds to 75%
    [0.825, 'rgb(255,135,100)'],   # Corresponds to 82.5%
    [0.85,  'rgb(255,120,85)'],    # Corresponds to 85%
    [0.875, 'rgb(255,105,70)'],    # Corresponds to 87.5%
    [0.9,   'rgb(255,90,60)'],     # Corresponds to 90%
    [0.925, 'rgb(255,75,50)'],     # Corresponds to 92.5%
    [0.95,  'rgb(255,60,40)'],     # Corresponds to 95%
    [0.96,  'rgb(245,50,35)'],     # Corresponds to 96%
    [0.97,  'rgb(235,40,30)'],     # Corresponds to 97%
    [0.98,  'rgb(225,30,25)'],     # Corresponds to 98%
    [0.995, 'rgb(215,20,20)'],     # Corresponds to 99.5%
    [1.0,   'rgb(205,0,0)']        # Corresponds to 100% - Darkest Peach
]

# Convert the binary 'geometry' column back to shapely geometry
merged_gdf['geometry'] = merged_gdf['geometry'].apply(wkb.loads)

# Convert back to a GeoDataFrame
gdf = gpd.GeoDataFrame(merged_gdf, geometry='geometry')
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001)

geojson_str = gdf.to_json()
geojson = json.loads(geojson_str)

# Use Choroplethmapbox for simplicity
fig = go.Figure(go.Choroplethmapbox(
    geojson=geojson,
    locations=merged_gdf.index,
    z=merged_gdf["Percent_Spent"],
    colorscale=CUSTOM_COLORSCALE,
    marker_opacity=0.5,
    marker_line_width=0,
    customdata=np.stack([
    merged_gdf['Name'], 
    merged_gdf['Party'], 
    merged_gdf['State'], 
    merged_gdf['District'],
    merged_gdf['Incumbent'], 
    merged_gdf['Percent_Spent'], 
    merged_gdf['Total_Spent_Per_District'], 
], axis=-1),
    hovertemplate="<b>%{customdata[0]}</b> - %{customdata[1]}<br>" +
                  "District: %{customdata[2]}%{customdata[3]}<br>" +  # District
                  "Incumbent: %{customdata[4]}<br>" +  # Incumbent
                  "Percent Spent: %{customdata[5]:.2f}%<br>" +  # Percent Spent
                  "Total Spent in District: $%{customdata[6]:,.0f}<extra></extra>",
    showlegend=False,
))

fig.update_layout(
    mapbox_style="carto-positron",
    mapbox_zoom=3,
    mapbox_center={"lat": 37.0902, "lon": -95.7129},
    mapbox_bearing=0,   # Set the bearing
    mapbox_pitch=0,     # Set the pitch
    uirevision='no_wrap',   # This ensures the state of user interactions (zoom, pan) persist across updates
    margin={"r":0,"t":0,"l":0,"b":0},
    legend_title_text='Percentages',  # This is the title for the legend/colorbar
    legend=dict(
        orientation="v",  # vertical orientation
        yanchor="top", 
        y=1.08,
        xanchor="left", 
        x=1.02
    )
)

# Dash App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Heat Map of Percent of Total Spent by Winner in Each District for 2020 House Elections"),
    html.P('Hovering over each district displays the winner of that district, whether they were incumbent and what percent of the total spent in that district was spent by this candidate', style={
        'fontSize': '16px',
        'color': '#888',
        'textAlign': 'left',
        'marginTop': '20px'
    }),
    dcc.Graph(figure=fig, style={'height': '80vh', 'width': '100%'}),
])

server = app.server


