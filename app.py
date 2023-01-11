#!/usr/bin/env python
# coding: utf-8

###############
# Preparation #
###############

# region Import libraries
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash import Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import geopandas as gp
import numpy as np

# import plotly
# import json
# from jupyter_dash import JupyterDash
# from openpyxl import Workbook
# import ogr
# import pyproj
# import plotly.io as pio

# endregion

# region read data
# Sozialdaten einlesen
df_soz = pd.read_csv("soz_lage_2019.csv", encoding='utf-8-sig', sep=';')
#df_soz.info()
# utf-8-sig
# Geodaten einlesen
# geo_df = json.loads("gemeinden_simplify200.geojson")
geo_df = gp.read_file('gemeinden_simplify200.geojson', encoding="ISO-8859-1")
# geo_df.to_csv("geo_df.csv", sep=';', encoding='utf-8-sig')
# endregion

# region prepare data
df_soz2 = df_soz[['Kommune', 'Landkreis', '2019 Kinderarmut (%)',
                  '2019 Jugendarmut (%)',
                  '2019 Altersarmut (%)',
                  '2019 SGB II-Quote (%)',
                  '2019 ALG II-Quote (%)',
                  '2019 Haushalte mit niedrigem Einkommen (%)',
                  'Bundesland',
                  'ARS'
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

df_soz3.drop(df_soz3.tail(7).index, inplace=True)

df_soz3.astype({"2019 Kinderarmut (%)": 'float64',
                "2019 Jugendarmut (%)": 'float64',
                "2019 Altersarmut (%)": 'float64',
                "2019 SGB II-Quote (%)": 'float64',
                "2019 ALG II-Quote (%)": 'float64',
                '2019 Haushalte mit niedrigem Einkommen (%)': 'float64',
                })#.info()

# df_soz3.to_csv("df_soz3.csv", sep=';', encoding='utf-8-sig')


# shapefile und Daten mergen
# TODO anderes shapefile teste, da Platzierung der Gemeinden in manchen LK nicht korrekt

geo_df = pd.merge(left=geo_df, right=df_soz3[
    ["Kommune", "Landkreis", '2019 SGB II-Quote (%)', "2019 Kinderarmut (%)", "2019 Jugendarmut (%)",
     "2019 Altersarmut (%)", "2019 ALG II-Quote (%)", "2019 Haushalte mit niedrigem Einkommen (%)"]],
    left_on="GEN", right_on="Kommune", how="left")

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
# endregion


#######
# App #
#######

# region init app
# TODO Anregungen für Weiterentwicklung hier: https://dash.gallery/dash-food-consumption/

external_stylesheets = [dbc.themes.SPACELAB]

app = Dash(__name__,
           external_stylesheets=external_stylesheets,
           )

server = app.server

landkreise = df_soz3['Landkreis'].unique()

# endregion

# region create html components
header = html.H4("Sozialdaten auf Gemeindeebene, 2019",
                 className="bg-primary text-white p-3 mb-2 text-center")

# TODO dot plot ergänzen

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

# dynamic html field containing a text statement, cf:
# https://community.plotly.com/t/changing-html-p-element-with-callback-function/10933,
# https://stackoverflow.com/questions/65694502/returning-dynamic-text-to-html-p-in-dash,
# https://stackoverflow.com/questions/71688663/how-to-connect-html-elements-with-dash-callback-in-python

minmax_card = html.Div(
                       [
                           dbc.Card(
                             dbc.CardBody(
                        [
                     html.H4("Auf einen Blick",
                             className="card-title"
                             ),
                     html.P(id="minmax_text",
                            className="card-text",
                           ),
                        ],
                        #style = {"width": "18rem"}
                                        ),
                           ),
                       ],
)

fig = html.Div(
    [dcc.Graph
        (
        id='example-graph',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
        style={'height': '60vh'},
    ),
    ],
)

## insert dotplot here as fig2 / example-graph2
fig2 = html.Div(
    [dcc.Graph
        (
        id='example-graph2',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
        style={'height': '100vh'},
    ),
    ],
)

fig3 = html.Div(
    [dcc.Graph
        (
        id='example-graph3',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '40vh', 'display': 'inline-block'},
        style={'height': '60vh'},
    ),
    ],
)

fig4 = html.Div(
    [dcc.Graph
        (
        id='example-graph4',
        config={'displayModeBar': True},
        #style={'width': '80vh', 'height': '70vh', 'display': 'inline-block'}
        style={'height': '100vh'}

    ),
    ],
)

# TODO add graph showing distance between min / max values of each Landkreis of the respective Bundesland
# endregion

# region create layout
# In order to develop our layout very easily, we used two types of flexible containers from the dash_bootstrap_components(dbc)
# library: dbc.Card & dbc.Container:

input_and_map = dbc.Card([dropdown, minmax_card, fig4], body=True)

chart_dotplot = dbc.Card([fig2], body=True)

chart1 = dbc.Card([fig], body=True)

chart2 = dbc.Card([fig3], body=True)



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
                dbc.Col([chart_dotplot],
                        #width=6,
                        xs=10, sm=8, md=5, lg=6, xl=5,
                        style={'overflowY': 'scroll', 'height': 800} # https://community.plotly.com/t/add-scrolling-options-to-plots/9493
                        # TODO scrollbar und höhe anpassen
                        ),
            ],
            className="h-100, g-6"
        ),
