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

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# instantiate the Dash application class object
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# dictionary of colors to use in app
# colors = {
#     'background': '#111111',
#     'text': '#7FDBFF'
# }

# Dash app layout has several components including HTML header (H1),
# HTML Content Division element (Div)
# Plot based on dash core components graph class (Graph)
app.layout = html.Div(children=[
    html.H1(
        children='Hello Dash'
    ),
    html.Div(children='Dash: A web application framework for Python.'
        # style={
        # 'textAlign': 'center',
        # 'color': colors['text']
        # }
    ),
    dcc.Graph(
        id='Graph1',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                # 'plot_bgcolor': colors['background'],
                # 'paper_bgcolor': colors['background'],
                # 'font': {
                #     'color': colors['text']
                # }
                'title' : 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
