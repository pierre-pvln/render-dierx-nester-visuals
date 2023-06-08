#!/usr/bin/env python
# coding: utf-8

app_version = "v06"
# put the name of this python file in txt file for processing by other scripts
with open("_current_app_version.txt", "w") as version_file:
    version_file.write(app_version + "\n")

import json
import os
import socket
import sys

# Visualization modules
import dash
import dash_bootstrap_components as dbc

import plotly
from dash import Dash, dcc, html
from dash.dash_table.Format import Align, Format, Group
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd 

import urllib3
import certifi

# authentication
import dash_auth_personal

# settings for strings
from config import strings

# app layout elements
from html_layouts import debug, footer, header, rows

# ==================================================
# DEFINE GENERICALLY USED VARS
# ==================================================
# initialize some globally used vars

run_environment = "production"
#run_environment = "tst"

if run_environment == "tst":
    glb_verbose = True  # True
    glb_fxn_verbose = 3  # 3
    # 0 = Don't output anything from function
    # 1 = Show only function name
    # 2 = Show function input values
    # 3 = Show additional info
    glb_hide_debug_text = False
elif run_environment == "acc":
    glb_verbose = True  # True
    glb_fxn_verbose = 2  # 2
    # 0 = Don't output anything from function
    # 1 = Show only function name
    # 2 = Show function input values
    # 3 = Show additional info
    glb_hide_debug_text = False
else:  # assumes production => minimum output
    glb_verbose = False
    glb_fxn_verbose = 0
    # 0 = Don't output anything from function
    # 1 = Show only function name
    # 2 = Show function input values
    # 3 = Show additional info
    glb_hide_debug_text = True


try:
    valid_username_password_pairs = json.loads(os.getenv("APP_AUTHENTICATION", default=None))
except Exception as e:
    valid_username_password_pairs = None
    print("[EXCEPTION]", e)

o_glb_header_subtitle = strings.HEADER_SUBTITLE  # the value of the location name in the selectionbox


# SYSTEM AND APP INFO
# =============================================
the_hostname = socket.gethostname()
run_on = os.getenv("RUN_LOCATION", "local")
if run_on.lower() in ["heroku"]:
    glb_verbose = False
python_version = sys.version.split()[0]
dash_version = dash.__version__
plotly_version = plotly.__version__

print("[INFO     ] Run environment:", run_environment)
print("[INFO     ] running on     : " + the_hostname)
print("[INFO     ] run on env var : " + run_on)
print("[INFO     ] app version    : " + app_version)
print("[INFO     ] python version : " + python_version)
print("[INFO     ] dash version   : " + dash_version)
print("[INFO     ] plotly version : " + plotly_version)
print("[INFO     ] authentication : configured") if valid_username_password_pairs is not None else print("[INFO     ] authentication : not configured")

# =============================================
# GETTING THE DATA
# =============================================

# dataset_path = "./data/final/DIERX_Test2.csv"
dataset_path = "http://partnersupport.neacon.eu/Dierx/print_values.php?auth=cordiplan"
locations_path = "./data/final/DIERX_Locations.csv"

if "http" not in dataset_path:
    # Read data from file 'filename.csv'
    dataset = pd.read_csv(dataset_path, sep=";", header=None, dtype=str)
else:
    # # Creating a PoolManager instance for sending requests.
    # https = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())
    # # Sending a GET request and getting back response as HTTPResponse object.
    #
    # dataset_path_URL = "https://partnersupport.neacon.eu/Dierx/print_values.php"
    # payload = {'auth': 'cordiplan'}
    #
    # response = https.request(
    #     "GET", dataset_path, fields=payload, retries=urllib3.Retry(total=40, status=40, redirect=40)
    # )
    #
    # # Print the returned data.
    # print(response.data)
    dataset = pd.read_csv(dataset_path, sep=";", header=None, dtype=str)

# name columns
dataset.columns =['IMEI_str', 'date-time_str', 'payload']

# remove de '<br> at the end of the payload string
# only valid for http download
dataset['payload'] = dataset['payload'].str.replace(r'<br>$', '', regex=True)

# Split payload column into two new columns
dataset[['payload_type', 'payload_1', 'payload_2']] = dataset.payload.str.split(":", expand=True)

# https://strftime.org/
dataset['date-time_dt'] = pd.to_datetime(dataset['date-time_str'], format='%Y-%m-%d %H:%M:%S')
dataset['date-time_dt'] = pd.to_datetime(dataset['date-time_str'], format='%Y-%m-%d %H:%M:%S')
dataset['datum_dt'] = pd.to_datetime(dataset['date-time_dt']).dt.date
dataset['datum_str'] = dataset['datum_dt'].astype(str)
dataset['tijdstip_dt'] = pd.to_datetime(dataset['date-time_dt']).dt.time
dataset['tijdstip_str'] = dataset['tijdstip_dt'].astype(str)
dataset['uur_str'] = dataset['tijdstip_str'].str[:2]

