#!/usr/bin/env python
# coding: utf-8

app_version = "v02"
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

import pandas as pd 
import plotly.express as px

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

# dataset_path = "./data/final/DIERX_Test.csv"
dataset_path = "http://partnersupport.neacon.eu/Dierx/print_values.php?auth=cordiplan"
locations_path = "./data/final/DIERX_Locations.csv"

# Read data from file 'filename.csv'
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

correct_payload_type_list = ['psh']  # only messeaured values are used

dataset_error = dataset[~dataset['payload_type'].isin(correct_payload_type_list)].copy()
dataset_error['datum_dt'] = pd.to_datetime(dataset_error['date-time_dt']).dt.date
dataset_error['tijdstip_dt'] = pd.to_datetime(dataset_error['date-time_dt']).dt.time
dataset_error['tijdstip_str'] = dataset_error['tijdstip_dt'].astype(str)
dataset_error['uur_str'] = dataset_error['tijdstip_str'].str[:2]
dataset_error['uniek_id'] = dataset_error['IMEI_str'] + "|" + dataset_error['payload_1']
# set dt column as index
dataset_error.set_index('date-time_dt', inplace=True)
# sort on index
dataset_error.sort_index(inplace=True)

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

merged = pd.merge(dataset_correct, locations, left_on='IMEI_str', right_on='serienr')
# print(merged.head())

merged['uniek_id'] = merged['IMEI_str'] + "|" + merged['Adres']

# https://strftime.org/
merged['date-time_dt'] = pd.to_datetime(dataset['date-time_str'], format='%Y-%m-%d %H:%M:%S')

# set dt column as index
merged.set_index('date-time_dt', inplace=True)

# sort on index
merged.sort_index(inplace=True)

# sort the municipality names also
all_location_names = sorted(merged["uniek_id"].unique().tolist())
location_names = [{"label": i, "value": i} for i in all_location_names]

current_fig = px.line(merged, x="date-time_str", y="payload_1",
                      color='uniek_id', title="Gemeten opbrengst",
                      labels={'date-time_str': 'datum / tijdstip',
                              'payload_1': 'gemeten kWh',
                              'uniek_id': 'DeviceId|Lokatie'}
                      )

cumulative_fig = px.line(merged, x="date-time_str", y="payload_2",
                         color='uniek_id', title="Cumulatieve opbrengst",
                         labels={'date-time_str': 'datum / tijdstip',
                                 'payload_2': 'gemeten kWh',
                                 'uniek_id': 'DeviceId|Lokatie'}
                         )

errordots_fig = px.scatter(dataset_error, x="datum_dt", y='uur_str',
                           color='uniek_id', title="Error Messages",
                           labels={'datum_dt': 'datum',
                                   'uur_str': 'tijdstip',
                                   'uniek_id': 'DeviceId|Foutcode'},
                           category_orders={
                               "uur_str": ['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                                           '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']},
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
app.layout = html.Div(
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
        # CENTER ROW
        # ==========

        html.Br([], ),
        rows.LOCATION_SELECTION_ROW("Selecteer lokatie(s)", location_names, all_location_names),
        html.Br([], ),

        dbc.Row(
            [
                # LEFT COLUMN
                # ============
                dbc.Col(
                    [
                    ],
                    width=4,
                    # style={"height": "400px"},
                ),
                # RIGHT COLUMN
                # ============
                dbc.Col(
                    [
                        # Adding Loading animation before map is shown
                        dcc.Loading(
                            id="loading-map",
                            type="default",
                            children=[
                                dcc.Graph(figure=current_fig),
                                dcc.Graph(figure=cumulative_fig),
                                dcc.Graph(figure=errordots_fig)
                                ]
                                ),
                        html.Br(),
                    ],
                    width=8,
                    # style={"height": "400px"},
                ),
            ],
            style={"paddingTop": "10px"},
        ),
        # BELOW THE MAP AND SELECTIONS
        # ============================
        html.Br(),
        footer.build_footer(),
    ],
    id="data-screen",
    # style={
    #     "border-style": "solid",
    #     "height": "98vh"
    # }
)


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
