import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.plotly as py
import plotly.graph_objs as go
from dash.exceptions import PreventUpdate
import math
import pandas as pd
import numpy as np
from plotly import tools
from tabs import tab_1,tab_2,tab_3,tab_4,tab_5,tab_6,tab_7,tab_8

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# BELOW is a workaround using flask for adding addtional CSS for fixing some dropdown issues
# in Dash Table object
#-------------------------------------------------------------------------------
# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
import os
import flask
css_directory = os.getcwd()
stylesheets = ['fix_issues.css']
static_css_route = '/static/'

@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return flask.send_from_directory(css_directory, stylesheet)

for stylesheet in stylesheets:
    app.css.append_css({"external_url": "/static/{}".format(stylesheet)})
#-------------------------------------------------------------------------------

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div([
    html.H1('Well Planning Application'),
    html.Div([
        dbc.Row([
            dbc.Col([
                'Select a scenario:'
            ]),
            dbc.Col([
                'Add a scenario:'
            ])
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='select-scenario',
                    options=[
                        {'label': 'Baseline', 'value': 'Baseline'},
                        {'label': 'Scenario1', 'value': 'Scenario1'}
                    ],
                    value = 'Baseline',
                    clearable = False
                ),
                dcc.Store(id='stored-scenario-names',storage_type='session')
            ]),
            dbc.Col([
                dcc.Input(id='input-new-scenario'),
                html.Button(
                    'Add',
                    id='add-scenario-button',
                    # n_clicks=0,
                    style={
                        'font-family': 'system-ui',
                        'color': '#000',
                        'letter-spacing': '0.7px',
                        'margin-left': '30px',
                        'border-color':'black'
                    }
                )
            ])
        ])
    ],
    style = {'padding':'10px'}
    ),
    # hidden stores for retaining info
    dcc.Store(id='well-trajectory-filenames',storage_type='session'),
    dcc.Store(id='lithology-store',storage_type='session'),
    dcc.Store(id='drill-bit-store',storage_type='session'),
    dcc.Store(id='drill-tools-store',storage_type='session'),
    dcc.Store(id='automation-store',storage_type='session'),
    dcc.Store(id='cementing-store',storage_type='session'),
    dcc.Store(id='logging-store',storage_type='session'),
    dcc.Store(id='logistics-store',storage_type='session'),
    dcc.Store(id='casing-store',storage_type='session'),
    dcc.Store(id='fluids-store',storage_type='session'),
    # dcc.Store(id='var-cost-store',storage_type='session'),
    dcc.Tabs(
        id="tabs",
        value='tab1', ################################# change tab here to help development
        parent_className = 'custom-tabs',
        className='custom-tabs-container',
        children=[
        dcc.Tab(
            label='Dashboard', value='tab1',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Well Trajectory & Formations',
            value='tab2',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Pipe, Drilling Fluids, & Cement',
            value='tab3',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Drill Bits & Drilling TSA',
            value='tab4',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Cementing',
            value='tab5',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Logging',
            value='tab6',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Rig Logistics',
            value='tab7',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            ),
        dcc.Tab(
            label='Summary AFE',
            value='tab8',
            className = 'custom-tab',
            selected_className='custom-tab--selected'
            )
    ]),
    html.Div(id='tabs-content')
])

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab1':
        return tab_1.tab_1_layout
    elif tab == 'tab2':
        return tab_2.tab_2_layout
    elif tab == 'tab3':
        return tab_3.tab_3_layout
    elif tab == 'tab4':
        return tab_4.tab_4_layout
    elif tab == 'tab5':
        return tab_5.tab_5_layout
    elif tab == 'tab6':
        return tab_6.tab_6_layout
    elif tab == 'tab7':
        return tab_7.tab_7_layout
    elif tab == 'tab8':
        return tab_8.tab_8_layout

# functions for parsing and plotting

def Coordinates(MD,Incl,Az):
    num_entries = len(MD)
    North = [0]
    East = [0]
    VertSect = [0]
    TVD = [0]
    for i in range(1,num_entries):
        newNorth = (((MD[i]-MD[i-1])/2)*(math.sin(Incl[i-1]/57.3)*math.cos(Az[i-1]/57.3)+math.sin(Incl[i]/57.3)*math.cos(Az[i]/57.3)))+North[-1]
        North.append(newNorth)
        newEast = (((MD[i]-MD[i-1])/2)*(math.sin(Incl[i-1]/57.3)*math.sin(Az[i-1]/57.3)+math.sin(Incl[i]/57.3)*math.sin(Az[i]/57.3)))+East[-1]
        East.append(newEast)
        # VertSect.append((newNorth**2+newEast**2)**0.5)
        TVD.append(((MD[i]-MD[i-1])/2)*((math.cos(Incl[i]/57.3)+math.cos(Incl[i-1]/57.3)))+TVD[-1])
    return North, East, TVD

def parse_uploaded_file(filename):
    try:
        df = pd.read_csv(filename)
        North, East, TVD = Coordinates(df['MD'].values,df['Incl'].values,df['Az'].values)
    except Exception as e:
        print(e)
    return North, East, TVD

############### Scenario callbacks ###############

# adding to store when add button is clicked
@app.callback(
    Output('stored-scenario-names','data'),
    [Input('add-scenario-button','n_clicks')],
    [State('stored-scenario-names','data'),
    State('input-new-scenario','value')]
)
def add_scenario(n_clicks,stored_scenarios,new_scenario_name):
    if n_clicks is None:
        raise PreventUpdate
    # defaule if no data
    stored_scenarios = stored_scenarios or [{'label': 'Baseline', 'value': 'Baseline'},{'label': 'Scenario1', 'value': 'Scenario1'}]

    stored_scenarios.append({'label':new_scenario_name, 'value': new_scenario_name})
    return stored_scenarios

# display stored options as dropdown options
@app.callback(
    Output('select-scenario','options'),
    [Input('stored-scenario-names','modified_timestamp')],
    [State('stored-scenario-names','data')]
)
def populate_stored_scenarios(ts,stored_scenarios):
    if ts is None:
        raise PreventUpdate
    stored_scenarios = stored_scenarios or [{'label': 'Baseline', 'value': 'Baseline'},{'label': 'Scenario1', 'value': 'Scenario1'}]
    return stored_scenarios

############### Tab 1 callbacks ###############
# change output of trajectory graph every time the scenario is changed or the stores change
@app.callback(
    Output('well-trajectory-dash-graph', 'figure'),
    [Input('well-trajectory-filenames','modified_timestamp'),
    Input('select-scenario','value')],
    [State('well-trajectory-filenames','data')]
    )
def populate_dash_trajectory(ts, selected_scenario, stored_filenames):
    if ts is None:
        raise PreventUpdate
    stored_filenames = stored_filenames or {}
    if selected_scenario in stored_filenames:
        North, East, TVD = parse_uploaded_file(stored_filenames[selected_scenario])
        trace = go.Scatter3d(
            x=East, y=North, z=TVD,
            marker=dict(
                size=4,
                color=TVD,
                colorscale='Viridis',
            ),
            line=dict(
                color='#1f77b4',
                width=1
            )
        )

        data = [trace]

        layout = dict(
            title=stored_filenames[selected_scenario],
            font=dict(
                family='Inspira sans,sans-serif',
                color='#fff'
            ),
            # width=500,
            # height=500,
            autosize=False,
            scene=dict(
                xaxis=dict(
                    title='East',
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    color='#fff'
                ),
                yaxis=dict(
                    title='North',
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    color='#fff'
                ),
                zaxis=dict(
                    title='TVD',
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    autorange='reversed',
                    color='#fff'
                ),
                camera=dict(
                    up=dict(
                        x=.75,
                        y=.75,
                        z=1
                    ),
                    center=dict(
                        x=0,
                        y=0,
                        z=-.25
                    )
                #     eye=dict( # eye vector determines camera point of view
                #         x=0,
                #         y=0,
                #         z=0,
                # )
                ),
                aspectratio = dict( x=1, y=1, z=.7),
                aspectmode = 'manual'
            ),
                # paper_bgcolor = 'rgba(255,255,255,.5)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
        )
        # theres a bug here that doesn't always populate first tab
        return dict(data=data,layout=layout)
    else:
        raise PreventUpdate

@app.callback(
    Output('lithology-dash-graph', 'figure'),
    [Input('select-scenario','value'),
    Input('lithology-store','data')])
