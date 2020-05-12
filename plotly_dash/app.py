# -*- coding: utf-8 -*-
# Operational Libs
import logging
import os
import glob

# Dash Libs
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Analytic Libs
import pandas as pd
import numpy as np
import math

LOG = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

app = dash.Dash(__name__ )

# Mark the correct server for Heroku or Civis deployment
server = app.server

# Import datafile to begin setting parameter limits
if os.getenv("CIVIS_SERVICE_VERSION"):
    # This environment variable will be set when deployed in Civis
    import civis
    CIVIS_FILE_ID = 100315314
    logging.info(f"Downloading data from Civis File {CIVIS_FILE_ID}.")
    df = civis.io.file_to_dataframe(CIVIS_FILE_ID)
    logging.info(f"Downloaded {len(df)} rows.")
    # TEMP HARDCODING
    output_list = ['infected', 'hospitalized',
                'critical', 'deaths', 'recovered']
    params_list = ['time_to_death', 'fraction_symptomatic', 'fraction_severe',
                'fraction_critical', 'cfr', 'reduced_inf_of_det_cases',
                'social_multiplier_3', 'fraction_dead', 'fraction_hospitalized']
    df = df[['date', 'ems', 'run_num'] + params_list + output_list].copy()
else:
    path_name = "data"
    f_name = "dash_EMS_trajectories_separate_endsip_20200419.csv"
    file_location = os.path.join(path_name, f_name)

    # Read in file
    df = pd.read_csv(file_location)

    # USE LOCAL FILE 
    params_list = [col for col in df if col.startswith('param')]
    output_list = [col for col in df if col.startswith('output')]


# Setup 
#******************************************************************************************

# Filter out timeframes for graphs
# Generate datetime to get weeks for slider
df['date']= pd.to_datetime(df['date'])
# Get week of date
df['week'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='d')

dateList = sorted(df['week'].unique())


# RangeSlider values need to be ints - convert to unix timestamp
def dtToUnix (dt):
    ''' Convert datetime to Unix Milliseconds 
        https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#from-timestamps-to-epoch
    '''
    unixTime = (dt - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    return unixTime

# Convert unix Time back to datetime
def unixToDt (unixTime):
    ''' Convert Unix milliseconds to datetime '''  
    return pd.to_datetime(unixTime, unit='s')




# Parameter Filtering -> RangeSlider Factory
def generateRangeSlider (param, numMarks):
    ''' Given a parameter from the dataframe, generates the divs for range sliders
        Returns the div + range slider
    '''

    def markFormatter (val):
            if val < 1:
                return "{:.1%}".format(val)
            else:
                return "{:.2f}".format(val)

    def setMarks():

        # Inherit parameter from function
        minMark = df[param].min()
        maxMark = df[param].max()
        # linspace returns evenly spaced list. Rounded to capture all values
        markRange =  np.linspace(math.floor(minMark * 1000) / 1000, math.ceil(maxMark * 1000) / 1000, numMarks)

        return markRange

    rangeList = setMarks()

    return html.Div (
        style = {"margin": "25px 5px 30px 0px"},
        children = [
            html.Div(
                style={"margin-left": "5px"},
                children=[
                    html.P(param.upper(), className="control_label",),
                    dcc.RangeSlider(
                        id=param + "Slider",
                        step=None,
                        marks = {v: markFormatter(v)  for v in rangeList},
                        min=rangeList[0],
                        max=rangeList[-1],
                        value=[rangeList[0], rangeList[-1]]
                    )
                ]
            )
        ]
    )



# Main App Layout
#############################################################################
app.layout = html.Div(
    children = [
        # Header
        html.Div(
            children =[
                html.H4("Northwestern COVID Simulation Model Explorer", id="title",),
                html.P("Model Version: <Date of Model Run>", id="subtitle",),
            ],
            id="pageTitleContainer",
            className="pretty_container title",
        ),
        # EMS Selector and Sliders
        html.Div(
            [   
                # EMS Selector
                html.Div(
                    [
                        html.P(
                            "Select EMS Region:",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            options=[{"label": str(i), "value": i} for i in sorted(df['ems'].unique())],
                            multi=False,
                            placeholder="Choose EMS Region",
                            id="emsDropdown",
                            className="dcc_control",
                        ),
                    ],
                    className="time-container",
                ),
                # Week Selector
                html.Div(
                    [
                        html.P(
                            "Filter Graphs by Week:",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="timeSlider",
                            min=dtToUnix(dateList[0]),
                            max=dtToUnix(dateList[-1]),
                            value=[dtToUnix(dateList[0]), dtToUnix(dateList[-1])],
                            marks= {#dtToUnix(dt): np.datetime_as_string(dt, unit='D') for i, dt in enumerate(dateList)},
                                dtToUnix(dt): {
                                    'label': np.datetime_as_string(dt, unit='D'),
                                    'style': {
                                        'transform':'rotate(45deg)',
                                        'font-size':'8px',
                                    }
                                } for i, dt in enumerate(dateList) #if i %2 == 0
                            },
                            #dots=True,
                            allowCross=False,
                            className="",
                        ),
                    ], 
                    className="time-container",
                ),
                # Sliders - Generate 3x3 Slider matrix
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    "Filter Graphs by Model Parameters:",
                                    className="control_label",
                                ),      
                            ],
                        ),
                        html.Div(
                            [
                                html.Div(
                                    # Generate a set of sliders for each param
                                    # Name of each slider is "[param] + _"slider"
                                    [generateRangeSlider(i, 5) for i in
                                        params_list[:len(params_list)//3]],
                                    className="one-third columns",
                                    id="",
                                ),
                                html.Div(
                                    [generateRangeSlider(i, 5) for i in
                                        params_list[len(params_list)//3: 2*len(params_list)//3]],
                                    className="one-third columns",
                                    id="",
                                ),
                                html.Div(
                                    [generateRangeSlider(i, 5) for i in
                                        params_list[2*len(params_list)//3:]],
                                    className="one-third columns",
                                    id="",
                                ),
                            ],
                            className="flex-display",
                        ),
                    ],
                    className="time-container",
                ),
            ],
            className=""
        ),
        # Container for all 5 Output Charts
        html.Div(
            [
                # Top 3 Chart Container
                html.Div(
                    [
                        # Chart 0
                        html.Div(
                            [
                                dcc.Graph(id="outputLineChart0")
                            ],
                            #className="one-third columns",
                            className="graphDiv",
                        ),
                        # Chart 1
                        html.Div(
                            [
                                dcc.Graph(id="outputLineChart1")
                            ],
                            #className="one-third columns",
                            className="graphDiv",
                        ),
                        # Chart 2...
                        html.Div(
                            [
                                dcc.Graph(id="outputLineChart2")
                            ],
                            #className="one-third columns",
                            className="graphDiv",
                        ),
                    ],
                    className="flex-display chartContainerDiv "
                ),
                # Remaining two charts
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(id="outputLineChart3")
                            ],
                            #className="one-third columns",
                            className="graphDiv",
                        ),
                        html.Div(
                            [
                                dcc.Graph(id="outputLineChart4")
                            ],
                            #className="one-third columns",
                            className="graphDiv",
                        ),
                    ],
                    #className="flex-display chartContainerDiv "
                    className="flex-display chartContainerDiv "
                ),
            ],
           # id="CONTAINER HOLDING ALL 5 CHARTS",
            className="chartContainer",
        ),
        # Footer Info
        html.Div(
            children=[
                html.P("Keith Walewski | Questions? - keith.walewski@gmail.com ",
                className="",
                id="footer"
                ),
            ],
            className="pretty-container"
        )
    ],
    className="mainContainer",
    id="",
)