correct_payload_type_list = ['psh']  # only messeaured values are used

glb_dataset_error = dataset[~dataset['payload_type'].isin(correct_payload_type_list)].copy()
glb_dataset_error['uniek_id'] = glb_dataset_error['IMEI_str'] + "|" + glb_dataset_error['payload_1']
# set dt column as index
glb_dataset_error.set_index('date-time_dt', inplace=True)
# sort on index
glb_dataset_error.sort_index(inplace=True)

dataset_correct = dataset[dataset['payload_type'].isin(correct_payload_type_list)].copy()

filtered_dataset = dataset_correct
dataset_correct[['payload_1', 'payload_2']] = dataset_correct[['payload_1', 'payload_2']].astype(float)

# Preview the first 5 lines of the loaded data
# print(dataset.head())
# print(dataset.dtypes)
# print(dataset['IMEI_str'].unique())

# Read data from file 'filename.csv'
locations = pd.read_csv(locations_path, sep=";", dtype=str) 

locations['Adres'] = locations['Straat'] + " " + locations['Huisnummer'] + " " + locations['Postcode'] + " " + locations['Plaats']

# Preview the first 5 lines of the loaded data 
# print(locations.head())
# print(locations.dtypes)
# print(locations['serienr'].unique())

glb_merged = pd.merge(dataset_correct, locations, left_on='IMEI_str', right_on='serienr')
# print(merged.head())

glb_merged['uniek_id'] = glb_merged['IMEI_str'] + "|" + glb_merged['Adres']

# https://strftime.org/
glb_merged['date-time_dt'] = pd.to_datetime(dataset['date-time_str'], format='%Y-%m-%d %H:%M:%S')

# set dt column as index
glb_merged.set_index('date-time_dt', inplace=True)

# sort on index
glb_merged.sort_index(inplace=True)

# ==================================================
# DROPDOWN / SLIDER INPUT DEFINITIONS
# ==================================================
# DROPDOWN locations
# ==================================================
# get the list with dicts for the location dropdown selection
# https://dash.plotly.com/dash-core-components/dropdown#options-and-value
all_location_names = sorted(glb_merged["uniek_id"].unique().tolist())
location_names = [
    {"label": i.split("|")[1],  # Get the last part of the 'uniek_id' which is the 'Adres' this is shown in dropdownbox
     "value": i.split("|")[0]}  # Get the first part of the 'uniek_id' which is the 'IMEI' this is the value returned
    for i in all_location_names
]
# use the IMEI part as the all_location_names
all_location_names = [i.split("|")[0] for i in all_location_names]
#print(location_names)
#print(all_location_names)

# DATESLIDER
# ==================================================
date_list = sorted(glb_merged['datum_str'].unique().tolist())
#print(date_list)
glb_dateslider_marks_dict = {}

for i in range(0, len(date_list)):
    glb_dateslider_marks_dict[i] = {'label': date_list[i],
                                    "style": {"marginTop": "20px",
                                              "marginLeft": "-30px",
                                              "transform": "rotate(-90deg)"}
                                        }
#print(glb_dateslider_marks_dict)


# ==================================================
# LAYOUT DEFINITIONS
# ==================================================
# ToDo move to module section
def GRAPHS_ROW(id_name, config_name, figure_dict, verbosity=False):
    return dbc.Row(
                # row with graph
                [
                    # first create a col. this ensures full use of row length
                    dbc.Col([
                        # Show a "spinner" until graph has loaded.
                        # To create this effect, add the graph as child of the loading
                        dcc.Loading(
                            # https://dash.plotly.com/dash-core-components/loading
                            id="loading_"+id_name,
                            type="default",
                            children=[
                                dcc.Graph(
                                    # https://dash.plotly.com/dash-core-components/graph
                                    id=id_name,
                                    figure=figure_dict,  # initialize with empty figure
                                    style={
                                    #    "height": "400px",
                                        "width": "100%"
                                    },
                                    config=config_name,
                                )
                            ],
                        ),
                    ],
                    ),
                ],
            )

# ToDo move to module section
def settings_graph_modebar(file_name):
    return dict(
        # https://plotly.com/javascript/configuration-options/#never-display-the-modebar
        displayModeBar="hover",
        # True : always show modebar
        # False: never show mode bar
        # "hover": only show modebar when hovering over graph

        # https://plotly.com/javascript/configuration-options/#remove-modebar-buttons
        modeBarButtonsToRemove=['lasso2d', 'select2d', 'pan2d',
                                'toggleSpikelines', 'toggleHover',
                                'hoverClosestCartesian', 'hoverCompareCartesian',
                                'hoverClosestGl2d'],

        # https://plotly.com/javascript/configuration-options/#customize-download-plot-options
        toImageButtonOptions=dict(
            format='png',  # one of 'png', 'svg', 'jpeg', 'webp'
            filename=file_name,
            height=500,
            width=700,
            scale=1  # Multiply title / legend / axis / canvas sizes by this factor
        ),

        # https://plotly.com/javascript/configuration-options/#hide-the-plotly-logo-on-the-modebar
        displaylogo=True  # Either True or False
    )


