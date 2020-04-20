import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

logging_cols = [{'name':'Top Depth (ft)','id':'Top Depth (ft)','type':'numeric','editable':True}]
logging_cols.extend([{'name':'Bottom Depth (ft)','id':'Bottom Depth (ft)','type':'numeric','editable':True}])
logging_cols.extend([{'name':'Logging Method','id':'Logging Method','presentation':'dropdown','editable':True}])
logging_cols.extend([{'name':'Logging Activity','id':'Logging Activity','type':'text','editable':True}])
logging_cols.extend([{'name':i,'id':i,'type':'numeric','editable':True} for i in ['Service Cost ($/day)','Est. Logging Time (hrs)','Est. Non-Productive Time (hrs)']])
logging_cols.extend([{'name':'Logging Cost ($)','id':'Logging Cost ($)','type':'numeric','editable':False}])

tab_6_layout= html.Div([
    dash_table.DataTable(
        id='logging-table',
        columns = logging_cols,
        data=[],
        editable=True,
        column_static_dropdown=[
            {
                'id': 'Logging Method',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['LWD', 'Wireline','Other']
                ]
            },
        ],
        row_deletable=True,
        # style_as_list_view=True,
        style_header={
            'font-family': 'system-ui',
            'font-weight':'bold'
        },
        style_cell={
            'textAlign': 'center',
            'font-family': 'system-ui'
        },
        style_data_conditional=[{
            'if': {'column_id':'Logging Cost ($)'},
            'backgroundColor':'#73ace2a2'
        }],
    ),
    html.Button(
        'Add Row',
        id='logging-add-row-button',
        n_clicks=0,
        n_clicks_timestamp=0,
        style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px'
        }
    ),
    html.Button(
        'Calculate',
        id='logging-calculate-button',
        n_clicks=0,
        n_clicks_timestamp=0,
        style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px',
                    'margin-left':'5px'
        }
    )
])
