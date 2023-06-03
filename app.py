import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from shiny import ui, render, App
from shinywidgets import output_widget, render_widget
from utils import generate_dataframe, ESTADOS, ANOS, FAIXAS_ETARIAS

# Create some random data
# A list of Python's built-in functions

app_ui = ui.page_fluid(
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
    output_widget("my_widget"),
    ui.div(
        ui.input_selectize(
            "srag", "SRAG", ['SARS2', 'FLUA', 'FLUB', 'VSR']
        ),
        class_="d-flex gap-3"
    ),
    output_widget("media_movel")
)

def server(input, output, session):
    @output
    @render_widget
    def my_widget():
        plot_df = generate_dataframe(input.estado(), input.faixa_etaria())
        if input.ano() != "Todos":
            plot_df = plot_df[plot_df["ANO_SIN_PRI"] == int(input.ano())]

        fig = px.line(
            plot_df,
            x=plot_df.index, 
            y=['POS_FLUA', 'POS_FLUB', 'POS_SARS2', 'POS_VSR'],
            custom_data=["N_INTERNACOES", "SEM_PRI", "SEM_SIN_PRI", "ANO_SIN_PRI"]
        )

        fig.update_xaxes(
            row=1, col=1, rangeslider_visible=True, tickformat="%b\n%Y", dtick="M1"
        )
        fig.update_yaxes(range=[0, 1])
        fig.update_traces(
            hovertemplate = "<br>".join([
                                        "Positividade: %{y}",
                                        "Semana: %{customdata[1]}",
                                        "Semana epidemiologica: %{customdata[2]}",
                                        "Ano: %{customdata[3]}",
                                        "N internacoes semana: %{customdata[0]}",
                                    ]),
            mode="markers+lines")
        fig.update_layout(
            xaxis_title='Semana epidemiológica',
            yaxis_title='Positividade',
            title='Positividade pra diferentes SRAGs em cada semana epidemiológica',
        )

        return fig

    @output
    @render_widget
    def media_movel():
        DF = generate_dataframe(input.estado(), input.faixa_etaria())

        if input.ano() != "Todos":
            DF = DF[DF["ANO_SIN_PRI"] == int(input.ano())]

        DF['MA4'] = (DF[f"POS_{input.srag()}"].rolling(4).mean())
        DF['MA8'] = (DF[f"POS_{input.srag()}"].rolling(8).mean())
        DF['MA12'] = (DF[f"POS_{input.srag()}"].rolling(12).mean())
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=DF.index,
                y=DF.MA4,
                mode='lines',
                name='4 semanas',
                customdata=np.stack((DF["SEM_PRI"], DF["ANO_SIN_PRI"], DF['SEM_SIN_PRI']), axis=-1)
            )
        )
        fig.add_trace(
            go.Scatter(
                x=DF.index,
                y=DF.MA8,
                mode='lines',
                name='8 semanas',
                customdata=np.stack((DF["SEM_PRI"], DF["ANO_SIN_PRI"], DF['SEM_SIN_PRI']), axis=-1)
            )
        )
        fig.add_trace(
            go.Scatter(
                x=DF.index,
                y=DF.MA12,
                mode='lines',
                name='12 semanas',
                customdata=np.stack((DF["SEM_PRI"], DF["ANO_SIN_PRI"], DF['SEM_SIN_PRI']), axis=-1)
            )
        )

        fig.update_layout(
            xaxis_title='Semana epidemiológica',
            yaxis_title='Media movel da positividade',
            title='Media movel da positividade por semana epidemiológica',
        )

        fig.update_xaxes(tickformat="%b\n%Y", dtick="M1")
        fig.update_traces(
        hovertemplate = "<br>".join([
                                    "Pos. media: %{y}",
                                    "Semana: %{customdata[0]}",
                                    "Semana primeiros sintomas: %{customdata[2]}",
                                    "Ano: %{customdata[1]}",
                                ]),
        mode="lines")

        return fig 


app = App(app_ui, server)