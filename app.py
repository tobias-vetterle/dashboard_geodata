#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import plotly
import plotly.express as px
from dash import dcc
from dash import html
from dash import Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import geopandas as gp
import numpy as np


# from jupyter_dash import JupyterDash
# from openpyxl import Workbook
# import ogr
# import json
# import pyproj
# import plotly.io as pio

# Sozialdaten einlesen
df_soz = pd.read_csv("soz_lage_2019.csv", encoding='utf-8-sig', sep=';')
# Geodaten einlesen
geo_df = gp.read_file('gemeinden_simplify200.geojson', encoding="ISO-8859-1")
# geo_df.to_csv("geo_df.csv", sep=';', encoding='utf-8-sig')

# Daten vorbereiten

df_soz2 = df_soz[['Kommune', 'Landkreis', '2019 Kinderarmut (%)',
  '2019 Jugendarmut (%)',
  '2019 Altersarmut (%)',
  '2019 SGB II-Quote (%)',
  '2019 ALG II-Quote (%)',
  '2019 Haushalte mit niedrigem Einkommen (%)',
  'geometry'
                  ]]

df_soz3 = df_soz2.copy(deep=True)

df_soz3["2019 Kinderarmut (%)"] = df_soz3["2019 Kinderarmut (%)"].str.replace(',', '.')
df_soz3["2019 Jugendarmut (%)"] = df_soz3["2019 Jugendarmut (%)"].str.replace(',', '.')
df_soz3["2019 Altersarmut (%)"] = df_soz3["2019 Altersarmut (%)"].str.replace(',', '.')
df_soz3["2019 SGB II-Quote (%)"] = df_soz3["2019 SGB II-Quote (%)"].str.replace(',', '.')
df_soz3["2019 ALG II-Quote (%)"] = df_soz3["2019 ALG II-Quote (%)"].str.replace(',', '.')
df_soz3['2019 Haushalte mit niedrigem Einkommen (%)'] = df_soz3['2019 Haushalte mit niedrigem Einkommen (%)'].str.replace(',', '.')


df_soz3.loc[df_soz3["2019 Kinderarmut (%)"] == 'k.A.', "2019 Kinderarmut (%)"] = np.nan
df_soz3.loc[df_soz3["2019 Jugendarmut (%)"] == 'k.A.', "2019 Jugendarmut (%)"] = np.nan
df_soz3.loc[df_soz3["2019 Altersarmut (%)"] == 'k.A.', "2019 Altersarmut (%)"] = np.nan
df_soz3.loc[df_soz3["2019 SGB II-Quote (%)"] == 'k.A.', "2019 SGB II-Quote (%)"] = np.nan
df_soz3.loc[df_soz3["2019 ALG II-Quote (%)"] == 'k.A.', "2019 ALG II-Quote (%)"] = np.nan
df_soz3.loc[df_soz3['2019 Haushalte mit niedrigem Einkommen (%)'] == 'k.A.', '2019 Haushalte mit niedrigem Einkommen (%)'] = np.nan
df_soz3.loc[df_soz3['geometry'] == '', 'nan'] = np.nan

df_soz3.drop(df_soz3.tail(7).index,inplace=True)

df_soz3.astype({"2019 Kinderarmut (%)": 'float64',
                           "2019 Jugendarmut (%)": 'float64',
                           "2019 Altersarmut (%)": 'float64',
                           "2019 SGB II-Quote (%)": 'float64',
                           "2019 ALG II-Quote (%)": 'float64',
                           '2019 Haushalte mit niedrigem Einkommen (%)': 'float64',
                         })\
    #.info()

# df_soz3.to_csv("df_soz3.csv", sep=';', encoding='utf-8-sig')

df_soz4 = df_soz3.drop(columns = ["nan", "geometry"])
# df_soz4.info()

# shapefile und Daten mergen

geo_df = pd.merge(left=geo_df, right=df_soz4[["Kommune", "Landkreis", '2019 SGB II-Quote (%)', "2019 Kinderarmut (%)", "2019 Jugendarmut (%)", "2019 Altersarmut (%)", "2019 ALG II-Quote (%)", "2019 Haushalte mit niedrigem Einkommen (%)"]], left_on="GEN", right_on="Kommune", how="left")#.dropna()
geo_df = geo_df.set_index("GEN")
geo_df['2019 SGB II-Quote (%)'] = geo_df['2019 SGB II-Quote (%)'].astype("float")
geo_df['2019 Kinderarmut (%)'] = geo_df['2019 Kinderarmut (%)'].astype("float")
geo_df['2019 Jugendarmut (%)'] = geo_df['2019 Jugendarmut (%)'].astype("float")
geo_df['2019 Altersarmut (%)'] = geo_df['2019 Altersarmut (%)'].astype("float")
geo_df['2019 ALG II-Quote (%)'] = geo_df['2019 ALG II-Quote (%)'].astype("float")
geo_df['2019 Haushalte mit niedrigem Einkommen (%)'] = geo_df['2019 Haushalte mit niedrigem Einkommen (%)'].astype("float")