def display_dash_lithology(selected_scenario,rows):
    rows = rows or {}
    if selected_scenario in rows:
        graph_columns = [{'name':i,'id':i} for i in ['Formation Name','Lithology']]
        return {
            'data': [{
                'type': 'heatmap',
                'colorscale': 'Viridis',
                'x': [c['name'] for c in graph_columns],
                'z': [[i,i] for i,row in enumerate(rows[selected_scenario])], # z is data entered in datatable ex. 'z': [['10', '203', '', '', '', '']]
                'y': [i for i,row in enumerate(rows[selected_scenario])],
                'xgap': 5,
                'showscale': False,
                'showlegend': False
            }],
            'layout': go.Layout(
                # title='Formations',
                xaxis={
                    'showticklabels': False,
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False
                },
                yaxis={
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False,
                    'autorange':'reversed'
                },
                annotations=[
                    dict(
                        x=c,
                        y=row.get('Layer', None),
                        text=row.get(c, None),
                        xanchor='center',
                        yanchor='middle',
                        showarrow=False,
                        font=dict(
                            color='white',
                            size=18
                        )
                    )
                    for row in rows[selected_scenario] for c in ['Lithology','Formation Name']
                ],
                margin=go.layout.Margin(
                    l=10,
                    r=10,
                    b=10,
                    t=10
                ),
                height = 300,
                # paper_bgcolor = 'rgba(255,255,255,.5)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'

            )
        }
    else:
        raise PreventUpdate

@app.callback(
    Output('drill-bits-dash-graph', 'figure'),
    [Input('drill-bit-store', 'data'),
    Input('select-scenario','value')])
def rop_dash_graph(rows, scenario):
    rows = rows or {}
    if scenario in rows:
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        x3 = []
        y3 = []
        for row in rows[scenario]:
            x1.append(row['ROPP10'])
            x1.append(row['ROPP10'])
            y1.append(row['Top Depth (ft)'])
            y1.append(row['Bottom Depth (ft)'])

            x2.append(row['ROPP90'])
            x2.append(row['ROPP90'])
            y2.append(row['Top Depth (ft)'])
            y2.append(row['Bottom Depth (ft)'])

            x3.append(row['ROPP50'])
            x3.append(row['ROPP50'])
            y3.append(row['Top Depth (ft)'])
            y3.append(row['Bottom Depth (ft)'])
        return dict(
            data= [
                go.Scatter(
                    x=x1,
                    y=y1,
                    name = 'P10'
                ),
                go.Scatter(
                    x=x2,
                    y=y2,
                    name = 'P50'
                ),
                go.Scatter(
                    x=x3,
                    y=y3,
                    name = 'P90'
                )
            ],
            layout=dict(
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)',
                xaxis = dict(
                    color='#fff',
                    showgrid=False,
                    title='ROP (ft/hr)'
                ),
                yaxis = dict(
                    color='#fff',
                    showgrid=False,
                    autorange='reversed',
                    title='Measured Depth'
                )
            )
        )
    else:
        raise PreventUpdate

@app.callback(
    Output('pipe-program-graph','figure'),
    [Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('select-scenario','value')]
)
def update_dash_casing(fluids_store,casing_store,scenario):
    try:
        fluids_table = fluids_store[scenario]
        casing_table = casing_store[scenario]
        graph_columns = [{'name':i,'id':i} for i in ['Mud Weight (ppg)','Mud Type']]
        x = []
        y = []
        for i,entry in enumerate(casing_table):
            if entry['Outer Diameter (in)'] == '':
                casing_table[i]['Outer Diameter (in)'] = 0
        for i,row in enumerate(casing_table):
            x.append(row['Outer Diameter (in)']/2)
            x.append(row['Outer Diameter (in)']/2)
            x.append(row['Outer Diameter (in)']/2)
            x.append(row['Outer Diameter (in)']*-1/2)
            x.append(row['Outer Diameter (in)']*-1/2)
            x.append(row['Outer Diameter (in)']*-1/2)
            y.append(casing_table[0]['Top Depth (ft)'])
            y.append(row['Set Depth (ft)'])
            y.append(None)
            y.append(casing_table[0]['Top Depth (ft)'])
            y.append(row['Set Depth (ft)'])
            y.append(None)

        trace1 = go.Scatter(
            x=x,
            y=y
        )
        for i,entry in enumerate(fluids_table):
            if entry['Top Depth (ft)'] == '' and i>0:
                fluids_table[i]['Top Depth (ft)'] = fluids_table[i-1]['Top Depth (ft)']
            if entry['Top Depth (ft)'] =='' and i==0:
                fluids_table[i]['Top Depth (ft)'] = 0
            if entry['Bottom Depth (ft)'] =='' and i>0:
                fluids_table[i]['Bottom Depth (ft)'] = fluids_table[i-1]['Bottom Depth (ft)']
            if entry['Bottom Depth (ft)'] =='' and i==0:
                fluids_table[i]['Bottom Depth (ft)'] = 1
        trace2 = {
            'type': 'heatmap',
            'colorscale': 'Viridis',
            'x': [c['name'] for c in graph_columns],
            'z': [[i,i] for i,row in enumerate(fluids_table)], # z is data entered in datatable ex. 'z': [['10', '203', '', '', '', '']]
            'y': [(row.get('Top Depth (ft)',0)+row.get('Bottom Depth (ft)',0))/2 for row in fluids_table],
            'xgap': 5,
            'showscale': False,
            'showlegend': False,
            'hoverinfo': 'none'
        }

        fig = tools.make_subplots(rows=1, cols=2, shared_yaxes=True, print_grid=False)

        fig.append_trace(trace1, 1, 1)
        fig.append_trace(trace2, 1, 2)

        fig['layout'].update(
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            xaxis={
                'showticklabels': False,
                'title':'Diameter (ft)',
                'showgrid': False,
                'zeroline': False,
                'color':'#fff'
            },
            yaxis={
                'showgrid': False,
                'zeroline': False,
                'autorange':'reversed',
                'color':'#fff',
                'title':'Depth (ft)'
            },
            xaxis2={
                'ticks':'',
                'showgrid': False,
                'zeroline': False,
                'color':'#fff'
            },
            yaxis2={
                'showgrid': False,
                'zeroline': False,
                'autorange':'reversed',
                'color':'#fff',
                'title':'Depth (ft)'
            },
            annotations=[
                dict(
                    x=c,
                    y=(row.get('Top Depth (ft)',0)+row.get('Bottom Depth (ft)',0))/2 ,
                    xref='x2',
                    text=row.get(c, None),
                    xanchor='center',
                    yanchor='middle',
                    showarrow=False,
                    font=dict(
                        color='white',
                        size=18
                    )
                )
                for row in fluids_table for c in ['Mud Weight (ppg)','Mud Type']
            ],
            )
        return fig
    except:
        raise PreventUpdate

