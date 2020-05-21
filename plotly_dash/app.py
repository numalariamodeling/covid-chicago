# -*- coding: utf-8 -*-
# Operational Libs
import collections
import logging
import os

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

# Where the CSV data files are found.
CIVIS_PROJECT_ID = 135876

LOCAL_DATA_DIR = "data"
DEV_CSV_FILENAME = "dash_trajectoriesDat_baseline.csv"  # file ID: 103222548

EMS_MAPPING = {"North-Central": (1, 2), "Central": (3, 6), "Southern": (4, 5), "Northeast": (7, 8, 9, 10, 11)}


def preprocess_df(df):
    """Preprocess the dataframe.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
    """
    # Filter out timeframes for graphs
    # Generate datetime to get weeks for slider
    df['date'] = pd.to_datetime(df['date'])
    # Get week of date
    df['week'] = df['date'] - pd.to_timedelta(df['date'].dt.weekday, unit='d')
    # Get month of date
    df['month'] = df['date'].values.astype('datetime64[M]')
    # Map EMS to Groupings
    ems_to_region_mapping = {x: region for region, v in EMS_MAPPING.items() for x in v}
    # Create a column for later filtering
    df['emsGroup'] = df['ems'].map(ems_to_region_mapping)
    return df


DATES = [np.datetime64('2020-02-01'), np.datetime64('2021-03-01')]

PARAMS = """
param_fraction asymptomatic cases detected
param_fraction mild symptomatic cases detected
param_fraction of infections that are symptomatic
param_fraction of severe cases that die
param_fraction of symptomatic cases that are severe
param_fraction severe cases detected
param_reduced contact after stay at home
param_reduced infectiousness of detected cases
""".strip().split("\n")

OUTPUTS = """
output_daily new ICU cases
output_daily new deaths
output_daily new mild symptomatic cases
output_daily new severe symptomatic cases
output_number currently infectious
output_number recovered
""".strip().split("\n")

# A dummy dataframe to not crash the dashboard when it first spins up.
INITIAL_DF = preprocess_df(
    pd.DataFrame(
        {
            "date": ["2020-02-01"],
            "ems": [1],
            "run_num": [0],
            **{param: [0] for param in PARAMS},
            **{output: [0] for output in OUTPUTS},
        }
    )
)

app = dash.Dash(__name__ )

# Mark the correct server for Heroku or Civis deployment
server = app.server

if os.getenv("CIVIS_SERVICE_VERSION"):
    # This environment variable will be set when deployed in Civis
    import civis

    client = civis.APIClient()
    CSV_FILES = civis.find(
        client.projects.get(CIVIS_PROJECT_ID).files,
        file_name=lambda filename: filename.endswith(".csv"),
    )
    logging.info("%d CSV files found", len(CSV_FILES))
else:
    CSVFile = collections.namedtuple("CSVFile", ("id", "file_name"))
    CSV_FILES = [CSVFile(id=None, file_name=DEV_CSV_FILENAME)]


# Setup 
#############################################################################

