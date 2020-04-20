import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

tab_5_layout= html.Div([
    dash_table.DataTable(
        id='cementing-table',
        columns = [{'name':i,'id':i,'type':'text'} if i in ['Casing/Pipe Section'] else {'name':i,'id':i,'type':'numeric'} for i in ['Top Depth (ft)','Set Depth (ft)','Casing/Pipe Section','Cement Cost ($)','Est. Cementing Time (hr)']],
        data=[],
        editable=True,
        row_deletable=True,
        # style_as_list_view=True,
        style_header={
            'font-family': 'system-ui',
            'font-weight':'bold'
        },
        style_cell={
            'textAlign': 'center',
            'font-family': 'system-ui'
        }
    ),
    html.Button(
        'Add Row',
        id='cementing-add-row-button', 
        n_clicks=0,
        style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px'
                }
        )
])
