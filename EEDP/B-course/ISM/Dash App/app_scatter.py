################################################################################
##
##    Property of Baker Hughes, a GE Company
##    Copyright 2019
##    Author: Sai Uppati
##    saipranav.uppati@bhge.com
##
################################################################################

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

# instantiate the Dash application class object
app = dash.Dash()

# get data from the web and assign to pandas data frame
df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/' +
    '5d1ea79569ed194d432e56108a04d188/raw/' +
    'a9f9e8076b837d541398e999dcbac2b2826a81f8/'+
    'gdp-life-exp-2007.csv')

# dictionary of colors to use in app
# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }

# Dash app layout has several components including HTML header (H1),
# HTML Content Division element (Div)
# Plot based on dash core components graph class (Graph)
app.layout = html.Div([
    # html.H1(
    #     children='Hello Dash',
    #     style={
    #         'textAlign': 'center',
    #         'color': colors['text']
    #     }
    # ),
    # html.Div(children='Dash: A web application framework for Python.', style={
    #     'textAlign': 'center',
    #     'color': colors['text']
    # }),
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure={
            'data': [
                go.Scatter(
                    x=df[df['continent'] == i]['gdp per capita'],
                    y=df[df['continent'] == i]['life expectancy'],
                    text=df[df['continent'] == i]['country'],
                    mode='markers',
                    opacity=0.8,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in df.continent.unique()
            ],
            'layout': go.Layout(
                xaxis=dict(type='log',
                    title='GDP Per Capita',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                ),
                yaxis=dict(title='Life Expectancy',
                    titlefont=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                ),
                #margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