# geo_df.to_csv("geo_df_merged.csv", sep=';', encoding='utf-8-sig')


# geo_df = pd.read_csv("geo_df_merged.csv", encoding='utf-8-sig', sep=';')
# df_soz3 = pd.read_csv("df_soz3.csv", encoding='utf-8-sig', sep=';')



# App

external_stylesheets = [dbc.themes.SPACELAB]

app = Dash(__name__, external_stylesheets=external_stylesheets)

landkreise = df_soz3['Landkreis'].unique()

header = html.H4("Sozialdaten auf Gemeindeebene, 2019",
             className="bg-primary text-white p-3 mb-2 text-center")

dropdown = html.Div(
                    [
                dbc.Label("Wählen Sie einen Landkreis aus (Texteingabe möglich):"),
                dcc.Dropdown(
                df_soz3['Landkreis'].unique(),
                id='dropdown'
                    ),
                    ], style={
                            'width': '28%', 
                            'display': 'inline-block'
                            },
                className="mb-4",
                    )
                    

    
    
fig = html.Div(
                [dcc.Graph
                     (
                        id='example-graph',
                        config={'displayModeBar': True},
                        style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
                     ),
                ], 
               )

fig3 = html.Div(
                [dcc.Graph
                     (
                        id='example-graph3',
                        config={'displayModeBar': True},
                        style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
                     ),
                ], 
               )

fig4 = html.Div(
                [dcc.Graph
                     (
                        id='example-graph4',
                        config={'displayModeBar': True},
                        style={'width': '80vh', 'height': '70vh', 'display': 'inline-block'}
                     ),
                ], 
               )


# layout

input_and_map = dbc.Card([dropdown, fig4], body=True)

charts = dbc.Card([fig, fig3], body = True)

app.layout = dbc.Container(
       [
           header,
           dbc.Row
           (
               [
                dbc.Col([input_and_map],
                        width =6,
                        style={"height": "100%"}
                       ),
                dbc.Col([charts],
                        width =6,
                        style={"height": "100%"}
                       ),
                ],
               className="h-100"
           ),
        ],
        fluid = True,
        className = "dbc",
        style={"height": "100vh"}
                        )


@app.callback(
                [
                    Output(component_id='example-graph', component_property='figure'),
                    Output(component_id='example-graph3', component_property='figure'),
                    Output(component_id='example-graph4', component_property='figure')
                ],
                    Input(component_id='dropdown', component_property='value')
             )


def update_graph(selected_region):
    
    dff = df_soz3[df_soz3.Landkreis == selected_region]
    
    geo_dff = geo_df[geo_df.Landkreis == selected_region]
    
    dff.astype({"2019 Kinderarmut (%)": 'float64', 
                          "2019 Jugendarmut (%)": 'float64', 
                          "2019 Altersarmut (%)": 'float64', 
                          "2019 SGB II-Quote (%)": 'float64', 
                          "2019 ALG II-Quote (%)": 'float64',
                          '2019 Haushalte mit niedrigem Einkommen (%)': 'float64',
                        })

    geo_dff.astype({"2019 Kinderarmut (%)": 'float64', 
                          "2019 Jugendarmut (%)": 'float64', 
                          "2019 Altersarmut (%)": 'float64', 
                          "2019 SGB II-Quote (%)": 'float64', 
                          "2019 ALG II-Quote (%)": 'float64',
                          '2019 Haushalte mit niedrigem Einkommen (%)': 'float64',
                        })
    
    fig = px.bar(dff,
                 x="Landkreis", 
                 y="2019 Kinderarmut (%)", 
                 color="Kommune", 
                 barmode="group", 
                 color_discrete_sequence= px.colors.sequential.Viridis)    

    
    fig.update_layout(
        font_family="Courier New, monospace",
        title_font_family="Courier New, monospace",
        plot_bgcolor="#ffffff",
    )
    
    fig.update_yaxes(type='linear')
    
    fig3 = px.bar(dff, 
                  x="Landkreis", 
                  y='2019 Haushalte mit niedrigem Einkommen (%)', 
                  color="Kommune", 
                  barmode="group", 
                  color_discrete_sequence= px.colors.sequential.Viridis)

    fig3.update_layout(
        font_family="Courier New, monospace",
        title_font_family="Courier New, monospace",
        plot_bgcolor="#ffffff",
    )
    
    fig3.update_yaxes(type='linear')
    
    fig4 = px.choropleth(geo_dff, 
                         geojson=geo_dff.geometry, 
                         locations=geo_dff.index, 
                         color="2019 SGB II-Quote (%)", 
                         projection="mercator", 
                         color_continuous_scale="Viridis")

    fig4.update_layout(
        font_family="Courier New, monospace",
        title_font_family="Courier New, monospace",
    )
    
    fig4.update_geos(fitbounds="locations", visible=False)
    
    return fig, fig3, fig4


if __name__ == '__main__':
    app.run_server()
    
# mode='external', port=3003






