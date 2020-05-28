# -*- coding: utf-8 -*-
# Operational Libs
import collections
import functools
import logging
import os

# Dash Libs
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, ALL

# Analytic Libs
import pandas as pd
import numpy as np
import math

LOG = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

# In production, the CSV files are at this project on Civis Platform:
# https://platform.civisanalytics.com/spa/#/projects/135876
CIVIS_PROJECT_ID = 135876

LOCAL_DATA_DIR = "data"
DEV_CSV_FILENAMES = [
    "dash_trajectoriesDat_baseline.csv",  # file ID: 103222548
    "dash_trajectoriesDat_june1partial10.csv",  # file ID: 103222598
    "dash_trajectoriesDat_june1partial30.csv",  # file ID: 103222650
]

EMS_MAPPING = {"North-Central": (1, 2), "Central": (3, 6), "Southern": (4, 5), "Northeast": (7, 8, 9, 10, 11)}

N_SLIDER_MARKS = 5
N_CHART_COLUMNS = 2

app = dash.Dash(__name__, prevent_initial_callbacks=True)

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
    CSV_FILES = [
        CSVFile(id=None, file_name=file_name)
        for file_name in DEV_CSV_FILENAMES
    ]


# Setup 
#############################################################################

# Color Options 
COLORS = {
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


@functools.lru_cache(maxsize=4)
def get_df(csv_file_path):
    """Get pandas DataFrame from CSV and apply pre-processing.

    Parameters
    ----------
    csv_file_path : str

    Returns
    -------
    pd.DataFrame
    """
    df = pd.read_csv(csv_file_path)
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


def get_param_slider(param, i, marks):
    return html.Div(
        style={"margin": "25px 5px 30px 0px"},
        children=[
            html.Div(
                style={"margin-left": "5px"},
                children=[
                    html.P(
                        param.replace("param_", "").upper(),
                        className="control_label",
                    ),
                    dcc.RangeSlider(
                        id={
                            "type": "parameter",
                            "index": i,
                        },
                        step=None,
                        marks={
                            m: "{:.1%}".format(m) if m < 1 else "{:.2f}".format(m)
                            for m in marks
                        },
                        min=marks[0],
                        max=marks[-1],
                        value=[marks[0], marks[-1]],
                    )
                ]
            )
        ]
    )


def get_formatted_charts(charts, columns=N_CHART_COLUMNS):
    result = []
    charts_in_row = []

    for chart in charts:
        if len(charts_in_row) == columns:
            div = html.Div(
                charts_in_row,
                className="flex-display chartContainerDiv ",
            )
            result.append(div)
            charts_in_row = []
        graph = dcc.Graph(figure=chart)
        charts_in_row.append(html.Div([graph], className="graphDiv"))

    if charts_in_row:
        div = html.Div(
            charts_in_row,
            className="flex-display chartContainerDiv ",
        )
        result.append(div)

    return result


def get_param_names(df):
    """Get the parameter names from df.

    Since the parameters are dynamically retrieved from the df,
    this function ensures that we have a consistent and correct mapping
    between their names and values across the callbacks.
    """
    return sorted(col for col in df.columns if col.startswith("param_"))


def get_week_slider(df):
    dates = sorted(df["month"].unique())
    week_slider = [
        dcc.RangeSlider(
            id="timeSlider",
            min=dtToUnix(dates[0]),
            max=dtToUnix(dates[-1]),
            value=[dtToUnix(dates[0]), dtToUnix(dates[-1])],
            marks= {
                dtToUnix(dt): {
                    'label': np.datetime_as_string(dt, unit='M'),
                    'style': {
                        'transform':'rotate(45deg)',
                        'font-size':'8px',
                    }
                } for i, dt in enumerate(dates)
            },
            allowCross=False,
            className="",
        ),
    ]
    return week_slider


def get_param_sliders(df):
    sliders = []

    for i, param in enumerate(get_param_names(df)):
        marks = np.linspace(
            math.floor(df[param].min() * 1000) / 1000,
            math.ceil(df[param].max() * 1000) / 1000,
            N_SLIDER_MARKS,
        )
        slider = get_param_slider(param, i, marks)
        sliders.append(slider)

    return sliders


# Main App Layout
#############################################################################
app.layout = html.Div(
    children = [
        html.Div(id="div-csv-file-name", style={"display": "none"}),
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
                                html.Div(
                                    # `children` is dynamically updated.
                                    [dcc.RangeSlider(
                                        id="timeSlider",
                                        min=dtToUnix(np.datetime64("2020-02")),
                                        max=dtToUnix(np.datetime64("2021-02")),
                                        value=[dtToUnix(np.datetime64("2020-02")),
                                               dtToUnix(np.datetime64("2021-02"))],
                                    )],
                                    className="dcc_control",
                                    id="week-slider",
                                ),
                            ],
                            className="time-container",
                        ),
                        # Parameter Sliders
                        html.Div(
                            [
                                html.P(
                                    "Filter Graphs by Model Parameters:",
                                    className="control_label",
                                ),
                                html.Div(
                                    # `children` is dynamically updated.
                                    [get_param_slider("", 0, [0, 1])],
                                    className="dcc_control",
                                    id="param-sliders",
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
                        html.Div(
                            id="output-charts",
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
    [
        Output("week-slider", "children"),
        Output("param-sliders", "children"),
    ],
    [Input("div-csv-file-name", "children")],
)
def set_sliders(csv_file_path):
    df = get_df(csv_file_path)
    week_slider = get_week_slider(df)
    param_sliders = get_param_sliders(df)
    return week_slider, param_sliders


@app.callback(
    Output("div-csv-file-name", "children"),
    [Input("csvDropdown", "value")],
)
@functools.lru_cache(maxsize=4)
def set_csv_file_name_and_download(csv_filename):
    """Set CSV file path in the app and download the CSV.

    Parameters
    ----------
    csv_filename : str

    Returns
    -------
    str
        CSV file path
    """
    if not os.path.exists(LOCAL_DATA_DIR):
        os.mkdir(LOCAL_DATA_DIR)
    csv_path = os.path.join(LOCAL_DATA_DIR, csv_filename)

    if os.path.exists(csv_path):
        # If the CSV already exists on disk, just use it.
        pass
    else:
        # The CSV has to come from Civis Platform.
        file_id = civis.find_one(CSV_FILES, file_name=csv_filename).id
        if file_id is None:
            raise ValueError(f"CSV file not retrievable without a Civis file ID")
        civis.io.civis_to_file(file_id, csv_path)
        logging.info("CSV downloaded to %s", csv_path)
    return csv_path


@app.callback(
    Output("output-charts", "children"),
    [
        Input('div-csv-file-name', 'children'),
        Input('emsDropdown', 'value'),
        Input('timeSlider', 'value'),
        Input({"type": "parameter", "index": ALL}, "value"),
    ],
)
def generateOutput(csv_file_path, emsValue, timeValues, paramValues):
    df = get_df(csv_file_path)
    params = get_param_names(df)

    # Generate query string for EMS value and range of sliders
    emsString = "({0} == '{1}')".format('emsGroup', emsValue)
    # Rangeslider passes values for the bottom and top of the range as a list [bottom, top]
    # Filter RangeSlider for timeValues - inclusive of selected timeframe
    timeString = "({0} >= '{1}') & ({0} <= '{2}')".format('week', unixToDt(timeValues[0]).strftime("%Y-%m-%d"), unixToDt(timeValues[1]).strftime("%Y-%m-%d"))
    # Filter RangeSlider for Parameter Values
    paramString = " & ".join(["(`{0}` >= {1}) & (`{0}` <= {2})".format(param, pvalue[0], pvalue[1]) for param, pvalue in zip(params, paramValues)])
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

    outputs = sorted(col for col in df.columns if col.startswith("output_"))
    dfg = dff.groupby(groupbyList)[outputs].agg(func_list).reset_index()

    def makeChart (outputVar):

        # Generate Figure for plotting
        figure = go.Figure()

        # Add traces - shades between IQR and 2.5-97.5
        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_2.50')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=COLORS['green'], width=0),
                    fill=None,
                )
            )

        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_97.50')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=COLORS['green'], width=0),
                    fill='tonexty', # fill area between this and previous trace
                )
            )

        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_25.00')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=COLORS['green'], width=0),
                    fill=None,
                )
            )

        figure.add_trace(go.Scatter(
                    x=dfg['date'],
                    y=dfg.loc[:, (outputVar, 'quantile_75.00')],
                    mode='lines',
                    opacity=0.3,
                    line=dict(color=COLORS['green'], width=0),
                    fill='tonexty',
                    
                )
            )

        figure.update_layout(
            font=dict(
                family="Open Sans, monospace",
                size=14,
                color=COLORS['green']
            ),
            title=outputVar.replace("output_", "").upper() + " by Date",
            showlegend=False,
            yaxis=dict(
                tickformat="<,f",
                gridcolor=COLORS['beige'],
                gridwidth=2,
            ),
            xaxis=dict(
                showgrid=False,
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
        )

        return figure

    charts = [makeChart(output) for output in outputs]
    return get_formatted_charts(charts)


if __name__ == '__main__':
    app.run_server(debug=True)
