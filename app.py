import plotly.graph_objects as go
from plotly.subplots import make_subplots
from shiny import ui, render, App
import plotly.io as pio
from shinywidgets import output_widget, render_widget
from utils import generate_dataframe, ESTADOS, ANOS, FAIXAS_ETARIAS, list_pos


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
            display: flex;
            justify-content: center;
            align-items: center;
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
            output_widget("barplot")
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


app = App(app_ui, server)