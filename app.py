#!/usr/bin/env python
# coding: utf-8

import pandas as pd
# import plotly
import plotly.express as px
from dash import dcc
from dash import html
from dash import Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import geopandas as gp
import numpy as np

# import json

# from jupyter_dash import JupyterDash
# from openpyxl import Workbook
# import ogr

# import pyproj
# import plotly.io as pio

# Sozialdaten einlesen
df_soz = pd.read_csv("soz_lage_2019.csv", encoding='utf-8-sig', sep=';')
# utf-8-sig
# Geodaten einlesen
# geo_df = json.loads("gemeinden_simplify200.geojson")
geo_df = gp.read_file('gemeinden_simplify200.geojson', encoding="ISO-8859-1")
# geo_df.to_csv("geo_df.csv", sep=';', encoding='utf-8-sig')

# Daten vorbereiten

df_soz2 = df_soz[['Kommune', 'Landkreis', '2019 Kinderarmut (%)',
                  '2019 Jugendarmut (%)',
                  '2019 Altersarmut (%)',
                  '2019 SGB II-Quote (%)',
                  '2019 ALG II-Quote (%)',
                  '2019 Haushalte mit niedrigem Einkommen (%)',
                  ]]

df_soz3 = df_soz2.copy(deep=True)

df_soz3["2019 Kinderarmut (%)"] = df_soz3["2019 Kinderarmut (%)"].str.replace(',', '.')
df_soz3["2019 Jugendarmut (%)"] = df_soz3["2019 Jugendarmut (%)"].str.replace(',', '.')
df_soz3["2019 Altersarmut (%)"] = df_soz3["2019 Altersarmut (%)"].str.replace(',', '.')
df_soz3["2019 SGB II-Quote (%)"] = df_soz3["2019 SGB II-Quote (%)"].str.replace(',', '.')
df_soz3["2019 ALG II-Quote (%)"] = df_soz3["2019 ALG II-Quote (%)"].str.replace(',', '.')
df_soz3['2019 Haushalte mit niedrigem Einkommen (%)'] = df_soz3[
    '2019 Haushalte mit niedrigem Einkommen (%)'].str.replace(',', '.')

df_soz3.loc[df_soz3["2019 Kinderarmut (%)"] == 'k.A.', "2019 Kinderarmut (%)"] = np.nan
df_soz3.loc[df_soz3["2019 Jugendarmut (%)"] == 'k.A.', "2019 Jugendarmut (%)"] = np.nan
df_soz3.loc[df_soz3["2019 Altersarmut (%)"] == 'k.A.', "2019 Altersarmut (%)"] = np.nan
df_soz3.loc[df_soz3["2019 SGB II-Quote (%)"] == 'k.A.', "2019 SGB II-Quote (%)"] = np.nan
df_soz3.loc[df_soz3["2019 ALG II-Quote (%)"] == 'k.A.', "2019 ALG II-Quote (%)"] = np.nan
df_soz3.loc[df_soz3[
                '2019 Haushalte mit niedrigem Einkommen (%)'] == 'k.A.', '2019 Haushalte mit niedrigem Einkommen (%)'] = np.nan

df_soz3.drop(df_soz3.tail(7).index, inplace=True)

df_soz3.astype({"2019 Kinderarmut (%)": 'float64',
                "2019 Jugendarmut (%)": 'float64',
                "2019 Altersarmut (%)": 'float64',
                "2019 SGB II-Quote (%)": 'float64',
                "2019 ALG II-Quote (%)": 'float64',
                '2019 Haushalte mit niedrigem Einkommen (%)': 'float64',
                }) \
    # .info()

# df_soz3.to_csv("df_soz3.csv", sep=';', encoding='utf-8-sig')


# shapefile und Daten mergen

geo_df = pd.merge(left=geo_df, right=df_soz3[
    ["Kommune", "Landkreis", '2019 SGB II-Quote (%)', "2019 Kinderarmut (%)", "2019 Jugendarmut (%)",
     "2019 Altersarmut (%)", "2019 ALG II-Quote (%)", "2019 Haushalte mit niedrigem Einkommen (%)"]], left_on="GEN",
                  right_on="Kommune", how="left")
geo_df = geo_df.set_index("GEN")
geo_df['2019 SGB II-Quote (%)'] = geo_df['2019 SGB II-Quote (%)'].astype("float")
geo_df['2019 Kinderarmut (%)'] = geo_df['2019 Kinderarmut (%)'].astype("float")
geo_df['2019 Jugendarmut (%)'] = geo_df['2019 Jugendarmut (%)'].astype("float")
geo_df['2019 Altersarmut (%)'] = geo_df['2019 Altersarmut (%)'].astype("float")
geo_df['2019 ALG II-Quote (%)'] = geo_df['2019 ALG II-Quote (%)'].astype("float")
geo_df['2019 Haushalte mit niedrigem Einkommen (%)'] = geo_df['2019 Haushalte mit niedrigem Einkommen (%)'].astype(
    "float")

# geo_df.to_csv("geo_df_merged.csv", sep=';', encoding='utf-8-sig')


# geo_df = pd.read_csv("geo_df_merged.csv", encoding='utf-8-sig', sep=';')
# df_soz3 = pd.read_csv("df_soz3.csv", encoding='utf-8-sig', sep=';')


# App
# TODO Anregungen für Weiterentwicklung hier: https://dash.gallery/dash-food-consumption/

external_stylesheets = [dbc.themes.SPACELAB]

