import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from shiny import App, render, ui
from shinywidgets import output_widget, render_widget

from utils import *

pio.templates.default = "plotly_white"

app_ui = ui.page_fluid(
    ui.tags.style(
        """
        ul.nav.nav-pills.nav-stacked {
            width: 200px; /* Set the desired width value */
        }
        div.col-sm-4.well {
            width: 300px;
        }
        div.d-flex.gap-3 {
            margin-top: 25px;
            margin-left: 25px;
            display: flex;
        }
        div.d-flex.gap-4 {
            margin-top: 25px;
            margin-left: 25px;
            display: flex;
        }
        """
    ),
    ui.navset_pill_list(
        ui.nav(
            "Prevalência dos Vírus",
            ui.div(
                ui.input_selectize(
                    "estado", "Estado", ESTADOS
                ),
                ui.input_selectize(
                    "ano", "Ano", ANOS,
                ),
                ui.input_select(
                    "faixa_etaria", "Faixa Etária", FAIXAS_ETARIAS
                ),
                class_="d-flex gap-3"
            ),
            output_widget("graf_lin_list_simple"),
            output_widget("barplot"),
            ui.div(
                ui.input_selectize(
                    "estado_hm", "Estado", ESTADOS
                ),
                class_="d-flex gap-4"
            ),
            output_widget("heatmap_brasil")
        ),
        ui.nav(
            "Metodologia",
            "TBD"
        ),
        ui.nav(
            "Código fonte",
            "TBD"
        ),
        ui.nav(
            "Colaboradores",
            "TBD"
        ),
    ),
    
)

def server(input, output, session):
    @output
    @render_widget
    def graf_lin_list_simple():
        fig = make_subplots(rows=2, cols=1,shared_xaxes=False,row_heights=[0.8, 0.2])
        df = generate_dataframe(input.estado(), input.faixa_etaria())
        for pos in list_pos:
            fig.add_trace(
                go.Scatter(
                    name=pos,
                    x=df['DT_SIN_PRI'],
                    y=df[pos],
                    mode='lines',
                    showlegend=True
                ), 
                row=1,
                col=1
            )
            fig.update_layout(
                height=600,
                width=1200,
                yaxis_title='Prop. Positivos',
                yaxis2_title='Quantidade de testes',
                title='Prevalência para o virus',
                hovermode="x" 
            )
        return fig

    @output
    @render_widget
    def barplot():
        df = generate_dataframe(input.estado(), input.faixa_etaria())
        fig = make_subplots(rows=2, cols=1,shared_xaxes=True,row_heights=[0.8, 0.2])

        for pos in list_pos[::-1]:
            fig.add_trace(
                go.Bar(
                    name=pos,
                    x=df['DT_SIN_PRI'],
                    y=df[pos],
                    showlegend=True
                ),
                row=1,
                col=1
        )
            
        fig.add_trace(
                go.Scatter(
                    x=df['DT_SIN_PRI'],
                    y=df['TESTES'],
                    name="Qtd. testes",
                    showlegend=True,
                ),
                row=2,
                col=1
            )

        fig.update_layout(
            height=600,
            width=1200,
            barmode='stack',
            xaxis={'categoryorder':'array', 'categoryarray':list_pos},
            yaxis_title='Prop. Positivos',
            yaxis2_title='Quantidade de testes',
            title='Prevalência para vírus',
            hovermode="x" 
        )

        return fig 

    @output
    @render_widget
    def heatmap_brasil():
        positive_distribution = pd.read_csv("pos_distri.csv", sep=";")

        if input.estado_hm() == "Todos":
            df = positive_distribution.groupby(["SG_UF_NOT"], as_index=False).sum(["POS_VSR"])
            filename = "Brasil"
            geojson = open_geojson(filename)
            equiv = "UF"
            locations = "SG_UF_NOT"
            custom_data = ["SG_UF_NOT"]
        else:
            positive_distribution = positive_distribution.query(f"SG_UF_NOT=='{input.estado_hm()}'")
            df = positive_distribution.groupby(["CO_MUN_NOT", "ID_MUNICIP"], as_index=False).sum(["POS_SARS2"])
            filename = input.estado_hm()
            mapp = {}
            geojson = open_geojson(filename)
            equiv = "GEOCODIGO"
            for feat in geojson["features"]:
                cod = feat["properties"][equiv]
                mapp[cod[:-1]] = cod
            df["CO_MUN_NOT"] = df["CO_MUN_NOT"].astype(str)
            df["CO_MUN_NOT_ATT"] = df["CO_MUN_NOT"].map(mapp)
            locations = "CO_MUN_NOT_ATT"
            custom_data = ["ID_MUNICIP"]

        lat, lon, zoom = get_lat_lon(input.estado_hm())

        fig = px.choropleth_mapbox(
            df,
            locations = locations,
            geojson = geojson,
            color = "POS_SARS2",
            featureidkey=f"properties.{equiv}",
            mapbox_style = "carto-positron",
            center={"lat":lat, "lon": lon},
            zoom = zoom,
            opacity = 0.5,
            color_continuous_scale="reds",
            custom_data=custom_data
        )
        fig.update_traces(
            hovertemplate="<br>".join([
                "Municipio: %{customdata[0]}",
            ])
        )
        fig.update_layout(
            autosize=False,
            width=800,
            height=800,
        )
        fig.layout.coloraxis.colorbar.title = 'Prob'
        return fig


app = App(app_ui, server)