# Color Options 
colors = {
    'sf': '#1798c1',
    'green': '#416165', # Color for plots & text
    'beige': '#F7F7FF', #Color for gridlinesgit 
}


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
        # TODO
        # minMark = DF[param].min()
        # maxMark = DF[param].max()
        minMark = 0
        maxMark = 100
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
        html.Div(id="df-hidden-div", style={"display": "none"}),
        # Header
        html.Div(
            children =[
                html.H4("Northwestern COVID Simulation Model Explorer", id="title",),
                html.P("Model Version: <Date of Model Run>", id="subtitle",),
            ],
            id="pageTitleContainer",
            className="pretty_container title",
        ),
        # Container holding selectors on left and charts on right
        html.Div(
            [   
                html.Div(
                    [
                        # CSV File Selector
                        html.Div(
                            [
                                html.P(
                                    "Select CSV File:",
                                    className="control_label",
                                ),
                                dcc.Dropdown(
                                    options=[
                                        {"label": f.file_name,
                                         "value": f.file_name}
                                        for f in CSV_FILES],
                                    multi=False,
                                    placeholder="Choose CSV File",
                                    id="csvDropdown",
                                    className="dcc_control",
                                ),
                            ],
                            className="time-container",
                        ),
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
                                            options=[{'label': name, 'value': name} for name in EMS_MAPPING],
                                            multi=False,
                                            placeholder="Choose EMS Region",
                                            id="emsDropdown",
                                            className="dcc_control",
                                        ),
                                    ],
                                    className="time-container one-half column",
                                ),
                                # Toggle For Charts
                                html.Div(
                                    [
                                        html.P(
                                            "This could be radio or dropdown:",
                                            className="control_label",
                                        ),
                                        dcc.RadioItems(
                                            options=[
                                                {'label': 'New York City', 'value': 'NYC'},
                                                {'label': 'Montréal', 'value': 'MTL'},
                                                {'label': 'San Francisco', 'value': 'SF'}
                                            ],
                                            value='MTL',
                                            id="chartToggle",
                                            className="dcc_control",
                                        ),
                                    ],
                                    className="time-container one-half column",
                                ),
                            ],
                            className="flex-display"
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
                                    min=dtToUnix(DATES[0]),
                                    max=dtToUnix(DATES[-1]),
                                    value=[dtToUnix(DATES[0]), dtToUnix(DATES[-1])],
                                    marks= {
                                        dtToUnix(dt): {
                                            'label': np.datetime_as_string(dt, unit='M'),
                                            'style': {
                                                'transform':'rotate(45deg)',
                                                'font-size':'8px',
                                            }
                                        } for i, dt in enumerate(DATES)
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
                                            [generateRangeSlider(i, 5) for i in PARAMS],
                                            className="dcc_control",
                                            id="",
                                        ),
                                    ],
                                    className="",
                                ),
                            ],
                            className="time-container",
                        ),
                    ],
                    className="four columns"
                ), 
                # Container for all Output Charts
                html.Div(
                    [
                        # Rendered Warning
                        html.Div(
                            [
                                html.P(
                                "Note: rendering may take a few seconds after adjusting parameters",
                                className="control_label",
                                ),
                            ],
                        ),
                        # 3 x 2 Arrangement
                        html.Div(
                            [
                                # Top 2 Charts
                                html.Div(
                                    [
                                        # Chart 0
                                        html.Div(
                                            [
                                                dcc.Graph(id="outputLineChart0")
                                            ],
                                            className="graphDiv",
                                        ),
                                        # Chart 1
                                        html.Div(
                                            [
                                                dcc.Graph(id="outputLineChart1")
                                            ],
                                            className="graphDiv",
                                        ),
                                    ],
                                    className="flex-display chartContainerDiv "
                                ),
                                # Middle two charts
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Graph(id="outputLineChart2")
                                            ],
                                            className="graphDiv",
                                        ),
                                        html.Div(
                                            [
                                                dcc.Graph(id="outputLineChart3")
                                            ],
                                            className="graphDiv",
                                        ),                                    
                                    ],
                                    className="flex-display chartContainerDiv "
                                ),
                                # Bottom two charts
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                dcc.Graph(id="outputLineChart4")
                                            ],
                                            className="graphDiv",
                                        ),
                                        html.Div(
                                            [
                                                dcc.Graph(id="outputLineChart5")
                                            ],
                                            className="graphDiv",
                                        ),
                                    ],
                                    className="flex-display chartContainerDiv "
                                ),
                            ],
                            className="chartContainer",
                        ),       
                    ], 
                    className="eight columns"
                ),
            ],
            className="flex-display"
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
        ),
    ],
    className="mainContainer",
    id="",
)


# Callback 
#############################################################################