# ========================================= #
#                                           #
# Define the web/html layout for the app    #
#                                           #
# - more details are defined in layouts.py  #
#                                           #
# ========================================= #
def OVERALL_APP_LAYOUT():
    empty_fig = go.Figure()

    return html.Div(
    [
        # TOP ROW / HEADER ROW
        # ====================
        # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
        header.build_header(
            title_str=strings.HEADER_TITLE,
            subtitle_str=o_glb_header_subtitle,
            version_str=app_version,
        ),
        debug.build_header(
            dbg_str="-* debug text here *-",  # start with empty debug text
            hide_it=glb_hide_debug_text,
        ),
        html.Br([], ),

        # CENTER ROW
        # ==========
        rows.LOCATION_SELECTION_ROW("Selecteer lokatie(s)", location_names, all_location_names),
        html.Br([], ),

        rows.DATESLIDER_SELECTION_ROW("Selecteer datum range", glb_dateslider_marks_dict, int(len(glb_dateslider_marks_dict) / 2)),
        html.Br([], ),

        GRAPHS_ROW("current_fig", settings_graph_modebar('current_graph'), empty_fig),
        GRAPHS_ROW("cumulative_fig", settings_graph_modebar('cumulative_graph'), empty_fig),
        GRAPHS_ROW("modulesdots_fig", settings_graph_modebar('modulesdots_graph'), empty_fig, ),
        GRAPHS_ROW("errordots_fig", settings_graph_modebar('errordots_graph'), empty_fig,),
        html.Br([], ),

        # BELOW THE ROWS
        # ============================
        html.Br([], ),

        # BOTTOM ROW / FOOTER ROW
        # ====================
        footer.build_footer(),
        html.Br([], ),
    ],
    id="data-screen",
    # style={
    #     "border-style": "solid",
    #     "height": "98vh"
    # }
)


# ==================================================
# APP DEFINITIONS
# ==================================================
external_stylesheets = [
    # https://bootswatch.com/zephyr/
    dbc.themes.ZEPHYR,
    # For Bootstrap Icons...
    dbc.icons.BOOTSTRAP,
]

app = Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=external_stylesheets,
)

# ToDo look into this. Authentication should return the logged-in username
# - the basic auth has to be updated
# - check if we can get userid from it
if valid_username_password_pairs is not None:
    print(valid_username_password_pairs)
    # adding authentication
    auth = dash_auth_personal.BasicAuth(
        app,
        valid_username_password_pairs
    )

app.title = strings.APP_TITLE
app.config["update_title"] = ".. Renewing .."
# ToDo html page title to location that is viewed
# https://dash.plotly.com/external-resources -> Update the Document Title Dynamically Based on the URL or Tab


# app.config["suppress_callback_exceptions"] = True  # default is False
# suppress_callback_exceptions: check callbacks to ensure referenced IDs exist and props are valid.
# Set to True if your layout is dynamic, to bypass these checks.

if the_hostname not in ["LEGION-2020"]:
    server = app.server  # required for Heroku

# ==================================================
# APP LAYOUT
# ==================================================
app.layout = OVERALL_APP_LAYOUT()


####################################################
# UPDATE GRAPHS
####################################################
# UPDATE current_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('current_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection', 'value'),  # use value from switch
    Input('date-slider-selection', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
)
def current_fig(data_to_show_list, dates_to_use):
    global glb_merged
    global glb_dateslider_marks_dict