# to control space between rows, play around with "margin-top" and "g-x" (unclear how it works exactly)
        dbc.Row
        (
            [
            dbc.Col([chart1],
                    # width=6,
                    xs=10, sm=8, md=5, lg=6, xl=5,
                    style={"height": "100%", "margin-top": "30px"}
                    ),
            dbc.Col([chart2],
                    # width=6,
                    xs=10, sm=8, md=5, lg=6, xl=5,
                    style={"height": "100%", "margin-top": "30px"}
                    ),
            ],
            className="h-100, g-6"
        ),
    ],
    fluid=True,
    className="dbc",
    style={"height": "100vh"}
)
# endregion

#
# # region Baustelle dot plot
# # TODO Sortierung nach Spannweite implementieren
# # TODO Gemeinde der min max Werte in tooltip anzeigen
# # creating dynaminc filter variable for Bundesland of selected Landkreis (replace df_soz3 with dff)
# selected_bl = df_soz3['Bundesland'].loc[df_soz3.index[0]]
# # filtering df_soz3 with the selected Bundesland
# dot_df = df_soz3[df_soz3["Bundesland"] == selected_bl]
# # selecting required columns
# dot_df1 = dot_df[["Kommune", "Landkreis", "2019 SGB II-Quote (%)"]]
# # creating two tables for the min and max values of each Landkreis
# dot_df1_min = dot_df1.astype({"2019 SGB II-Quote (%)": 'float64'}).sort_values("2019 SGB II-Quote (%)").groupby("Landkreis", as_index=False).first()
# dot_df1_min['minmax']='min'
# dot_df1_max = dot_df1.astype({"2019 SGB II-Quote (%)": 'float64'}).sort_values("2019 SGB II-Quote (%)", ascending=False).groupby("Landkreis", as_index=False).first()
# dot_df1_max['minmax']='max'
# # concating the tables
# df_dot_minmax = pd.concat([dot_df1_min, dot_df1_max], ignore_index=True, axis=0)
# df_dot_minmax = df_dot_minmax.sort_values("2019 SGB II-Quote (%)", ascending=False)
# # ploting data on a dot plot
# # Use column names of df for the different parameters x, y, color, ...
#
#
# fig2 = px.scatter(df_dot_minmax, x="2019 SGB II-Quote (%)", y="Landkreis", color="minmax",
#                  title="Spannweite der SGB II Quoten", # hier noch das Bundesland anfügen
#                  hover_data=['Kommune', "2019 SGB II-Quote (%)"]
#                  #labels={"salary":"Annual Salary (in thousands)"} # customize axis label
#                 )
# fig2.update_traces(marker_size=15)
#
# # https://community.plotly.com/t/plotly-colours-list/11730/3
# # https://plotly.com/python/axes/?_ga=2.145648308.1006701091.1673255542-1435390182.1649168166#styling-and-coloring-axes-and-the-zeroline
# fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='slateblue', griddash='dot')
# fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='slateblue', griddash='dot')
#
# fig2.update_layout(
#         font_family="Courier New, monospace",
#         title_font_family="Courier New, monospace",
#         plot_bgcolor="#ffffff",
#         )
# endregion



# region Callback
@app.callback(
    [
        Output(component_id='example-graph', component_property='figure'),
        Output(component_id='example-graph3', component_property='figure'),
        Output(component_id='example-graph4', component_property='figure'),
        Output(component_id='example-graph2', component_property='figure'),
        Output(component_id='minmax_text', component_property='children')
    ],
    Input(component_id='dropdown', component_property='value')
)
# endregion

