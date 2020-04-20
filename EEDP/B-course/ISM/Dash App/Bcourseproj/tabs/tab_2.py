import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc



tab_2_layout = dbc.Row([
    dbc.Col([
        html.Div([
            # # hidden div for retaining info
            # dcc.Store(id='filename-storage',storage_type='session'),
            html.H6('Well Trajectory'),
            # Well trajectory upload option, and plot
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    html.A('Drag and Drop or Select .csv File (MD, Incl, Az)')
                ]),
                style={
                    # 'width': '100%',
                    # 'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                    'font-family': 'system-ui',
                    'color': '#fff'
                },
                # Allow multiple files to be uploaded
                # multiple=True
            ),

            dcc.Graph(
                id='well-trajectory-graph',
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
            )
        ])
    ]),
    dbc.Col([
        html.Div([
            # dcc.Store(id='lithology-store',storage_type='session'),
            html.H6('Formations'),
            # lithology datatable, button, and plot
            dcc.Graph(
                id='lithology-graph',
                config={
                    'displayModeBar': False,
                    'staticPlot': True
                },
                figure={
                    'data': [],
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
            dash_table.DataTable(
                id='lithology-table',
                columns = [{'name':i,'id':i} for i in ['Layer','Top Depth (ft)','Bottom Depth (ft)','Formation Name','Lithology']],
                data=[],
                editable=True,
                row_deletable=True,
                # style_as_list_view=True,
                style_header={
                    # 'font-family': 'Inspira sans,sans-serif',
                    'font-family': 'system-ui',
                    # 'backgroundColor': 'black',
                    # 'color': '#fff',
                   'font-weight':'bold'
                },
                style_cell={
                    'textAlign': 'center',
                    # 'font-family': 'Inspira sans,sans-serif',
                    'font-family': 'system-ui',
                    # 'backgroundColor': 'black',
                    # 'color': '#fff'
                }
            ),
            html.Button(
                'Add Layer',
                id='lithology-add-row-button', 
                n_clicks=0,
                style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px'
                }
            )
        ])

    ])
])