# function definition for collecting AFE data (used several times in callbacks)
def collect_afe_data(data, casing, cementing, drillbit, fluids, logging, logistics, scenario):
    # Est. Mobilization time (already in days)
    try:
        data.extend([{
            'Phase Description':'Mob',
            'Depth 1':0,
            'Depth 2':0,
            'Order':0,
            'Min.':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Best':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Max.':max(0.1, round(row['Mobilization/Demobilization (days)'],1))
            } for row in logistics[scenario]])
    except:
        pass

    # Est. Casing/Cementing time (in hours, convert to days)
    try:
        data.extend([{
            'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
            'Depth 1':row['Top Depth (ft)'],
            'Depth 2':row['Set Depth (ft)'],
            'Order':3,
            'Min.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1))
        } for row in cementing[scenario]])
    except:
        pass

    # Est ROP drilling time (drillbit table, already calculated in days)
    try:
        data.extend([{
            'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth 1':row['Top Depth (ft)'],
            'Depth 2':row['Bottom Depth (ft)'],
            'Order':1,
            'Min.':row['esttimeP10'],
            'Best':row['esttimeP50'],
            'Max.':row['esttimeP90']
        } for row in drillbit[scenario]])
    except:
        pass

    # Est. Tripping Time (also from drillbit table, convert from hours to days)
    try:
        data.extend([{
            'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth 1':row['Top Depth (ft)'],
            'Depth 2':row['Bottom Depth (ft)'],
            'Order':4,
            'Min.':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Trip Time (hr)']/24,1))
            } for row in drillbit[scenario]])
    except:
        pass

    # Est. Non-productive logging time (calculate in days based on type of logging)
    # includes logging time if wireline, otherwise only est. non-productive time
    try:
        # loop through logging activities and estimate the NPT and output line in AFE
        for row in logging[scenario]:
            if row['Logging Method'] == 'Wireline':
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth 1':row['Top Depth (ft)'],
                    'Depth 2':row['Bottom Depth (ft)'],
                    'Order':2,
                    'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                    }])
            else:
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth 1':row['Top Depth (ft)'],
                    'Depth 2':row['Bottom Depth (ft)'],
                    'Order':2,
                    'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                    }])
    except:
        pass

    # convert to Pandas DataFrame and organize in an AFE order
    dvd_data = {'time':[], 'depth':[]}     # dictionary to store values for plot of days v depth
    data_df = pd.DataFrame(data)
    afe_df = data_df.sort_values(by=['Depth 2', 'Order'])
    for index, row in afe_df.iterrows():
        if index==0:
            dvd_data['time'].append(0)
            dvd_data['depth'].append(row['Depth 1'])
        last_time = dvd_data['time'][-1]
        dvd_data['time'].append(last_time + row['Best'])
        dvd_data['depth'].append(row['Depth 2'])

    # add 'Demob' at the end of afe_df and dvd_data
    try:
        mob_index = afe_df.index[afe_df['Phase Description'] == 'Mob'].tolist()
        mob_row = afe_df.loc[mob_index]
        mob_row['Phase Description'] = 'Demob'
        mob_row['Order'] = 6
        latest_depth = afe_df.iloc[-1]['Depth 2']
        mob_row['Depth 1'] = latest_depth
        mob_row['Depth 2'] = latest_depth
        afe_df = afe_df.append(mob_row, ignore_index = True)

        last_time = dvd_data['time'][-1]
        dvd_data['time'].append(last_time + afe_df.iloc[-1]['Best'])
        dvd_data['depth'].append(afe_df.iloc[-1]['Depth 2'])
    except:
        pass

    # calculate cumulative time and cost (in days and $)
    try:
        rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
        p90cost = []
        p50cost = []
        p10cost = []
        p90cumtime = []
        p50cumtime = []
        p10cumtime = []
        p90cumcost = []
        p50cumcost = []
        p10cumcost = []
        for i,entry in afe_df.iterrows():
            p10cost.append(rig_rate*entry['Min.'])
            p50cost.append(rig_rate*entry['Best'])
            p90cost.append(rig_rate*entry['Max.'])

            if i==0:
                p10cumtime.append(entry['Min.'])
                p50cumtime.append(entry['Best'])
                p90cumtime.append(entry['Max.'])
            else:
                p10cumtime.append(entry['Min.'] + p10cumtime[-1])
                p50cumtime.append(entry['Best'] + p50cumtime[-1])
                p90cumtime.append(entry['Max.'] + p90cumtime[-1])

            if i==0:
                p90cumcost.append(p90cost[i])
                p50cumcost.append(p50cost[i])
                p10cumcost.append(p10cost[i])
            else:
                p90cumcost.append(p90cost[i] + p90cumcost[-1])
                p50cumcost.append(p50cost[i] + p50cumcost[-1])
                p10cumcost.append(p10cost[i] + p10cumcost[-1])
        afe_df['Min Est. Cost ($)'] = p10cost
        afe_df['Best Est. Cost ($)'] = p50cost
        afe_df['Max Est. Cost ($)'] = p90cost
        afe_df['Min Cumulative Cost'] = p10cumcost
        afe_df['Best Cumulative Cost'] = p50cumcost
        afe_df['Max Cumulative Cost'] = p90cumcost
        afe_df['Min Cumulative Time'] = p10cumtime
        afe_df['Best Cumulative Time'] = p50cumtime
        afe_df['Max Cumulative Time'] = p90cumtime
    except:
        pass

    return afe_df, dvd_data

