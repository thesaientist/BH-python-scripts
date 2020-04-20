import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.plotly as py
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

drill_bit_cols = [{'name':['',i],'id':i,'presentation':'dropdown','editable':True} for i in ['Type']]
drill_bit_cols.extend({'name':['',i],'id':i,'type':'numeric','editable':True} for i in ['Bit Cost ($)','Top Depth (ft)','Bottom Depth (ft)','Trip Time (hr)'])
drill_bit_cols.extend({'name':['Estimated ROP (ft/hr)',i],'id':'ROP'+i,'type':'numeric','editable':True} for i in ['P10','P50','P90'])
drill_bit_cols.extend({'name':['Estimated Time (days)',i],'id':'esttime'+i,'type':'numeric','editable':False} for i in ['P10','P50','P90'])

drill_tool_cols = [{'name':['',i],'id':i,'type':'text','editable':True} if i in ['Tool/Service Type'] else {'name':['',i],'id':i, 'type':'numeric','editable':True} for i in ['Top Depth (ft)','Bottom Depth (ft)','Tool/Service Type','Rental Cost ($/day)']]
drill_tool_cols.extend({'name':['Estimated Time (days)',i],'id':'esttime'+i,'type':'numeric','editable':True} for i in ['P10','P50','P90'])
drill_tool_cols.extend({'name':['Estimated Cost ($)',i],'id':'estcost'+i, 'type':'numeric','editable':False} for i in ['P10','P50','P90'])

auto_cols = [{'name':['',i],'id':i,'presentation':'dropdown','editable':True} for i in ['Technology']]
auto_cols.extend([{'name':['',i],'id':i,'type':'text','editable':True} for i in ['Description (if Other)']])
auto_cols.extend([{'name':['',i],'id':i,'presentation':'dropdown','editable':True} for i in ['Type of Time Affected']])
auto_cols.extend([{'name':['',i],'id':i,'type':'numeric','editable':True} for i in ['Percentage Decrease in Time (%)','Cost ($)']])

tab_4_layout= html.Div([
    html.H6('ROP vs. Depth'),
    dcc.Graph(id='drill-bits-graph',
    figure=dict(
        layout=dict(
            paper_bgcolor = 'rgba(0,0,0,0)',
            plot_bgcolor = 'rgba(0,0,0,0)',
            xaxis = dict(
                color='#fff',
                showgrid=False
            ),
            yaxis = dict(
                color='#fff',
                showgrid=False
            )
        )
    )),
    html.H5('Drill Bits'),
    dash_table.DataTable(
        id='drill-bits-table',
        columns = drill_bit_cols,
        data=[],
        editable = True,
        column_static_dropdown=[
            {
                'id': 'Type',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['Roller Cone', 'TCI', 'PDC', 'Diamond','Other']
                ]
            },
        ],
        # editable={i:True if i in ['Top Depth (ft)','Bottom Depth (ft)','Type','Diameter (in)','Est. Min ROP (ft/hr)','Est. Best ROP (ft/hr)','Est. Max ROP (ft/hr)','Bit Cost ($)','Trip Time (hr)'] else i:False for i in ['Top Depth (ft)','Bottom Depth (ft)','Type','Diameter (in)','Est. Min ROP (ft/hr)','Est. Best ROP (ft/hr)','Est. Max ROP (ft/hr)','ROPP10','ROPP50','ROPP90','Bit Cost ($)','Trip Time (hr)']},
        row_deletable=True,
        merge_duplicate_headers=True,
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
            'if': {'column_id':'esttimeP10'},
            'backgroundColor':'#73ace2a2'
        },
        {
            'if': {'column_id':'esttimeP90'},
            'backgroundColor':'#73ace2a2'
        },
        {
            'if': {'column_id':'esttimeP50'},
            'backgroundColor':'#73ace2a2'
        }
        ],
    ),
    html.Button(
        'Add Row',
        id='drill-bit-add-row-button',
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
        id='drill-bit-calculate-button',
        n_clicks=0,
        n_clicks_timestamp=0,
        style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px',
                    'margin-left':'5px'
        }
    ),
    html.H5('Drilling Tools/Services'),
    dash_table.DataTable(
        id='drill-tools-table',
        columns = drill_tool_cols,
        data=[],
        editable=True,
        row_deletable=True,
        merge_duplicate_headers=True,
        # style_as_list_view=True,
        style_header={
            # 'backgroundColor': '#fff',
            'font-family': 'system-ui',
            # 'color': 'black',
            'font-weight':'bold'
        },
        style_cell={
            'textAlign': 'center',
            'font-family': 'system-ui',
            # 'backgroundColor': '#fff',
            # 'color': 'black'
        },
        style_data_conditional=[{
            'if': {'column_id':'estcostP10'},
            'backgroundColor':'#73ace2a2'
        },
        {
            'if': {'column_id':'estcostP90'},
            'backgroundColor':'#73ace2a2'
        },
        {
            'if': {'column_id':'estcostP50'},
            'backgroundColor':'#73ace2a2'
        }
        ],
    ),
    html.Button(
        'Add Row',
        id='drill-tool-add-row-button',
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
        id='drill-tool-calculate-button',
        n_clicks=0,
        n_clicks_timestamp=0,
        style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px',
                    'margin-left':'5px'
        }
    ),
    html.H5('Automation Technologies'),
    dash_table.DataTable(
        id='automation-table',
        columns = auto_cols,
        data=[],
        editable=True,
        column_static_dropdown=[
            {
                'id': 'Technology',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['Motor Steerable', 'Rotary Steerable', \
                            'Managed Pressure Drilling (MPD)', 'Measurement While Drilling (MWD)', \
                            'Pipe Handling System', 'Computer Controlled WOB / ROP', \
                            'Computer Controlled Mud System', 'Other']
                ]
            },
            {
                'id': 'Type of Time Affected',
                'dropdown': [
                    {'label': i, 'value': i}
                    for i in ['Non-Productive Time (NPT)', 'Drilling Time','Both']
                ]
            },

        ],
        row_deletable=True,
        merge_duplicate_headers=True,
        # style_as_list_view=True,
        style_header={
            # 'backgroundColor': '#fff',
            'font-family': 'system-ui',
            # 'color': 'black',
            'font-weight':'bold'
        },
        style_cell={
            'textAlign': 'center',
            'font-family': 'system-ui',
            # 'backgroundColor': '#fff',
            # 'color': 'black'
        },
    ),
    html.Button(
        'Add Row',
        id='automation-add-row-button',
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
        'Apply',
        id='automation-apply-button',
        n_clicks=0,
        n_clicks_timestamp=0,
        style={
                    'font-family': 'system-ui',
                    'color': '#fff',
                    'letter-spacing': '0.7px',
                    'margin-top':'10px',
                    'margin-left':'5px'
        }
    ),
])
