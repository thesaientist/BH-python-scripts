import dash
import dash_core_components as dcc
import dash_table
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

tab_3_layout = html.Div([
    html.H6('Drilling Fluids and Pipe Program'),
    dcc.Graph(
        id='pipe-graph',
        config={
            'displayModeBar': False,
            'staticPlot': True
        },
        figure={
            'data':[],
            'layout': go.Layout(
                xaxis={
                    'showticklabels': False,
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False
                },
                yaxis={
                    'showticklabels': False,
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False
                },
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
            )
        }
    ),
    html.H6('Casing/Pipe'),
    dash_table.DataTable(
        id='drill-casing-table',
        columns = [{'name':i,'id':i,'presentation':'dropdown'} if i in ['Casing/Pipe Section'] else {'name':i,'id':i,'type':'numeric'} for i in ['Top Depth (ft)','Set Depth (ft)','Hole Size (in)','Casing/Pipe Section','Outer Diameter (in)','Inner Diameter (in)','Pipe Cost ($)']],
        data=[],
        editable=True,
        column_static_dropdown=[
            {
                'id': 'Casing/Pipe Section',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['Conductor', 'Surface', 'Intermediate', 'Production', 'Contingency', 'Liner','Other']
                ]
            },
        ],
        row_deletable = True,
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
        id='casing-add-row-button',
        n_clicks=0,
        style={
            'font-family': 'system-ui',
            'color': '#fff',
            'letter-spacing': '0.7px',
            'margin-top':'10px',
            'margin-bottom':'10px'
        }
    ),
    html.H6('Drilling Fluids'),
    dash_table.DataTable(
        id='drill-fluids-table',
        row_deletable = True,
        columns = [{'name':i,'id':i,'presentation':'dropdown'} if i in ['Mud Type','Additives'] else{ 'name':i,'id':i,'type':'numeric'} for i in ['Top Depth (ft)','Bottom Depth (ft)','Mud Type','Additives','Mud Weight (ppg)','Fluids Cost ($)']],
        data=[],
        editable=True,
        column_static_dropdown=[
            {
                'id': 'Mud Type',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['OBM', 'WBM','Other']
                ]
            },
            {
                'id': 'Additives',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['Barite', 'Bentonite', 'Clays', 'Dispersants/Thinners', 'Surfactants', 'Polymers', 'Contaminate Reducers','Other']
                ]
            },
        ],
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
        id='fluids-add-row-button',
        n_clicks=0,
        style={
            'font-family': 'system-ui',
            'color': '#fff',
            'letter-spacing': '0.7px',
            'margin-top':'10px'
        }
    )
])