# Selector for First Output Chart
# Callback inputs will all be the same
@app.callback(
    [
        Output('outputLineChart0', 'figure'),
        Output('outputLineChart1', 'figure'),
        Output('outputLineChart2', 'figure'),
        Output('outputLineChart3', 'figure'),
        Output('outputLineChart4', 'figure'),
    ],

    [
        Input('emsDropdown', 'value'),
        Input('timeSlider', 'value'),
        # Unpack the elements of the list using *
        *[Input(param + 'Slider', 'value') for param in params_list]
    ],
)
def generateOutput(emsValue, timeValues, *paramValues):

    # Setup Color Options
    colors = {
        'sf': '#1798c1',
        'green': '#416165', # Color for plots & text
        'beige': '#F7F7FF', #Color for gridlinesgit 
    }

    def makeChart (outputVar):
        # Generate query string for EMS value and range of sliders
        emsString = "({0} == {1})".format('ems', emsValue)
        # Rangeslider passes values for the bottom and top of the range as a list [bottom, top]
        # Filter RangeSlider for timeValues - inclusive of selected timeframe
        timeString = "({0} >= '{1}') & ({0} <= '{2}')".format('week', unixToDt(timeValues[0]).strftime("%Y-%m-%d"), unixToDt(timeValues[1]).strftime("%Y-%m-%d")) 
        # Filter RangeSlider for Parameter Values
        paramString = " & ".join(["({0} >= {1}) & ({0} <= {2})".format(param, pvalue[0], pvalue[1]) for param, pvalue in zip(params_list, paramValues)]) 
        strings = [emsString, timeString, paramString]
        queryString = " & ".join(strings)
        
        # Filter data frame given the slider inputs
        dff = df.query(queryString)

        # Generate list of columns to group by:
        groupbyList =  ['ems', 'run_num'] + params_list

        # Generate Figure for plotting
        figure = go.Figure()

        # This plot will create # of runs * parameter combo traces
        for name, group in dff.groupby(groupbyList):
            figure.add_trace(go.Scatter(
                        x=group['date'],
                        y=group[outputVar], # Variable for each output chart
                        mode='lines',
                        opacity=0.3,
                        line=dict(color=colors['green'], width=1)
                    )
                )
        figure.update_layout(
            font=dict(
                family="Open Sans, monospace",
                size=14,
                color=colors['green']
            ),
            title=outputVar.upper() + " by Date",
            showlegend=False,
            yaxis=dict(
                tickformat="<,f",
                gridcolor=colors['beige'],
                gridwidth=2,
            ),
            xaxis=dict(
                showgrid=False,
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
        )

        return figure

    # Return a list of figures to feed callback
    return [makeChart(output) for output in output_list]



if __name__ == '__main__':
    app.run_server(debug=True)



# TODOS
# ----- DONE Update Title & Subtitle
# Add note for refresh timing
# Add ability to choose multiple EMS groups (checkbox or multi-select dropdown)
# Add toggle for all traces or only median / percentiles
# Add slider for Week-chooser
# Show Today's date on graph