@app.callback(
    Output('depth-time-graph','figure'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def update_depth_time(logistics,fluids,casing,drillbit,cementing,logging,selected_scenario):
    # try/except prevents error when launching the app at which point no data is available for update
    try:
        scenarios = list(logistics.keys()) or []
        scenario_data = {}
        for scenario in scenarios:
            scenario_data[scenario] = {}
            data = []

            # call collect_afe_data function for populating the list of lists 'data'
            afe_df, dvd_data = collect_afe_data(data, casing, cementing, drillbit, fluids, logging, logistics, scenario)
            scenario_data[scenario]['time'] = dvd_data['time']
            scenario_data[scenario]['depth'] = dvd_data['depth']

    except:
        raise PreventUpdate
    try:
        return dict(
                        data= [
                            go.Scatter(
                                x=scenario_data[scenario]['time'],
                                y=scenario_data[scenario]['depth'],
                                name=scenario
                            ) for scenario in scenarios
                        ],
                        layout=dict(
                            paper_bgcolor = 'rgba(0,0,0,0)',
                            plot_bgcolor = 'rgba(0,0,0,0)',
                            xaxis = dict(
                                color='#fff',
                                showgrid=False,
                                title='Time (days)'
                            ),
                            yaxis = dict(
                                color='#fff',
                                showgrid=False,
                                autorange='reversed',
                                title='Measured Depth (ft)'
                            )
                        )
                    )
    except:
        raise PreventUpdate

@app.callback(
    Output('cost-time-graph','figure'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def update_cost_time(logistics,fluids,casing,drillbit,cementing,logging,selected_scenario):
    # try/except prevents error when launching the app at which point no data is available for update
    try:
        scenarios = list(logistics.keys())
        scenario_data = {}
        for scenario in scenarios:
            scenario_data[scenario] = {}
            data = []
            # Est. Cementing time
            try:
                data.extend([{
                    'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
                    'Depth':row['Set Depth (ft)'],
                    'Min.':row['Est. Cementing Time (hr)'],
                    'Best':row['Est. Cementing Time (hr)'],
                    'Max.':row['Est. Cementing Time (hr)']
                } for row in cementing[scenario]])
            except:
                pass

            # Est ROP drilling time (drillbit table)
            try:
                data.extend([{
                    'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':row['esttimeP10'],
                    'Best':row['esttimeP50'],
                    'Max.':row['esttimeP90']
                } for row in drillbit[scenario]])
            except:
                pass

            # Est. Tripping Time (also from drillbit table)
            try:
                data.extend([{
                    'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':row['Trip Time (hr)'],
                    'Best':row['Trip Time (hr)'],
                    'Max.':row['Trip Time (hr)']
                    } for row in drillbit[scenario]])
            except:
                pass

            # Est. Non-productive logging time (calculate in days based on type of logging)
            # includes logging time if wireline, otherwise only est. non-productive time
            try:
                # loop through logging activities and estimate the NPT and output line in AFE
                for row in logging[scenario]:
                    if row['Logging Method'] == 'Wireline':
                        data.extend([{
                            'Phase Description':'Logging: '+row['Logging Activity'],
                            'Depth':row['Bottom Depth (ft)'],
                            'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                            'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                            'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                            }])
                    else:
                        data.extend([{
                            'Phase Description':'Logging: '+row['Logging Activity'],
                            'Depth':row['Bottom Depth (ft)'],
                            'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                            'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                            'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                            }])
            except:
                pass

            try:
                rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
                for i,entry in enumerate(data):
                    data[i]['Min Est. Cost ($)'] = rig_rate*entry['Min.']
                    data[i]['Best Est. Cost ($)'] = rig_rate*entry['Best']
                    data[i]['Max Est. Cost ($)'] = rig_rate*entry['Max.']

                    if i==0:
                        data[i]['Min Cumulative Time'] = entry['Min.']
                        data[i]['Best Cumulative Time'] = entry['Best']
                        data[i]['Max Cumulative Time'] = entry['Max.']
                    else:
                        data[i]['Min Cumulative Time'] = entry['Min.'] + data[i-1]['Min Cumulative Time']
                        data[i]['Best Cumulative Time'] = entry['Best'] + data[i-1]['Best Cumulative Time']
                        data[i]['Max Cumulative Time'] = entry['Max.'] + data[i-1]['Max Cumulative Time']

                    if i==0:
                        data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)']
                        data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)']
                        data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)']
                    else:
                        data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)'] + data[i-1]['Min Cumulative Cost']
                        data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)'] + data[i-1]['Best Cumulative Cost']
                        data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)'] + data[i-1]['Max Cumulative Cost']
            except:
                pass
            try:
                data_df = pd.DataFrame(data)
                data_df = data_df.sort_values(by=['Depth'])
                data_df['Best'] = data_df['Best'].cumsum()
                data_df['Best Cumulative Cost'] = data_df['Best Est. Cost ($)'].cumsum()
                scenario_data[scenario]['time'] = data_df['Best']
                scenario_data[scenario]['cost'] = data_df['Best Cumulative Cost']
            except:
                raise PreventUpdate
    except:
        raise PreventUpdate
    try:
        return dict(
                        data= [
                            go.Scatter(
                                x=scenario_data[scenario]['time'],
                                y=scenario_data[scenario]['cost'],
                                name=scenario
                            ) for scenario in scenarios
                        ],
                        layout=dict(
                            paper_bgcolor = 'rgba(0,0,0,0)',
                            plot_bgcolor = 'rgba(0,0,0,0)',
                            xaxis = dict(
                                color='#fff',
                                showgrid=False,
                                title='Time (days)'
                            ),
                            yaxis = dict(
                                color='#fff',
                                showgrid=False,
                                autorange='reversed',
                                title='Cost ($)'
                            )
                        )
                    )
    except:
        raise PreventUpdate
@app.callback(
    Output('total-cost-graph','figure'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def update_cost_total(logistics,fluids,casing,drillbit,cementing,logging,selected_scenario):
    # try/except prevents error when launching the app at which point no data is available for update
    try:
        scenarios = list(logistics.keys())
        scenario_data = {}
        for scenario in scenarios:
            scenario_data[scenario] = {}
            data = []
            # Est. Cementing time
            try:
                data.extend([{
                    'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
                    'Depth':row['Set Depth (ft)'],
                    'Min.':row['Est. Cementing Time (hr)'],
                    'Best':row['Est. Cementing Time (hr)'],
                    'Max.':row['Est. Cementing Time (hr)']
                } for row in cementing[scenario]])
            except:
                pass

            # Est ROP drilling time (drillbit table)
            try:
                data.extend([{
                    'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':row['esttimeP10'],
                    'Best':row['esttimeP50'],
                    'Max.':row['esttimeP90']
                } for row in drillbit[scenario]])
            except:
                pass

            # Est. Tripping Time (also from drillbit table)
            try:
                data.extend([{
                    'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':row['Trip Time (hr)'],
                    'Best':row['Trip Time (hr)'],
                    'Max.':row['Trip Time (hr)']
                    } for row in drillbit[scenario]])
            except:
                pass

            # Est. Non-productive logging time (calculate in days based on type of logging)
            # includes logging time if wireline, otherwise only est. non-productive time
            try:
                # loop through logging activities and estimate the NPT and output line in AFE
                for row in logging[scenario]:
                    if row['Logging Method'] == 'Wireline':
                        data.extend([{
                            'Phase Description':'Logging: '+row['Logging Activity'],
                            'Depth':row['Bottom Depth (ft)'],
                            'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                            'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                            'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                            }])
                    else:
                        data.extend([{
                            'Phase Description':'Logging: '+row['Logging Activity'],
                            'Depth':row['Bottom Depth (ft)'],
                            'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                            'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                            'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                            }])
            except:
                pass

            try:
                rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
                for i,entry in enumerate(data):
                    data[i]['Min Est. Cost ($)'] = rig_rate*entry['Min.']
                    data[i]['Best Est. Cost ($)'] = rig_rate*entry['Best']
                    data[i]['Max Est. Cost ($)'] = rig_rate*entry['Max.']

                    if i==0:
                        data[i]['Min Cumulative Time'] = entry['Min.']
                        data[i]['Best Cumulative Time'] = entry['Best']
                        data[i]['Max Cumulative Time'] = entry['Max.']
                    else:
                        data[i]['Min Cumulative Time'] = entry['Min.'] + data[i-1]['Min Cumulative Time']
                        data[i]['Best Cumulative Time'] = entry['Best'] + data[i-1]['Best Cumulative Time']
                        data[i]['Max Cumulative Time'] = entry['Max.'] + data[i-1]['Max Cumulative Time']

                    if i==0:
                        data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)']
                        data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)']
                        data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)']
                    else:
                        data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)'] + data[i-1]['Min Cumulative Cost']
                        data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)'] + data[i-1]['Best Cumulative Cost']
                        data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)'] + data[i-1]['Max Cumulative Cost']
            except:
                pass
            try:
                data_df = pd.DataFrame(data)
                scenario_data[scenario]['min_total'] = sum(data_df['Min Est. Cost ($)'])
                scenario_data[scenario]['best_total'] = sum(data_df['Best Est. Cost ($)'])
                scenario_data[scenario]['max_total'] = sum(data_df['Max Est. Cost ($)'])

            except:
                raise PreventUpdate
    except:
        raise PreventUpdate
    try:
        return dict(
                    data= [
                        go.Bar(
                            x=['P10','P50','P90'],
                            y=[scenario_data[scenario]['min_total'],scenario_data[scenario]['best_total'],scenario_data[scenario]['max_total']],
                            name=scenario
                        ) for scenario in scenarios],
                    layout=dict(
                        # showlegend=False,
                        paper_bgcolor = 'rgba(0,0,0,0)',
                        plot_bgcolor = 'rgba(0,0,0,0)',
                        xaxis = dict(
                            color='#fff',
                            showgrid=False,
                            title='Estimate'
                        ),
                        yaxis = dict(
                            color='#fff',
                            showgrid=False,
                            title='Cost ($)'
                        )
                    )
                )
    except:
        raise PreventUpdate

############### Tab 2 callbacks ###############

# well trajectory side

# update store when things are "uploaded"
@app.callback(
    Output('well-trajectory-filenames','data'),
    [Input('upload-data','filename')],
    [State('select-scenario','value'),
    State('well-trajectory-filenames','data')]
    )
def save_filename(new_filename, selected_scenario, stored_filenames):
    if new_filename is None:
        raise PreventUpdate
    stored_filenames = stored_filenames or {}
    stored_filenames[selected_scenario] = new_filename
    return stored_filenames

# display graph when store or scenario are changed
@app.callback(Output('well-trajectory-graph', 'figure'),
              [Input('well-trajectory-filenames','modified_timestamp'),
              Input('select-scenario','value')],
              [State('well-trajectory-filenames','data')])
def populate_graph(ts,selected_scenario,stored_filenames):
    if ts is None:
        raise PreventUpdate
    stored_filenames = stored_filenames or {}
    if selected_scenario in stored_filenames:
        North, East, TVD = parse_uploaded_file(stored_filenames[selected_scenario])
        trace = go.Scatter3d(
            x=East, y=North, z=TVD,
            marker=dict(
                size=4,
                color=TVD,
                colorscale='Viridis',
            ),
            line=dict(
                color='#1f77b4',
                width=1
            )
        )

        data = [trace]

        layout = dict(
            title=stored_filenames[selected_scenario],
            font=dict(
                family='Inspira sans,sans-serif',
                color='#fff'
            ),
            # width=500,
            # height=500,
            autosize=False,
            scene=dict(
                xaxis=dict(
                    title='East',
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    color='#fff'
                ),
                yaxis=dict(
                    title='North',
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    color='#fff'
                ),
                zaxis=dict(
                    title='TVD',
                    gridcolor='rgb(255, 255, 255)',
                    zerolinecolor='rgb(255, 255, 255)',
                    showbackground=True,
                    backgroundcolor='rgb(230, 230,230)',
                    autorange='reversed',
                    color='#fff'
                ),
                camera=dict(
                    up=dict(
                        x=.75,
                        y=.75,
                        z=1
                    ),
                    center=dict(
                        x=0,
                        y=0,
                        z=-.25
                    )
                #     eye=dict( # eye vector determines camera point of view
                #         x=0,
                #         y=0,
                #         z=0,
                # )
                ),
                aspectratio = dict( x=1, y=1, z=.7),
                aspectmode = 'manual'
            ),
                # paper_bgcolor = 'rgba(255,255,255,.5)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
        )
        return dict(data=data,layout=layout)
    else:
        raise PreventUpdate


# lithology side

# updates table when rows are added

@app.callback(
    Output('lithology-table','data'),
    [Input('lithology-add-row-button','n_clicks')],
    [State('lithology-store','data'),
    State('select-scenario','value')]
)
def update_lithology_store(n_clicks,store,scenario):
    store = store or {}
    if n_clicks >0:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Layer','Top Depth (ft)','Bottom Depth (ft)','Formation Name','Lithology']})
            store[scenario][-1]['Layer'] = len(store[scenario])-1
        else:
            store[scenario] = [{c: '' for c in ['Layer','Top Depth (ft)','Bottom Depth (ft)','Formation Name','Lithology']}]
            store[scenario][-1]['Layer'] = 0
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

@app.callback(
    Output('lithology-store','data'),
    [Input('lithology-table','data')],
    [State('select-scenario','value'),
    State('lithology-store','data')]
)
def update_lithology_table(table,scenario,store):
    store = store or {}
    if table:
        for i,entry in enumerate(table):
            table[i]['Layer'] = i
        store[scenario] = table
    return store

@app.callback(
    Output('lithology-graph', 'figure'),
    [Input('lithology-table', 'data')])
def display_output(rows):
    if rows:
        graph_columns = [{'name':i,'id':i} for i in ['Formation Name','Lithology']]
        return {
            'data': [{
                'type': 'heatmap',
                'colorscale': 'Viridis',
                'x': [c['name'] for c in graph_columns],
                'z': [[i,i] for i,row in enumerate(rows)], # z is data entered in datatable ex. 'z': [['10', '203', '', '', '', '']]
                'y': [i for i,row in enumerate(rows)],
                'xgap': 5,
                'showscale': False,
                'showlegend': False
            }],
            'layout': go.Layout(
                # title='Formations',
                height=300,
                xaxis={
                    'showticklabels': False,
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False
                },
                yaxis={
                    'ticks': '',
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False,
                    'autorange':'reversed'
                },
                annotations=[
                    dict(
                        x=c,
                        y=row.get('Layer', None),
                        text=row.get(c, None),
                        xanchor='center',
                        yanchor='middle',
                        showarrow=False,
                        font=dict(
                            color='white',
                            size=18
                        )
                    )
                    for row in rows for c in ['Lithology','Formation Name']
                ],
                margin=go.layout.Margin(
                    l=10,
                    r=10,
                    b=10,
                    t=10
                ),
                # paper_bgcolor = 'rgba(255,255,255,.5)',
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'

            )
        }
    else:
        raise PreventUpdate


############### Tab 3 callbacks ###############
@app.callback(
    Output('drill-casing-table','data'),
    [Input('casing-add-row-button','n_clicks')],
    [State('casing-store','data'),
    State('select-scenario','value')]
)
def update_casing_store(n_clicks,store,scenario):
    store = store or {}
    if n_clicks >0:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Top Depth (ft)','Set Depth (ft)','Hold Size (in)','Casing/Pipe Section','Outer Diameter (in)','Inner Diameter (in)','Pipe Cost ($)']})
        else:
            store[scenario] = [{c: '' for c in ['Top Depth (ft)','Set Depth (ft)','Hold Size (in)','Casing/Pipe Section','Outer Diameter (in)','Inner Diameter (in)','Pipe Cost ($)']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

@app.callback(
    Output('casing-store','data'),
    [Input('drill-casing-table','data')],
    [State('select-scenario','value'),
    State('casing-store','data')]
)
def update_casing_table(table,scenario,store):
    store = store or {}
    if table:
        store[scenario] = table
    return store

@app.callback(
    Output('drill-fluids-table','data'),
    [Input('fluids-add-row-button','n_clicks')],
    [State('fluids-store','data'),
    State('select-scenario','value')]
)
def update_fluids_store(n_clicks,store,scenario):
    store = store or {}
    if n_clicks >0:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Top Depth (ft)','Bottom Depth (ft)','Mud Type','Additives','Mud Weight (ppg)','Fluids Cost ($)']})
        else:
            store[scenario] = [{c: '' for c in ['Top Depth (ft)','Bottom Depth (ft)','Mud Type','Additives','Mud Weight (ppg)','Fluids Cost ($)']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

@app.callback(
    Output('fluids-store','data'),
    [Input('drill-fluids-table','data')],
    [State('select-scenario','value'),
    State('fluids-store','data')]
)
def update_fluids_table(table,scenario,store):
    store = store or {}
    if table:
        store[scenario] = table
    return store

@app.callback(
    Output('pipe-graph','figure'),
    [Input('drill-fluids-table','data'),
    Input('drill-casing-table', 'data')]
)
def update_pipe_graph(fluids_table,casing_table):
    graph_columns = [{'name':i,'id':i} for i in ['Mud Weight (ppg)','Mud Type']]
    x = []
    y = []
    for i,entry in enumerate(casing_table):
        if entry['Outer Diameter (in)'] == '':
            casing_table[i]['Outer Diameter (in)'] = 0
    for i,row in enumerate(casing_table):
        x.append(row['Outer Diameter (in)']/2)
        x.append(row['Outer Diameter (in)']/2)
        x.append(row['Outer Diameter (in)']/2)
        x.append(row['Outer Diameter (in)']*-1/2)
        x.append(row['Outer Diameter (in)']*-1/2)
        x.append(row['Outer Diameter (in)']*-1/2)
        y.append(casing_table[0]['Top Depth (ft)'])
        y.append(row['Set Depth (ft)'])
        y.append(None)
        y.append(casing_table[0]['Top Depth (ft)'])
        y.append(row['Set Depth (ft)'])
        y.append(None)

    trace1 = go.Scatter(
        x=x,
        y=y
    )
    for i,entry in enumerate(fluids_table):
        if entry['Top Depth (ft)'] == '' and i>0:
            fluids_table[i]['Top Depth (ft)'] = fluids_table[i-1]['Top Depth (ft)']
        if entry['Top Depth (ft)'] =='' and i==0:
            fluids_table[i]['Top Depth (ft)'] = 0
        if entry['Bottom Depth (ft)'] =='' and i>0:
            fluids_table[i]['Bottom Depth (ft)'] = fluids_table[i-1]['Bottom Depth (ft)']
        if entry['Bottom Depth (ft)'] =='' and i==0:
            fluids_table[i]['Bottom Depth (ft)'] = 1

    fig = tools.make_subplots(rows=1, cols=2, shared_yaxes=True, print_grid=False)

    fig.append_trace(trace1, 1, 1)
    trace2 = {
        'type': 'heatmap',
        'colorscale': 'Viridis',
        'x': [c['name'] for c in graph_columns],
        'z': [[i,i] for i,row in enumerate(fluids_table)], # z is data entered in datatable ex. 'z': [['10', '203', '', '', '', '']]
        'y': [(row.get('Top Depth (ft)',0)+row.get('Bottom Depth (ft)',0))/2 for row in fluids_table],
        # 'dy': [row.get('Bottom Depth (ft)',0) for row in fluids_table],
        # 'y':fig['layout']['yaxis']['tickvals'],
        'xgap': 5,
        'showscale': False,
        # 'showlegend': False,  # this property doesn't exist for heatmap object, so it was giving an error
        'hoverinfo': 'none'
    }
    fig.append_trace(trace2, 1, 2)
    fig['layout'].update(
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        xaxis={
            'showticklabels': False,
            'title':'Diameter (ft)',
            'showgrid': False,
            'zeroline': False,
            'color':'#fff'
        },
        yaxis={
            'showgrid': False,
            'zeroline': False,
            'autorange':'reversed',
            'color':'#fff',
            'title':'Depth (ft)'
        },
        xaxis2={
            'ticks':'',
            'showgrid': False,
            'zeroline': False,
            'color':'#fff'
        },
        yaxis2={
            'showgrid': False,
            'zeroline': False,
            'autorange':'reversed',
            'color':'#fff',
            'title':'Depth (ft)'
        },
        annotations=[
            dict(
                x=c,
                y=(row.get('Top Depth (ft)',0)+row.get('Bottom Depth (ft)',0))/2 ,
                xref='x2',
                text=row.get(c, None),
                xanchor='center',
                yanchor='middle',
                showarrow=False,
                font=dict(
                    color='white',
                    size=18
                )
            )
            for row in fluids_table for c in ['Mud Weight (ppg)','Mud Type']
        ],
        )
    return fig

############### Tab 4 callbacks ###############
# adds a row to table when add row is clicked
@app.callback(
    Output('drill-bits-table','data'),
    [Input('drill-bit-add-row-button','n_clicks'),
    Input('drill-bit-add-row-button','n_clicks_timestamp'),
    Input('drill-bit-calculate-button','n_clicks'),
    Input('drill-bit-calculate-button','n_clicks_timestamp')],
    [State('drill-bit-store','data'),
    State('select-scenario','value')]
)
def update_drill_bit_table(n_clicks,add_row_timestamp,n_click_calc,calc_ts,store,scenario):
    store = store or {}
    if n_clicks >0 and add_row_timestamp>calc_ts:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Top Depth (ft)','Bottom Depth (ft)','Type','Diameter (in)','ROPP10','ROPP50','ROPP90','esttimeP10','esttimeP50','esttimeP90','Bit Cost ($)','Trip Time (hr)']})
        else:
            store[scenario] = [{c: '' for c in ['Top Depth (ft)','Bottom Depth (ft)','Type','Diameter (in)','ROPP10','ROPP50','ROPP90','esttimeP10','esttimeP50','esttimeP90','Bit Cost ($)','Trip Time (hr)']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

# update store when table is edited
@app.callback(
    Output('drill-bit-store','data'),
    [Input('drill-bits-table','data')],
    [State('select-scenario','value'),
    State('drill-bit-store','data')]
)
def update_drill_bit_store(table,scenario,store):
    store = store or {}
    if table:
        # calculate estimated time in days based on P10, P50 and P90 ROP estimates
        for i,entry in enumerate(table):
            if all(not type(entry[col]) is str for col in ['Top Depth (ft)','Bottom Depth (ft)','ROPP10']):
                table[i]['esttimeP10'] = max(0.1,round((entry['Bottom Depth (ft)']-entry['Top Depth (ft)'])/entry['ROPP10']/24,1))
            if all(not type(entry[col]) is str for col in ['Bottom Depth (ft)','Top Depth (ft)','ROPP90']):
                table[i]['esttimeP90'] = max(0.1,round((entry['Bottom Depth (ft)']-entry['Top Depth (ft)'])/entry['ROPP90']/24,1))
            if all(not type(entry[col]) is str for col in ['Bottom Depth (ft)','Top Depth (ft)','ROPP50']):
                table[i]['esttimeP50'] = max(0.1,round((entry['Bottom Depth (ft)']-entry['Top Depth (ft)'])/entry['ROPP50']/24,1))

        store[scenario] = table
    return store

@app.callback(
    Output('drill-bits-graph', 'figure'),
    [Input('drill-bits-table', 'data')])
def drill_bit_graph(rows):
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
    for row in rows:
        x1.append(row['ROPP10'])
        x1.append(row['ROPP10'])
        x1.append(row['ROPP10'])
        y1.append(row['Top Depth (ft)'])
        y1.append(row['Bottom Depth (ft)'])
        y1.append(None)

        x2.append(row['ROPP90'])
        x2.append(row['ROPP90'])
        x2.append(row['ROPP90'])
        y2.append(row['Top Depth (ft)'])
        y2.append(row['Bottom Depth (ft)'])
        y2.append(None)

        x3.append(row['ROPP50'])
        x3.append(row['ROPP50'])
        x3.append(row['ROPP50'])
        y3.append(row['Top Depth (ft)'])
        y3.append(row['Bottom Depth (ft)'])
        y3.append(None)
    return dict(
        data= [
            go.Scatter(
                x=x1,
                y=y1,
                name = 'P10'
            ),
            go.Scatter(
                x=x2,
                y=y2,
                name = 'P90'
            ),
            go.Scatter(
                x=x3,
                y=y3,
                name = 'P50'
            )
        ],
        layout=dict(
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(
                color='#fff',
                showgrid=False,
                title='ROP (ft/hr)'
            ),
            yaxis = dict(
                color='#fff',
                showgrid=False,
                autorange='reversed',
                title='Measured Depth'
            )
        )
    )

# add row to table when add row is clicked
@app.callback(
    Output('drill-tools-table','data'),
    [Input('drill-tool-add-row-button','n_clicks'),
    Input('drill-tool-calculate-button','n_clicks'),
    Input('drill-tool-add-row-button','n_clicks_timestamp'),
    Input('drill-tool-calculate-button','n_clicks_timestamp')],
    [State('drill-tools-store','data'),
    State('select-scenario','value')]
)
def update_drill_tool_table(n_clicks,n_clicks_calc,row_ts,calc_ts,store,scenario):
    store = store or {}
    # print(row_ts,calc_ts)
    if n_clicks >0 and row_ts>calc_ts:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Top Depth (ft)','Bottom Depth (ft)','Tool/Service Type','Rental Cost ($/day)','esttimeP10','esttimeP50','esttimeP90','estcostP10','estcostP50','estcostP90']})
        else:
            store[scenario] = [{c: '' for c in ['Top Depth (ft)','Bottom Depth (ft)','Tool/Service Type','Rental Cost ($/day)','esttimeP10','esttimeP50','esttimeP90','estcostP10','estcostP50','estcostP90']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

# update store when table is edited
@app.callback(
    Output('drill-tools-store','data'),
    [Input('drill-tools-table','data')],
    [State('select-scenario','value'),
    State('drill-tools-store','data')]
)
def update_drill_tool_store(table,scenario,store):
    store = store or {}
    if table:
        for i,entry in enumerate(table):
            if all(not type(entry[col]) is str for col in ['Rental Cost ($/day)','esttimeP10']):
                table[i]['estcostP10'] = entry['Rental Cost ($/day)']*entry['esttimeP10']
            if all(not type(entry[col]) is str for col in ['Rental Cost ($/day)','esttimeP50']):
                table[i]['estcostP50'] = entry['Rental Cost ($/day)']*entry['esttimeP50']
            if all(not type(entry[col]) is str for col in ['Rental Cost ($/day)','esttimeP90']):
                table[i]['estcostP90'] = entry['Rental Cost ($/day)']*entry['esttimeP90']
        store[scenario] = table
    return store

# adds a row to table when add row is clicked in automation table
@app.callback(
    Output('automation-table','data'),
    [Input('automation-add-row-button','n_clicks'),
    Input('automation-add-row-button','n_clicks_timestamp'),
    Input('automation-apply-button','n_clicks'),
    Input('automation-apply-button','n_clicks_timestamp')],
    [State('automation-store','data'),
    State('select-scenario','value')]
)
def update_automation_table(n_clicks,add_row_timestamp,n_click_calc,calc_ts,store,scenario):
    store = store or {}
    if n_clicks >0 and add_row_timestamp>calc_ts:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Technology','Description (if Other)','Type of Time Affected','Percentage Decrease in Time (%)','Cost ($)']})
        else:
            store[scenario] = [{c: '' for c in ['Technology','Description (if Other)','Type of Time Affected','Percentage Decrease in Time (%)','Cost ($)']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

# update store when table is edited
@app.callback(
    Output('automation-store','data'),
    [Input('automation-table','data')],
    [State('select-scenario','value'),
    State('automation-store','data')]
)
def update_automation_store(table,scenario,store):
    store = store or {}
    if table:
        # apply the percentage change to appropriate times
        # for i,entry in enumerate(table):
        #     if all(not type(entry[col]) is str for col in ['Top Depth (ft)','Bottom Depth (ft)','ROPP10']):
        #         table[i]['esttimeP10'] = max(0.1,round((entry['Bottom Depth (ft)']-entry['Top Depth (ft)'])/entry['ROPP10']/24,1))
        #     if all(not type(entry[col]) is str for col in ['Bottom Depth (ft)','Top Depth (ft)','ROPP90']):
        #         table[i]['esttimeP90'] = max(0.1,round((entry['Bottom Depth (ft)']-entry['Top Depth (ft)'])/entry['ROPP90']/24,1))
        #     if all(not type(entry[col]) is str for col in ['Bottom Depth (ft)','Top Depth (ft)','ROPP50']):
        #         table[i]['esttimeP50'] = max(0.1,round((entry['Bottom Depth (ft)']-entry['Top Depth (ft)'])/entry['ROPP50']/24,1))

        store[scenario] = table
    return store

############### Tab 5 callbacks ###############

# adds a row to table when add row is clicked
@app.callback(
    Output('cementing-table','data'),
    [Input('cementing-add-row-button','n_clicks')],
    [State('cementing-store','data'),
    State('select-scenario','value')]
)
def update_cementing_store(n_clicks,store,scenario):
    store = store or {}
    if n_clicks >0:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Top Depth (ft)','Set Depth (ft)','Casing/Pipe Section','Cement Cost ($)','Est. Cementing Time (hr)']})
        else:
            store[scenario] = [{c: '' for c in ['Top Depth (ft)','Set Depth (ft)','Casing/Pipe Section','Cement Cost ($)','Est. Cementing Time (hr)']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

# update store when table is edited
@app.callback(
    Output('cementing-store','data'),
    [Input('cementing-table','data')],
    [State('select-scenario','value'),
    State('cementing-store','data')]
)
def update_cementing_table(table,scenario,store):
    store = store or {}
    if table:
        store[scenario] = table
    return store

############### Tab 6 callbacks ###############
# adds a row to table when add row is clicked
@app.callback(
    Output('logging-table','data'),
    [Input('logging-add-row-button','n_clicks'),
    Input('logging-calculate-button','n_clicks'),
    Input('logging-add-row-button','n_clicks_timestamp'),
    Input('logging-calculate-button','n_clicks_timestamp')],
    [State('logging-store','data'),
    State('select-scenario','value')]
)
def update_logging_store(n_clicks,n_clicks_calc,row_ts,calc_ts,store,scenario):
    store = store or {}
    if n_clicks >0 and row_ts>calc_ts:
        if scenario in store:
            store[scenario].append({c: '' for c in ['Top Depth (ft)', 'Bottom Depth (ft)', 'Logging Method','Logging Activity','Service Cost ($/day)','Est. Logging Time (hrs)','Est. Non-Productive Time (hrs)','Logging Cost ($)']})
        else:
            store[scenario] = [{c: '' for c in ['Top Depth (ft)', 'Bottom Depth (ft)', 'Logging Method','Logging Activity','Service Cost ($/day)','Est. Logging Time (hrs)','Est. Non-Productive Time (hrs)','Logging Cost ($)']}]
    if not scenario in store:
        raise PreventUpdate
    return store[scenario]

# update store when table is edited
@app.callback(
    Output('logging-store','data'),
    [Input('logging-table','data')],
    [State('select-scenario','value'),
    State('logging-store','data')]
)
def update_logging_table(table,scenario,store):
    store = store or {}
    if table:
        for i,entry in enumerate(table):
            if all(not type(entry[col]) is str for col in ['Service Cost ($/day)','Est. Logging Time (hrs)']):
                table[i]['Logging Cost ($)'] = round(entry['Service Cost ($/day)']*entry['Est. Logging Time (hrs)']/24,2)
        store[scenario] = table
    return store


############### Tab 7 callbacks ###############
@app.callback(
    Output('logistics-table','data'),
    [Input('hidden-initializer','children')],
    [State('logistics-store','data'),
    State('select-scenario','value')]
)
def initialize_table(trigger,store,scenario):
    store = store or {}
    if scenario in store:
        return store[scenario]
    else:
        raise PreventUpdate

@app.callback(
    Output('logistics-store','data'),
    [Input('logistics-table','data')],
    [State('select-scenario','value'),
    State('logistics-store','data')]
)
def store_logistics(table,scenario,store):
    store = store or {}
    store[scenario] = table
    return store

############### Tab 8 callbacks ###############
@app.callback(
    Output('fixed-cost-table','data'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def update_fixed_costs(logistics,fluids,casing,drillbit,cementing,logging,scenario):
    data=[{'Item':item} for item in ['Location','Power, Fuel, Water','Transportation','Rental Equipment','Pipe','Drill Bits','Drilling Fluids','Cement','Logging']]
    # location prep cost
    try:
        data[0]['Cost'] = logistics[scenario][0]['Location Prep Cost ($)']
    except:
        pass

    # fuel water cost
    try:
        data[1]['Cost'] = logistics[scenario][0]['Fuel Cost ($)'] + logistics[scenario][0]['Water Cost ($)']
    except:
        pass

    # transportation cost
    try:
        data[2]['Cost'] = logistics[scenario][0]['Transportation Cost ($)']
    except:
        pass

    # rental equipment
    try:
        data[3]['Cost'] = logistics[scenario][0]['Rental Equipment Cost ($)']
    except:
        pass

    # pipe
    try:
        data[4]['Cost'] = sum(i['Pipe Cost ($)'] for i in casing[scenario])
    except:
        pass

    # drill bits
    try:
        data[5]['Cost'] = sum(i['Bit Cost ($)'] for i in drillbit[scenario])
    except:
        pass

    # drill fluids
    try:
        data[6]['Cost'] = sum(i['Fluids Cost ($)'] for i in fluids[scenario])
    except:
        pass

    # cement
    try:
        data[7]['Cost'] = sum(i['Cement Cost ($)'] for i in cementing[scenario])
    except:
        pass

    # logging
    try:
        data[8]['Cost'] = sum(i['Logging Cost ($)'] for i in logging[scenario])
    except:
        pass
    return data

@app.callback(
    Output('var-cost-table','data'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def update_var_costs(logistics,fluids,casing,drillbit,cementing,logging,scenario):
    data = []
    # Est. Mobilization time (days)
    try:
        data.extend([{
            'Phase Description':'Mobilization',
            'Depth':0,
            'Min.':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Best':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Max.':max(0.1, round(row['Mobilization/Demobilization (days)'],1))
            } for row in logistics[scenario]])
    except:
        pass

    # Est. Cementing time (convert to days)
    try:
        data.extend([{
            'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
            'Depth':row['Set Depth (ft)'],
            'Min.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1))
        } for row in cementing[scenario]])
    except:
        pass

    # Est ROP drilling time (drillbit table; already in days)
    try:
        data.extend([{
            'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':row['esttimeP10'],
            'Best':row['esttimeP50'],
            'Max.':row['esttimeP90']
        } for row in drillbit[scenario]])
    except:
        pass

    # Est. Tripping Time (also from drillbit table; convert to days)
    try:
        data.extend([{
            'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Trip Time (hr)']/24,1))
            } for row in drillbit[scenario]])
    except:
        pass

    # Est. Non-productive logging time (calculate in days based on type of logging)
    # includes logging time if wireline, otherwise only est. non-productive time
    try:
        # loop through logging activities and estimate the NPT and output line in AFE
        for row in logging[scenario]:
            if row['Logging Method'] == 'Wireline':
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                    }])
            else:
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                    }])
    except:
        pass

    try:
        rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
        for i,entry in enumerate(data):
            data[i]['Min Est. Cost ($)'] = rig_rate*entry['Min.']
            data[i]['Best Est. Cost ($)'] = rig_rate*entry['Best']
            data[i]['Max Est. Cost ($)'] = rig_rate*entry['Max.']

            if i==0:
                data[i]['Min Cumulative Time'] = round(entry['Min.'],1)
                data[i]['Best Cumulative Time'] = round(entry['Best'],1)
                data[i]['Max Cumulative Time'] = round(entry['Max.'],1)
            else:
                data[i]['Min Cumulative Time'] = round(entry['Min.'] + data[i-1]['Min Cumulative Time'],1)
                data[i]['Best Cumulative Time'] = round(entry['Best'] + data[i-1]['Best Cumulative Time'],1)
                data[i]['Max Cumulative Time'] = round(entry['Max.'] + data[i-1]['Max Cumulative Time'],1)

            if i==0:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)']
            else:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)'] + data[i-1]['Min Cumulative Cost']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)'] + data[i-1]['Best Cumulative Cost']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)'] + data[i-1]['Max Cumulative Cost']
    except:
        pass
    # try:
    #     data_df = pd.DataFrame(data)
    #     data_df = data_df.sort_values(by=['Depth'])
    #     data_df['Best'] = data_df['Best'].cumsum()
    #     scenario_data[scenario]['time'] = data_df['Best']
    #     scenario_data[scenario]['depth'] = data_df['Depth']
    # except:
    #     raise PreventUpdate
    return data

@app.callback(
    Output('rig-days','children'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def calc_rig_days(logistics,fluids,casing,drillbit,cementing,logging,scenario):
    data = []
    # Est. Mobilization time (days)
    try:
        data.extend([{
            'Phase Description':'Mobilization',
            'Depth':'',
            'Min.':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Best':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Max.':max(0.1, round(row['Mobilization/Demobilization (days)'],1))
            } for row in logistics[scenario]])
    except:
        pass

    # Est. Cementing time (convert to days)
    try:
        data.extend([{
            'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
            'Depth':row['Set Depth (ft)'],
            'Min.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1))
        } for row in cementing[scenario]])
    except:
        pass

    # Est ROP drilling time (drillbit table; already in days)
    try:
        data.extend([{
            'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':row['esttimeP10'],
            'Best':row['esttimeP50'],
            'Max.':row['esttimeP90']
        } for row in drillbit[scenario]])
    except:
        pass

    # Est. Tripping Time (also from drillbit table; convert to days)
    try:
        data.extend([{
            'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Trip Time (hr)']/24,1))
            } for row in drillbit[scenario]])
    except:
        pass

    # Est. Non-productive logging time (calculate in days based on type of logging)
    # includes logging time if wireline, otherwise only est. non-productive time
    try:
        # loop through logging activities and estimate the NPT and output line in AFE
        for row in logging[scenario]:
            if row['Logging Method'] == 'Wireline':
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                    }])
            else:
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                    }])
    except:
        pass

    try:
        rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
        for i,entry in enumerate(data):
            data[i]['Min Est. Cost ($)'] = rig_rate*entry['Min.']
            data[i]['Best Est. Cost ($)'] = rig_rate*entry['Best']
            data[i]['Max Est. Cost ($)'] = rig_rate*entry['Max.']

            if i==0:
                data[i]['Min Cumulative Time'] = entry['Min.']
                data[i]['Best Cumulative Time'] = entry['Best']
                data[i]['Max Cumulative Time'] = entry['Max.']
            else:
                data[i]['Min Cumulative Time'] = entry['Min.'] + data[i-1]['Min Cumulative Time']
                data[i]['Best Cumulative Time'] = entry['Best'] + data[i-1]['Best Cumulative Time']
                data[i]['Max Cumulative Time'] = entry['Max.'] + data[i-1]['Max Cumulative Time']

            if i==0:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)']
            else:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)'] + data[i-1]['Min Cumulative Cost']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)'] + data[i-1]['Best Cumulative Cost']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)'] + data[i-1]['Max Cumulative Cost']
    except:
        pass
    try:
        data_df = pd.DataFrame(data)
        return "{:,}".format(math.ceil(sum(data_df['Best'])))
    except:
        raise PreventUpdate