# region Callback function
def update_graph(selected_region):
    dff = df_soz3[df_soz3.Landkreis == selected_region]

    geo_dff = geo_df[geo_df.Landkreis == selected_region]

    # selected_bl = dff['Bundesland'].loc[dff.index[0]] #"irgendein Wert aus der Spalte Bundesland in dff"
    # dot_df = df_soz3 # filtern mit selected_lk

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

    # creating dynaminc filter variable for Bundesland of selected Landkreis (replace df_soz3 with dff)
    selected_bl = dff['Bundesland'].loc[dff.index[0]]
    # filtering df_soz3 with the selected Bundesland
    dot_df = df_soz3[df_soz3["Bundesland"] == selected_bl]
    # selecting required columns
    dot_df1 = dot_df[["Kommune", "Landkreis", "2019 SGB II-Quote (%)"]]
    # creating two tables for the min and max values of each Landkreis
    dot_df1_min = dot_df1.astype({"2019 SGB II-Quote (%)": 'float64'}).sort_values("2019 SGB II-Quote (%)").groupby(
        "Landkreis", as_index=False).first()
    dot_df1_min['minmax'] = 'min'
    dot_df1_max = dot_df1.astype({"2019 SGB II-Quote (%)": 'float64'}).sort_values("2019 SGB II-Quote (%)",
                                                                                   ascending=False).groupby("Landkreis",
                                                                                                            as_index=False).first()
    dot_df1_max['minmax'] = 'max'
    # concating the tables
    df_dot_minmax = pd.concat([dot_df1_min, dot_df1_max], ignore_index=True, axis=0)
    df_dot_minmax = df_dot_minmax.sort_values("2019 SGB II-Quote (%)", ascending=False)
    # ploting data on a dot plot
    # Use column names of df for the different parameters x, y, color, ...


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

    fig2 = px.scatter(df_dot_minmax, x="2019 SGB II-Quote (%)", y="Landkreis", color="minmax",
                      title="Spannweite der SGB II Quoten",  # hier noch das Bundesland anfügen
                      hover_data=['Kommune', "2019 SGB II-Quote (%)"],
                      # labels={"salary":"Annual Salary (in thousands)"} # customize axis label
                      )
    fig2.update_traces(marker_size=5)

    # https://community.plotly.com/t/plotly-colours-list/11730/3
    # https://plotly.com/python/axes/?_ga=2.145648308.1006701091.1673255542-1435390182.1649168166#styling-and-coloring-axes-and-the-zeroline
    fig2.update_xaxes(showgrid=True, gridwidth=1, gridcolor='slateblue', griddash='dot')
    fig2.update_yaxes(showgrid=True, gridwidth=1, gridcolor='slateblue', griddash='dot')

    fig2.update_layout(
        font_family="Courier New, monospace",
        title_font_family="Courier New, monospace",
        plot_bgcolor="#ffffff",
    )

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
# legend positioning and tweaking:
# https://plotly.com/python/legend/?_ga=2.205267728.1447699042.1673006461-1475463668.1670716474#legend-position,
# https://plotly.com/python/reference/?_ga=2.205267728.1447699042.1673006461-1475463668.1670716474#layout-legend
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

# tweaking coloraxis of choropleth map:
# https://stackoverflow.com/questions/68174188/update-colorbar-coloraxis-position-plotly-python,
# https://plotly.com/python/reference/layout/coloraxis/
    fig4.update_coloraxes(colorbar_orientation="h",
                          colorbar_x=1,
                          colorbar_xanchor="right",
                          colorbar_y=-0.3,
                          colorbar_title_side="top",
                          colorbar_thickness=10
                          )

    fig4.update_geos(fitbounds="locations", visible=False)

# calculating range between min/max values in column "2019 SGB II-Quote (%)" of geo_dff:
# https://www.w3schools.com/python/pandas/ref_df_max.asp
# https://www.geeksforgeeks.org/accessing-elements-of-a-pandas-series/

    col = "2019 SGB II-Quote (%)"
    max_col = geo_dff.loc[geo_dff[col].idxmax()]
    max_gem = max_col["Kommune"]
    max_val = max_col["2019 SGB II-Quote (%)"].astype(float)

    min_col = geo_dff.loc[geo_dff[col].idxmin()]
    min_gem = min_col["Kommune"]
    min_val = min_col["2019 SGB II-Quote (%)"].astype(float)
    range_val = round((max_val) - (min_val), 1)

# writing the results in a statement to be passed on towards the dynamic html component

    statement = ("Die Gemeinde mit der höchsten Quote ist ", max_gem, " mit einem Wert von ", max_val,
          "%. Die Gemeinde mit der niedrigsten Quote in diesem Landkreis ist ", min_gem, " mit einem Wert von ", min_val,
          "%. Das entspricht einer Spannweite zwischen höchstem und niedrigstem Wert von ", range_val, " Prozentpunkten.")

    return fig, fig3, fig4, fig2, statement
# endregion

# region run server
if __name__ == '__main__':
    app.run_server(debug=True,
                   # mode='external',
                   # port=3003)
                   ),
# endregion


