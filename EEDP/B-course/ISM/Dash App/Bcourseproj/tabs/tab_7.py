import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

tab_7_layout=html.Div([
    dash_table.DataTable(
        id='logistics-table',
        columns = [{'name':i,'id':i,'type':'numeric'} for i in ['Location Prep Cost ($)','Fuel Cost ($)','Water Cost ($)','Transportation Cost ($)','Rental Equipment Cost ($)','Mobilization/Demobilization (days)','Daily Rig Rate ($/day)']],
        data=[{c:'' for c in ['Location Prep Cost ($)','Fuel Cost ($)','Water Cost ($)','Transportation Cost ($)','Rental Equipment Cost ($)','Mobilization/Demobilization Setup Time (days)','Daily Rig Rate ($/day)']}],
        editable=True,
        row_deletable=False,
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
    html.Div(id='hidden-initializer',children = 'trigger',style = dict(display='none'))
])
