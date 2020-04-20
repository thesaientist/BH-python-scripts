import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

tab_8_layout=html.Div([
    dbc.Row([
        dbc.Col([
            html.H6('Total Fixed Cost Estimates ($)'),
            dash_table.DataTable(
                id='fixed-cost-table',
                columns = [{'name':'Item','id':'Item','type':'text'},{'name':'Cost','id':'Cost','type':'numeric'}],
                data=[{'Item':item} for item in ['Location','Power, Fuel, Water','Transportation','Rental Equipment','Pipe','Drill Bits','Drilling Fluids','Cement','Logging']],
                editable=False,
                # style_as_list_view=True,
                style_header={
                    'font-family': 'system-ui',
                    'font-weight':'bold'
                },
                style_cell={
                    'textAlign': 'left',
                    'font-family': 'system-ui'
                }
            )
        ]),
        dbc.Col([
            html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([
                            html.Th('Rig Days'),
                            html.Th('Subtotal ($)'),
                            html.Th('Total ($)')
                        ])
                    ]),
                    html.Tbody([
                        html.Tr([
                            html.Td(0, id='rig-days'),
                            html.Td(0, id='subtotal-cost'),
                            html.Td(0, id='total-cost')
                        ])
                    ])
                ],className='custom-table')
            ]
            )
        ])
    ]),
    html.H6('Variable Cost Estimates ($)'),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='var-cost-table',
                columns = [
                    {'name':['','Phase Description'],'id':'Phase Description','type':'text'},
                    {'name':['','Depth'],'id':'Depth','type':'numeric'},
                    {'name':['Time Estimates (days)','Min.'],'id':'Min.','type':'numeric'},
                    {'name':['Time Estimates (days)','Best'],'id':'Best','type':'numeric'},
                    {'name':['Time Estimates (days)','Max.'],'id':'Max.','type':'numeric'},
                    {'name':['Minimum Estimate','Est. Cost ($)'],'id':'Min Est. Cost ($)','type':'numeric'},
                    {'name':['Minimum Estimate','Cumulative Time'],'id':'Min Cumulative Time','type':'numeric'},
                    {'name':['Minimum Estimate','Cumulative Cost'],'id':'Min Cumulative Cost','type':'numeric'},
                    {'name':['Best Estimate','Est. Cost ($)'],'id':'Best Est. Cost ($)','type':'numeric'},
                    {'name':['Best Estimate','Cumulative Time'],'id':'Best Cumulative Time','type':'numeric'},
                    {'name':['Best Estimate','Cumulative Cost'],'id':'Best Cumulative Cost','type':'numeric'},
                    {'name':['Maximum Estimate','Est. Cost ($)'],'id':'Max Est. Cost ($)','type':'numeric'},
                    {'name':['Maximum Estimate','Cumulative Time'],'id':'Max Cumulative Time','type':'numeric'},
                    {'name':['Maximum Estimate','Cumulative Cost'],'id':'Max Cumulative Cost','type':'numeric'},
                ],
                data = [],
                merge_duplicate_headers=True,
                editable=False,
                # style_as_list_view=True,
                style_header={
                    'font-family': 'system-ui',
                    'font-weight':'bold'
                },
                style_cell={
                    'textAlign': 'center',
                    'font-family': 'system-ui'
                }
            )
        ])
    ])
    # html.H4('Rig Days:'),
    # html.H4('Subtotal ($):'),
    # html.H4('Total ($):')
])