@app.callback(
    Output("df-hidden-div", "children"),
    [Input("csvDropdown", "value")],
)
def get_df(csv_filename):
    """Get the pandas dataframe from CSV.

    Parameters
    ----------
    csv_filename : str

    Returns
    -------
    str
        JSON-ified pandas dataframe
    """
    if csv_filename is None:
        # csv_filename is None when the dashboard app spins up.
        return INITIAL_DF.to_json()

    csv_path = os.path.join(LOCAL_DATA_DIR, csv_filename)

    if os.path.exists(csv_path):
        # If the CSV already exists on disk (during dev), just use it.
        pass
    else:
        # The CSV has to come from Civis Platform.
        file_id = civis.find_one(CSV_FILES, file_name=csv_filename)
        if file_id is None:
            raise ValueError(f"CSV file not retrievable without a Civis file ID")
        with open(csv_path, "wb") as f:
            civis.io.civis_to_file(file_id, f)
    df = preprocess_df(pd.read_csv(csv_path))

    return df.to_json()


# Callback inputs will all be the same
@app.callback(
    [
        Output('outputLineChart0', 'figure'),
        Output('outputLineChart1', 'figure'),
        Output('outputLineChart2', 'figure'),
        Output('outputLineChart3', 'figure'),
        Output('outputLineChart4', 'figure'),
        Output('outputLineChart5', 'figure'),
    ],

    [
        Input('df-hidden-div', 'children'),
        Input('emsDropdown', 'value'),
        Input('timeSlider', 'value'),
        # Unpack the elements of the list using *
        *[Input(param + 'Slider', 'value') for param in PARAMS]
    ],
)
def generateOutput(jsonified_df, emsValue, timeValues, *paramValues):
    df = pd.read_json(jsonified_df)

    # Generate query string for EMS value and range of sliders
    emsString = "({0} == '{1}')".format('emsGroup', emsValue)
    # Rangeslider passes values for the bottom and top of the range as a list [bottom, top]
    # Filter RangeSlider for timeValues - inclusive of selected timeframe
    timeString = "({0} >= '{1}') & ({0} <= '{2}')".format('week', unixToDt(timeValues[0]).strftime("%Y-%m-%d"), unixToDt(timeValues[1]).strftime("%Y-%m-%d")) 
    # Filter RangeSlider for Parameter Values
    paramString = " & ".join(["(`{0}` >= {1}) & (`{0}` <= {2})".format(param, pvalue[0], pvalue[1]) for param, pvalue in zip(PARAMS, paramValues)])
    strings = [emsString, timeString, paramString]
    queryString = " & ".join(strings)

    # Filter data frame given the slider inputs
    dff = df.query(queryString)

    # List of columns to group by
    groupbyList = ['date']
    
    def getQuantile(n):
        ''' Function to generate quantiles for groupby, returns quantile '''
        def _getQuantile(x):
            return x.quantile(n)
        _getQuantile.__name__ = 'quantile_{:2.2f}'.format(n*100)
        return _getQuantile

    # Function list passed to aggregation
    func_list = ['mean', 'sum', getQuantile(.025), getQuantile(.975), getQuantile(.25), getQuantile(.75)]

    #dfg[[output_list[0]]].mean().reset_index()['date']
    dfg = dff.groupby(groupbyList)[OUTPUTS].agg(func_list).reset_index()


    def makeChart (outputVar):

        # Generate Figure for plotting
        figure = go.Figure()

        # Add traces - shades between IQR and 2.5-97.5
        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_2.50')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=colors['green'], width=0), 
                    fill=None,
                )
            )

        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_97.50')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=colors['green'], width=0),
                    fill='tonexty', # fill area between this and previous trace
                )
            )

        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_25.00')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=colors['green'], width=0), 
                    fill=None,
                )
            )

        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_75.00')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=colors['green'], width=0),
                    fill='tonexty',
                    
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
    return [makeChart(output) for output in OUTPUTS]


if __name__ == '__main__':
    app.run_server(debug=True)



# TODOS
# ----- DONE Update Title & Subtitle
# ----- DONE Add note for refresh timing
# ----- DONE Add ability to choose multiple EMS groups (checkbox or multi-select dropdown)
# ----- DONE Add slider for Week-chooser