@app.callback(
    Output('subtotal-cost','children'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def calc_subtotal(logistics,fluids,casing,drillbit,cementing,logging,scenario):
    data = []
    # Est. Mobilization time (days)
    try:
        data.extend([{
            'Phase Description':'Mobilization',
            'Depth':'',
            'Min.':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Best':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Max.':max(0.1, round(row['Mobilization/Demobilization (days)'],1))
            } for row in logistics[scenario]])
    except:
        pass

    # Est. Cementing time (convert to days)
    try:
        data.extend([{
            'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
            'Depth':row['Set Depth (ft)'],
            'Min.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1))
        } for row in cementing[scenario]])
    except:
        pass

    # Est ROP drilling time (drillbit table; already in days)
    try:
        data.extend([{
            'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':row['esttimeP10'],
            'Best':row['esttimeP50'],
            'Max.':row['esttimeP90']
        } for row in drillbit[scenario]])
    except:
        pass

    # Est. Tripping Time (also from drillbit table; convert to days)
    try:
        data.extend([{
            'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Trip Time (hr)']/24,1))
            } for row in drillbit[scenario]])
    except:
        pass

    # Est. Non-productive logging time (calculate in days based on type of logging)
    # includes logging time if wireline, otherwise only est. non-productive time
    try:
        # loop through logging activities and estimate the NPT and output line in AFE
        for row in logging[scenario]:
            if row['Logging Method'] == 'Wireline':
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                    }])
            else:
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                    }])
    except:
        pass

    try:
        rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
        for i,entry in enumerate(data):
            data[i]['Min Est. Cost ($)'] = rig_rate*entry['Min.']
            data[i]['Best Est. Cost ($)'] = rig_rate*entry['Best']
            data[i]['Max Est. Cost ($)'] = rig_rate*entry['Max.']

            if i==0:
                data[i]['Min Cumulative Time'] = entry['Min.']
                data[i]['Best Cumulative Time'] = entry['Best']
                data[i]['Max Cumulative Time'] = entry['Max.']
            else:
                data[i]['Min Cumulative Time'] = entry['Min.'] + data[i-1]['Min Cumulative Time']
                data[i]['Best Cumulative Time'] = entry['Best'] + data[i-1]['Best Cumulative Time']
                data[i]['Max Cumulative Time'] = entry['Max.'] + data[i-1]['Max Cumulative Time']

            if i==0:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)']
            else:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)'] + data[i-1]['Min Cumulative Cost']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)'] + data[i-1]['Best Cumulative Cost']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)'] + data[i-1]['Max Cumulative Cost']
    except:
        pass

    try:
        data_df = pd.DataFrame(data)
        return "{:,}".format(math.ceil(sum(data_df['Best Est. Cost ($)'])))
    except:
        raise PreventUpdate