#    print('current_fig')
#    print(data_to_show_list)
#    print(glb_merged.columns)

    start_date_str = glb_dateslider_marks_dict[dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[dates_to_use[1]]['label']

    mask = (glb_merged['datum_str'] >= start_date_str) & (glb_merged['datum_str'] <= end_date_str)
    dates_subset_df = glb_merged.loc[mask]

    output_fig = px.line(dates_subset_df[dates_subset_df["IMEI_str"].isin(data_to_show_list)],
                         x="date-time_str",
                         y="payload_1",
                         color='uniek_id',
                         title="Gemeten opbrengst",
                         labels={'date-time_str': 'datum / tijdstip',
                                 'payload_1': 'gemeten kWh',
                                 'uniek_id': 'DeviceId|Lokatie'},
                         markers=True,
                         )

    #    output_fig.update_traces(line=dict(dash="dot", width=4, color="red"),
    #                             marker=dict(color="darkblue", size=20, opacity=0.8))
    output_fig.update_traces(marker=dict(opacity=0.5))

    return output_fig


# UPDATE cumulative_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('cumulative_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection', 'value'),  # use value from switch
    Input('date-slider-selection', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
)
def cumulative_fig(data_to_show_list, dates_to_use):
    global glb_merged
    global glb_dateslider_marks_dict

    start_date_str = glb_dateslider_marks_dict[dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[dates_to_use[1]]['label']

    mask = (glb_merged['datum_str'] >= start_date_str) & (glb_merged['datum_str'] <= end_date_str)
    dates_subset_df = glb_merged.loc[mask]

    output_fig = px.line(dates_subset_df[dates_subset_df["IMEI_str"].isin(data_to_show_list)],
                         x="date-time_str",
                         y="payload_2",
                         color='uniek_id',
                         title="Cumulatieve opbrengst",
                         labels={'date-time_str': 'datum / tijdstip',
                                 'payload_2': 'gemeten kWh',
                                 'uniek_id': 'DeviceId|Lokatie'},
                         markers=True,
                         )

#    output_fig.update_traces(line=dict(dash="dot", width=4, color="red"),
#                             marker=dict(color="darkblue", size=20, opacity=0.8))

    output_fig.update_traces(marker=dict(opacity=0.5))

    return output_fig


# UPDATE errordots_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('errordots_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection', 'value'),  # use value from switch
    Input('date-slider-selection', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
)
def error_dots_fig(data_to_show_list, dates_to_use):
    global glb_dataset_error
    global glb_dateslider_marks_dict

#    print('error_dots_fig')
#    print(data_to_show_list)
#    print(dates_to_use)
#    print(glb_dataset_error)

    start_date_str = glb_dateslider_marks_dict[dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[dates_to_use[1]]['label']

    mask = (glb_dataset_error['datum_str'] >= start_date_str) & (glb_dataset_error['datum_str'] <= end_date_str)
    dates_subset_df = glb_dataset_error.loc[mask]

    output_fig = px.scatter(dates_subset_df[dates_subset_df["IMEI_str"].isin(data_to_show_list)],
                            x="datum_dt",
                            y='uur_str',
                            color='uniek_id',
                            title="Error Messages",
                            labels={'datum_dt': 'datum',
                                    'uur_str': 'tijdstip',
                                    'uniek_id': 'DeviceId|Foutcode'},
                            category_orders={
                                   "uur_str": ['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                                               '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']
                                },
                            )
    return output_fig

# UPDATE modulesdots_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('modulesdots_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection', 'value'),  # use value from switch
    Input('date-slider-selection', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
)
def module_dots_fig(data_to_show_list, dates_to_use):
    global glb_merged
    global glb_dateslider_marks_dict

#    print('error_dots_fig')
#    print(data_to_show_list)
#    print(dates_to_use)
#    print(glb_dataset_error)

    start_date_str = glb_dateslider_marks_dict[dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[dates_to_use[1]]['label']

    # Select the datapoints within the given dates
    mask = (glb_merged['datum_str'] >= start_date_str) & (glb_merged['datum_str'] <= end_date_str)
    dates_subset_df = glb_merged.loc[mask]

    # select the datapoints for the IEMI's
    pivot_df = pd.pivot_table(dates_subset_df[dates_subset_df["IMEI_str"].isin(data_to_show_list)],
                              values='payload',
                              aggfunc='count',
                              index='datum_str',
                              columns='uur_str')

    # flatten pivot data
    wide_df = pd.DataFrame(pivot_df.to_records())
    wide_df.fillna(0, inplace=True)
    # print(wide_df)

    # create long df for easy plotting
    long_df = pd.melt(wide_df,
                      id_vars='datum_str',
                      value_vars=['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                                  '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00'])
    # print(long_df)

    output_fig = px.scatter(long_df,
                            x="datum_str",
                            y='variable',
                            size='value',
                            title="Aantal berichten van modules",
                            labels={'datum_str': 'datum',
                                    'variable': 'tijdstip'},
                            category_orders={
                                   "variable": ['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                                                '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']
                                   },
                            height=800,
                            )

    output_fig.update_layout(yaxis=dict(tickvals=['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                                                  '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']))
    return output_fig


# ==================================================
# START THE APP
# ==================================================
if __name__ == "__main__":
    # local development machine
    if the_hostname == "LEGION-2020":
        app.run_server(
            debug=True, use_reloader=False
        )  # Turn off reloader if inside Jupyter

    # on Heroku / render
    else:
        app.run_server(
            debug=True, use_reloader=False
        )  # Turn off reloader if inside Jupyter