app = Dash(__name__,
           external_stylesheets=external_stylesheets,
           )

server = app.server

landkreise = df_soz3['Landkreis'].unique()

header = html.H4("Sozialdaten auf Gemeindeebene, 2019",
                 className="bg-primary text-white p-3 mb-2 text-center")

# TODO add text field: " ... So beträgt der Abstand zwischen der Gemeinde mit der höchsten und der niedrigsten SGB II Quote im Landkreis "Name" [X] Prozentpunkte und liegt damit [Y] Prozentpunkte über/unter dem deutschen  Durchschnitt
# # working template for text card (for later use)
# minmax_card = html.Div(
#                       [
#                           dbc.Card(
#                             dbc.CardBody(
#                 [
#                     html.H4("Auf einen Blick", className="card-title"),
#                     html.P(
#                         "Some quick example text to build on the card title and "
#                         "make up the bulk of the card's content.",
#                         className="card-text",
#                     ),
#                 ],
#     style = {"width": "18rem"}
#             )
#                         id="minmax_text",
#                           )
#                       ]
# )


dropdown = html.Div(
    [
        dbc.Label("Wählen Sie einen Landkreis aus (Texteingabe möglich):"),
        dcc.Dropdown(
            df_soz3['Landkreis'].unique(),
            value="Roth, LK",
            id='dropdown'
        ),
    ], style={
        'width': '50%',
        'display': 'inline-block'
    },
    className="mb-4",
)


fig = html.Div(
    [dcc.Graph
        (
        id='example-graph',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
        style={'height': '40vh'},
    ),
    ],
)

fig3 = html.Div(
    [dcc.Graph
        (
        id='example-graph3',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
        style={'height': '40vh'},
    ),
    ],
)

fig4 = html.Div(
    [dcc.Graph
        (
        id='example-graph4',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '70vh', 'display': 'inline-block'}
        style={'height': '70vh'}

    ),
    ],
)

# TODO add graph showing distance between min / max values of each Landkreis of the respective Bundesland


# layout
# In order to develop our layout very easily, we used two types of flexible containers from the dash_bootstrap_components(dbc)
# library: dbc.Card & dbc.Container:

input_and_map = dbc.Card([dropdown, minmax_card, fig4], body=True)

charts = dbc.Card([fig, fig3], body=True)



app.layout = dbc.Container(
    [
        header,
        dbc.Row
            (
            [
                dbc.Col([input_and_map],
                        #width=6,
                        xs=10, sm=8, md=5, lg=6, xl=5,
                        style={"height": "100%"}
                        ),
                dbc.Col([charts],
                        #width=6,
                        xs=10, sm=8, md=5, lg=6, xl=5,
                        style={"height": "100%"}
                        ),
            ],
            className="h-100"
        ),
    ],
    fluid=True,
    className="dbc",
    style={"height": "100vh"}
)


@app.callback(
    [
        Output(component_id='example-graph', component_property='figure'),
        Output(component_id='example-graph3', component_property='figure'),
        Output(component_id='example-graph4', component_property='figure'),
        Output(component_id='minmax_text', component_property='children')
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
# manually specifying labels: https://plotly.com/python/figure-labels/
    fig = px.bar(dff,
                 x="Landkreis",
                 y="2019 Kinderarmut (%)",
                 color="Kommune",
                 barmode="group",
                 color_discrete_sequence=px.colors.sequential.Viridis,
                 labels={
                     "Kommune": "Gemeinden"
                        },
                 )

# overview on methods for defining layout: https://plotly.com/python/reference/layout/
    fig.update_layout(
        font_family="Courier New, monospace",
        title_font_family="Courier New, monospace",
        plot_bgcolor="#ffffff",
        legend=dict(
            orientation="h",
            y=-0.3,
            xanchor="right",
            x=1
                   )
    )

    fig.update_yaxes(type='linear')

    fig3 = px.bar(dff,
                  x="Landkreis",
                  y='2019 Haushalte mit niedrigem Einkommen (%)',
                  color="Kommune",
                  barmode="group",
                  color_discrete_sequence=px.colors.sequential.Viridis,
                  labels={
                      "Kommune": "Gemeinden"
                  },
                  )

    fig3.update_layout(
        font_family="Courier New, monospace",
        title_font_family="Courier New, monospace",
        plot_bgcolor="#ffffff",
# legend positioning and tweaking: https://plotly.com/python/legend/?_ga=2.205267728.1447699042.1673006461-1475463668.1670716474#legend-position, https://plotly.com/python/reference/?_ga=2.205267728.1447699042.1673006461-1475463668.1670716474#layout-legend
        legend=dict(
            orientation="h",
            y=-0.3,
            xanchor="right",
            x=1
        )
    )

    fig3.update_yaxes(type='linear')

# basics on creating maps: https://plotly.com/python/map-configuration/
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

# tweaking coloraxis of choropleth map: # https://stackoverflow.com/questions/68174188/update-colorbar-coloraxis-position-plotly-python, https://plotly.com/python/reference/layout/coloraxis/
    fig4.update_coloraxes(colorbar_orientation="h",
                          colorbar_x=1,
                          colorbar_xanchor="right",
                          colorbar_y=-0.3,
                          colorbar_title_side="top",
                          colorbar_thickness=10
                          )

    fig4.update_geos(fitbounds="locations", visible=False)



    return fig, fig3, fig4, minmax_card


if __name__ == '__main__':
    app.run_server(debug=True)

# mode='external', port=3003