@app.callback(
    Output('total-cost','children'),
    [Input('logistics-store','data'),
    Input('fluids-store','data'),
    Input('casing-store','data'),
    Input('drill-bit-store','data'),
    Input('cementing-store','data'),
    Input('logging-store','data'),
    Input('select-scenario','value')]
)
def calc_total(logistics,fluids,casing,drillbit,cementing,logging,scenario):
    data = []
    # Est. Mobilization time (days)
    try:
        data.extend([{
            'Phase Description':'Mobilization',
            'Depth':'',
            'Min.':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Best':max(0.1, round(row['Mobilization/Demobilization (days)'],1)),
            'Max.':max(0.1, round(row['Mobilization/Demobilization (days)'],1))
            } for row in logistics[scenario]])
    except:
        pass

    # Est. Cementing time (convert to days)
    try:
        data.extend([{
            'Phase Description':'Cementing: '+row['Casing/Pipe Section'],
            'Depth':row['Set Depth (ft)'],
            'Min.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Est. Cementing Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Est. Cementing Time (hr)']/24,1))
        } for row in cementing[scenario]])
    except:
        pass

    # Est ROP drilling time (drillbit table; already in days)
    try:
        data.extend([{
            'Phase Description':'Drilling Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':row['esttimeP10'],
            'Best':row['esttimeP50'],
            'Max.':row['esttimeP90']
        } for row in drillbit[scenario]])
    except:
        pass

    # Est. Tripping Time (also from drillbit table; convert to days)
    try:
        data.extend([{
            'Phase Description':'Trip Time'+', '+str(row['Top Depth (ft)'])+'-'+str(row['Bottom Depth (ft)'])+'ft',
            'Depth':row['Bottom Depth (ft)'],
            'Min.':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Best':max(0.1,round(row['Trip Time (hr)']/24,1)),
            'Max.':max(0.1,round(row['Trip Time (hr)']/24,1))
            } for row in drillbit[scenario]])
    except:
        pass

    # Est. Non-productive logging time (calculate in days based on type of logging)
    # includes logging time if wireline, otherwise only est. non-productive time
    try:
        # loop through logging activities and estimate the NPT and output line in AFE
        for row in logging[scenario]:
            if row['Logging Method'] == 'Wireline':
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Best':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1)),
                    'Max.':max(0.1,round((row['Est. Logging Time (hrs)']+row['Est. Non-Productive Time (hrs)'])/24,1))
                    }])
            else:
                data.extend([{
                    'Phase Description':'Logging: '+row['Logging Activity'],
                    'Depth':row['Bottom Depth (ft)'],
                    'Min.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Best':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1)),
                    'Max.':max(0.1,round(row['Est. Non-Productive Time (hrs)']/24,1))
                    }])
    except:
        pass

    try:
        rig_rate = logistics[scenario][0]['Daily Rig Rate ($/day)']
        for i,entry in enumerate(data):
            data[i]['Min Est. Cost ($)'] = rig_rate*entry['Min.']
            data[i]['Best Est. Cost ($)'] = rig_rate*entry['Best']
            data[i]['Max Est. Cost ($)'] = rig_rate*entry['Max.']

            if i==0:
                data[i]['Min Cumulative Time'] = entry['Min.']
                data[i]['Best Cumulative Time'] = entry['Best']
                data[i]['Max Cumulative Time'] = entry['Max.']
            else:
                data[i]['Min Cumulative Time'] = entry['Min.'] + data[i-1]['Min Cumulative Time']
                data[i]['Best Cumulative Time'] = entry['Best'] + data[i-1]['Best Cumulative Time']
                data[i]['Max Cumulative Time'] = entry['Max.'] + data[i-1]['Max Cumulative Time']

            if i==0:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)']
            else:
                data[i]['Min Cumulative Cost'] = entry['Min Est. Cost ($)'] + data[i-1]['Min Cumulative Cost']
                data[i]['Best Cumulative Cost'] = entry['Best Est. Cost ($)'] + data[i-1]['Best Cumulative Cost']
                data[i]['Max Cumulative Cost'] = entry['Max Est. Cost ($)'] + data[i-1]['Max Cumulative Cost']
    except:
        pass
    data_df = pd.DataFrame(data)

    data_fixed=[{'Item':item} for item in ['Location','Power, Fuel, Water','Transportation','Rental Equipment','Pipe','Drill Bits','Drilling Fluids','Cement','Logging']]
    # location prep cost
    try:
        data_fixed[0]['Cost'] = logistics[scenario][0]['Location Prep Cost ($)']
    except:
        pass

    # fuel water cost
    try:
        data_fixed[1]['Cost'] = logistics[scenario][0]['Fuel Cost ($)'] + logistics[scenario][0]['Water Cost ($)']
    except:
        pass

    # transportation cost
    try:
        data_fixed[2]['Cost'] = logistics[scenario][0]['Transportation Cost ($)']
    except:
        pass

    # rental equipment
    try:
        data_fixed[3]['Cost'] = logistics[scenario][0]['Rental Equipment Cost ($)']
    except:
        pass

    # pipe
    try:
        data_fixed[4]['Cost'] = sum(i['Pipe Cost ($)'] for i in casing[scenario])
    except:
        pass

    # drill bits
    try:
        data_fixed[5]['Cost'] = sum(i['Bit Cost ($)'] for i in drillbit[scenario])
    except:
        pass

    # drill fluids
    try:
        data_fixed[6]['Cost'] = sum(i['Fluids Cost ($)'] for i in fluids[scenario])
    except:
        pass

    # cement
    try:
        data_fixed[7]['Cost'] = sum(i['Cement Cost ($)'] for i in cementing[scenario])
    except:
        pass

    # logging
    try:
        data_fixed[8]['Cost'] = sum(i['Logging Cost ($)'] for i in logging[scenario])
    except:
        pass
    try:
        data_fixed_df = pd.DataFrame(data_fixed)
        return "{:,}".format(math.ceil(sum(data_df['Best Est. Cost ($)'])+sum(data_fixed_df['Cost'])))
    except:
        raise PreventUpdate


app.css.append_css({
    'external_url': '/assets/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
