import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

tab_1_layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6('Well Trajectory'),
            dcc.Graph(
            id='well-trajectory-dash-graph',
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
            )])
        ]),
        dbc.Col([
            html.Div([
                html.H6('Formations'),
            dcc.Graph(
                id='lithology-dash-graph',
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
            )
            ])
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H6('Drilling Fluids and Pipe Program'),
            dcc.Graph(
                id='pipe-program-graph',
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
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H6('ROP vs. Depth'),
                dcc.Graph(
                    id='drill-bits-dash-graph',
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
               html.H6('Time vs. Depth'),
               dcc.Graph(
                    id='depth-time-graph',
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
        ])
    ]),
    dbc.Row([
        dbc.Col([
           html.Div([
               html.H6('Time vs. Cost'),
               dcc.Graph(
                    id='cost-time-graph',
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
               html.H6('Total Project Cost'),
               dcc.Graph(
                    id='total-cost-graph',
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
        ])
    ])
])