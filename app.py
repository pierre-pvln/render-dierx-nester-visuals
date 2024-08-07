""" graph_test

"""
#!/usr/bin/env python
# coding: utf-8

app_version = "v20"
# put the name of this python file in txt file for processing by other scripts
with open("_current_app_version.txt", "w") as version_file:
    version_file.write(app_version + "\n")

# import module to trace the memomry allocation of this app
import tracemalloc

import json
import os
import socket
import sys

import pandas as pd

# Visualization modules
import dash
import dash_bootstrap_components as dbc

import plotly
from dash import Dash, dcc, html, callback
# from dash.dash_table.Format import Align, Format, Group
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

import urllib3
import certifi

# authentication
import dash_auth_personal

# local settings from subfolders of this app
from dcc_graphs.configs.modebars import graph_modebar
# app layout elements
from html_layouts import debug, footer, header, rows
# settings for strings
from config import strings


# ==================================================
# GENERIC/UTILITY FUNCTIONS
# ==================================================
def loc_info(locationspath, locationslist, api_key):
    info_df = pd.DataFrame()

    if "https://" not in locations_path:  # use a local file
        info_df = pd.read_csv(locationspath, sep=";", dtype=str)
        info_df['Adres'] = info_df['Straat'] + " " + info_df['Huisnummer'] + " " + info_df['Postcode'] + " " + info_df['Plaats']

    else:  # retrieve data from API
        https = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

        headers = {"Content-Type": "application/json",
                   "Accept": "*/*",
                   "Accept-Encoding": "gzip, deflate, br",
                   "x-api-key": api_key
                   }

        for locationid in locationslist:
            # print(locationid)
            base_url = locations_path + str(locationid)
            # print(base_url)

            # retrieve location info for locationid = IMEI code
            response = https.request(method='GET',
                                     headers=headers,
                                     url=base_url,
                                     )

            data_json_dict = json.loads(response.data.decode('utf-8'))
            #print(data_json_dict)

            for index in range(data_json_dict['Count']):  # Should be only 1 item, but to be sure loop over it
                # print(data_json_dict['Items'][index])
                serienr = data_json_dict['Items'][index]['SerieNr']['S']
                plaats = data_json_dict['Items'][index]['Plaats']['S']
                postcode = data_json_dict['Items'][index]['Postcode']['S']
                straat = data_json_dict['Items'][index]['Straat']['S']
                huisnummer = data_json_dict['Items'][index]['Huisnummer']['S']
                adres = straat + " " + huisnummer + " " + postcode + " " + plaats
                datadict = {'Adres': adres,
                            'Straat': straat,
                            'Huisnummer': huisnummer,
                            'Postcode': postcode,
                            'Plaats': plaats,
                            'serienr': serienr}

                # print(pd.DataFrame([datadict]))

                info_df = pd.concat([info_df, pd.DataFrame([datadict])], ignore_index=True)

    return info_df


def retrieve_sim_data(data_url):
    datasetinput = pd.read_html(data_url, header=0)  # returns a list of df's
    df_raw = pd.concat(datasetinput)
    datasetinput = []  # clean the datasetinput data

    all_columns = False

    # 'sensor1': '868333032573210',  # Kastanjelaan 1
    # ========================================
    extended_columns = ['TimeStamp', 'SensorID', 'ValueTypeID', 'REAL Value']
    if all_columns:
        df1 = df_raw[extended_columns + ['TimeStamp_1', 'Value_1']].copy()
    else:
        df1 = df_raw[['TimeStamp_1', 'Value_1']].copy()
    df1.rename(columns={'TimeStamp_1': 'date-time_str', 'Value_1': 'payload_1'}, inplace=True)
    df1.sort_values(by=['date-time_str'], inplace=True)
    df1['temp_kwh'] = df1['payload_1']*20/60
    df1['payload_2'] = df1['temp_kwh'].cumsum()
    df1.drop(columns=['temp_kwh'], inplace=True)
    df1['IMEI_str'] = '868333032573210'

    # 'sensor2': '868333032564722',  # St Jozefweg 50
    # ========================================
    if all_columns:
        df2 = df_raw[extended_columns + ['TimeStamp_2', 'Value_2']].copy()
    else:
        df2 = df_raw[['TimeStamp_2', 'Value_2']].copy()
    df2.rename(columns={'TimeStamp_2': 'date-time_str', 'Value_2': 'payload_1'}, inplace=True)
    df2.sort_values(by=['date-time_str'], inplace=True)
    df2['temp_kwh'] = df2['payload_1']*20/60
    df2['payload_2'] = df2['temp_kwh'].cumsum()
    df2.drop(columns=['temp_kwh'], inplace=True)
    df2['IMEI_str'] = '868333032564722'

    # 'sensor3': '868333032947257',  # St Jozefweg 49
    # ========================================
    if all_columns:
        df3 = df_raw[extended_columns + ['TimeStamp_3', 'Value_3']].copy()
    else:
        df3 = df_raw[['TimeStamp_3', 'Value_3']].copy()
    df3.rename(columns={'TimeStamp_3': 'date-time_str', 'Value_3': 'payload_1'}, inplace=True)
    df3.sort_values(by=['date-time_str'], inplace=True)
    df3['temp_kwh'] = df3['payload_1']*20/60
    df3['payload_2'] = df3['temp_kwh'].cumsum()
    df3.drop(columns=['temp_kwh'], inplace=True)
    df3['IMEI_str'] = '868333032947257'

    # 'sensor4': '868333036363584',  # Goud Es-laan 12
    # ========================================
    if all_columns:
        df4 = df_raw[extended_columns + ['TimeStamp_4', 'Value_4']].copy()
    else:
        df4 = df_raw[['TimeStamp_4', 'Value_4']].copy()
    df4.rename(columns={'TimeStamp_4': 'date-time_str', 'Value_4': 'payload_1'}, inplace=True)
    df4.sort_values(by=['date-time_str'], inplace=True)
    df4['temp_kwh'] = df4['payload_1']*20/60
    df4['payload_2'] = df4['temp_kwh'].cumsum()
    df4.drop(columns=['temp_kwh'], inplace=True)
    df4['IMEI_str'] = '868333036363584'

    # 'sensor5': '868333032833069',  # Goud Es-laan 11
    # ========================================
    if all_columns:
        df5 = df_raw[extended_columns + ['TimeStamp_5', 'Value_5']].copy()
    else:
        df5 = df_raw[['TimeStamp_5', 'Value_5']].copy()
    df5.rename(columns={'TimeStamp_5': 'date-time_str', 'Value_5': 'payload_1'}, inplace=True)
    df5.sort_values(by=['date-time_str'], inplace=True)
    # set startdate for goud es 11 (868333032833069) and eikenlaan 9 (868333032402170) to 17 mei
    # thus remove all data before that date
    df5 = df5.drop(df5[(df5['date-time_str'] < '2023-05-17 00:00:00')].index)
    df5['temp_kwh'] = df5['payload_1']*20/60
    df5['payload_2'] = df5['temp_kwh'].cumsum()
    df5.drop(columns=['temp_kwh'], inplace=True)
    df5['IMEI_str'] = '868333032833069'

    # 'sensor6': '868333032402170',  # Eikenlaan 9
    # ========================================
    if all_columns:
        df6 = df_raw[extended_columns + ['TimeStamp_6', 'Value_6']].copy()
    else:
        df6 = df_raw[['TimeStamp_6', 'Value_6']].copy()
    df6.rename(columns={'TimeStamp_6': 'date-time_str', 'Value_6': 'payload_1'}, inplace=True)
    df6.sort_values(by=['date-time_str'], inplace=True)
    # set startdate for goud es 11 (868333032833069) and eikenlaan 9 (868333032402170) to 17 mei
    # thus remove all data before that date
    df6 = df6.drop(df6[(df6['date-time_str'] < '2023-05-17 00:00:00')].index)
    df6['temp_kwh'] = df6['payload_1']*20/60
    df6['payload_2'] = df6['temp_kwh'].cumsum()
    df6.drop(columns=['temp_kwh'], inplace=True)
    df6['IMEI_str'] = '868333032402170'

    # 'sensor7': '868333036364624',  # Goud Es-laan 5
    # ========================================
    if all_columns:
        df7 = df_raw[extended_columns + ['TimeStamp_7', 'Value_7']].copy()
    else:
        df7 = df_raw[['TimeStamp_7', 'Value_7']].copy()
    df7.rename(columns={'TimeStamp_7': 'date-time_str', 'Value_7': 'payload_1'}, inplace=True)
    df7.sort_values(by=['date-time_str'], inplace=True)
    df7['temp_kwh'] = df7['payload_1']*20/60
    df7['payload_2'] = df7['temp_kwh'].cumsum()
    df7.drop(columns=['temp_kwh'], inplace=True)
    df7['IMEI_str'] = '868333036364624'

    # 'sensor8': '868333035034327',  # Micha
    # ========================================
    if all_columns:
        df8 = df_raw[extended_columns + ['TimeStamp_8', 'Value_8']].copy()
    else:
        df8 = df_raw[['TimeStamp_8', 'Value_8']].copy()
    df8.rename(columns={'TimeStamp_8': 'date-time_str', 'Value_8': 'payload_1'}, inplace=True)
    df8.sort_values(by=['date-time_str'], inplace=True)
    df8['temp_kwh'] = df8['payload_1']*20/60
    df8['payload_2'] = df8['temp_kwh'].cumsum()
    df8.drop(columns=['temp_kwh'], inplace=True)
    df8['IMEI_str'] = '868333035034327'

    # 'sensor9': '868333035023122',  # Dierx
    # ========================================
    if all_columns:
        df9 = df_raw[extended_columns + ['TimeStamp_9', 'Value_9']].copy()
    else:
        df9 = df_raw[['TimeStamp_9', 'Value_9']].copy()
    df9.rename(columns={'TimeStamp_9': 'date-time_str', 'Value_9': 'payload_1'}, inplace=True)
    df9.sort_values(by=['date-time_str'], inplace=True)
    df9['temp_kwh'] = df9['payload_1']*20/60
    df9['payload_2'] = df9['temp_kwh'].cumsum()
    df9.drop(columns=['temp_kwh'], inplace=True)
    df9['IMEI_str'] = '868333035023122'

    df_raw = pd.DataFrame()  # clean df_raw

    df_set = [df1, df2, df3, df4, df5, df6, df7, df8, df9]
    df = pd.concat(df_set)
    df_set = []  # clean df_set

    # print(df.columns)
    # print(df)
    # df.to_csv("simulated.csv", sep=";")
    # df.to_excel("simulated.xlsx")

    df_out = df[['IMEI_str', 'date-time_str', 'payload_1', 'payload_2']].copy()
    df = pd.DataFrame()  # clean the df data

    df_out.dropna(inplace=True)
    df_out['date-time_str'] = df_out['date-time_str'].str[:-3]
    df_out['payload_type'] = 'psh'
    df_out['payload_1'] = df_out['payload_1'].astype(str)
    df_out['payload_2'] = df_out['payload_2'].astype(str)
    # print(df_out.columns)
    # print(df_out.dtypes)

    # print(df_out.columns)
    # print(df_out)

    # df_out.to_csv("OUTsimulated.csv", sep=";", index=False, header=False)
    # df_out.to_excel("OUTsimulated.xlsx", index=False, header=False)

    return df_out


# ==================================================
# LOAD DATASET
# ==================================================
def load_dataset(base_url, data_period):
    global glb_location_names
    global glb_all_location_names
    global glb_dateslider_marks_dict
    global glb_dataset_correct
    global glb_dataset_error
    global glb_merged_dataset

    #print(data_period)
    dataset_path = base_url + "convert.php?date=" + data_period
    dataset = retrieve_sim_data(dataset_path)

    # set the message type (unknown, error or correct)
    dataset['msg_type'] = 'unkown'
    correct_payload_type_list = ['psh']  # only measured values are used
    error_payload_type_list = ['err']  # only measured values are used
    dataset.loc[dataset['payload_type'].isin(correct_payload_type_list), 'msg_type'] = 'correct'
    dataset.loc[dataset['payload_type'].isin(error_payload_type_list), 'msg_type'] = 'error'

    # https://strftime.org/
    dataset['date-time_dt'] = pd.to_datetime(dataset['date-time_str'], format='%Y-%m-%d %H:%M:%S')
    dataset['datum_dt'] = pd.to_datetime(dataset['date-time_dt']).dt.date
    dataset['datum_str'] = dataset['datum_dt'].astype(str)
    dataset['tijdstip_dt'] = pd.to_datetime(dataset['date-time_dt']).dt.time
    dataset['tijdstip_str'] = dataset['tijdstip_dt'].astype(str)
    dataset['uur_str'] = dataset['tijdstip_str'].str[:2]

    # get the locations info
    serienr_list = dataset['IMEI_str'].unique().tolist()
    # print(serienr_list)
    locations = loc_info(locations_path, serienr_list, aws_api_gw_key)

    # combine data with location
    glb_merged_dataset = pd.merge(dataset, locations, how='left', left_on='IMEI_str', right_on='serienr')

    # make sure that a new location/device is detected => merged['adres'] = NaN => "ONBEKEND ADRES"
    glb_merged_dataset["Adres"] = glb_merged_dataset["Adres"].fillna("ONBEKEND ADRES")
    glb_merged_dataset['uniek_id'] = glb_merged_dataset['IMEI_str'] + "|" + glb_merged_dataset['Adres']

    glb_merged_dataset.sort_values(by=['datum_dt', 'uniek_id'], ignore_index=True, inplace=True)
    # glb_merged_dataset.to_csv('./glb_merged_dataset.csv')

    # print(glb_merged_dataset.columns)

    glb_dataset_error = glb_merged_dataset[glb_merged_dataset['msg_type'] == 'error'].copy()
    glb_dataset_error['uniek_id_err_msg'] = glb_dataset_error['IMEI_str'] + "|" + glb_dataset_error['Adres'] + "|" + \
                                            glb_dataset_error['payload_1']
    # set dt column as index
    glb_dataset_error.set_index('date-time_dt', inplace=True)
    # sort on index
    glb_dataset_error.sort_index(inplace=True)
    # glb_dataset_error.to_csv('./glb_dataset_error.csv')

    glb_dataset_correct = glb_merged_dataset[glb_merged_dataset['msg_type'] == 'correct'].copy()
    glb_dataset_correct[['payload_1', 'payload_2']] = glb_dataset_correct[['payload_1', 'payload_2']].astype(float)
    glb_dataset_correct['uniek_id'] = glb_dataset_correct['IMEI_str'] + "|" + glb_dataset_correct['Adres']
    # set dt column as index
    glb_dataset_correct.set_index('date-time_dt', inplace=True)
    # sort on index
    glb_dataset_correct.sort_index(inplace=True)
    # glb_dataset_correct.to_csv('./glb_dataset_correct.csv')

    # ==================================================
    # DROPDOWN / SLIDER INPUT DEFINITIONS
    # ==================================================

    # DROPDOWN locations
    # ==================================================
    # get the list with dicts for the location dropdown selection
    # https://dash.plotly.com/dash-core-components/dropdown#options-and-value
    glb_all_location_names = sorted(glb_dataset_correct["uniek_id"].unique().tolist())
    glb_location_names = [
        {"label": i.split("|")[1],
         # Get the last part of the 'uniek_id' which is the 'Adres' this is shown in dropdownbox
         "value": i.split("|")[0]}
        # Get the first part of the 'uniek_id' which is the 'IMEI' this is the value returned
        for i in glb_all_location_names
    ]
    # use the IMEI part as the all_location_names
    glb_all_location_names = [i.split("|")[0] for i in glb_all_location_names]

    # DATESLIDER
    # ==================================================
    date_list = sorted(glb_dataset_correct['datum_str'].unique().tolist())
    # print(date_list)
    glb_dateslider_marks_dict = {}

    for i in range(0, len(date_list)):
        glb_dateslider_marks_dict[i] = {'label': date_list[i],
                                        "style": {"marginTop": "20px",
                                                  "marginLeft": "-30px",
                                                  "transform": "rotate(-90deg)"}
                                        }

    return


mem_insights_needed = False
if mem_insights_needed:
    tracemalloc.start()

# ==================================================
# DEFINE GENERICALLY USED VARS
# ==================================================
# initialize some globally used vars

run_environment = "production"
# run_environment = "tst"

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

# get the API key from environment var
aws_api_gw_key = os.getenv("AWS_API_GATEWAY_KEY", default=None)
# print(aws_api_gw_key)

try:
    valid_username_password_pairs = json.loads(os.getenv("APP_AUTHENTICATION", default=None))
except Exception as e:
    valid_username_password_pairs = None
    print("[EXCEPTION]", e)

o_glb_header_subtitle = strings.HEADER_SUBTITLE  # the value of the location name in the selectionbox

glb_periods_list = [
    {'label': '2023-05', 'value': '2023-05'},
    {'label': '2023-06', 'value': '2023-06'},
    {'label': '2023-07', 'value': '2023-07'},
    {'label': '2023-08', 'value': '2023-08'},
    {'label': '2023-09', 'value': '2023-09'},
    {'label': '2023-10', 'value': '2023-10'},
    {'label': '2023-11', 'value': '2023-11'},
    {'label': '2023-12', 'value': '2023-12'},
    {'label': '2024-01', 'value': '2024-01'},
    {'label': '2024-02', 'value': '2024-02'},
    {'label': '2024-03', 'value': '2024-03'},
    {'label': '2024-04', 'value': '2024-04'},
    {'label': '2024-05', 'value': '2024-05'},
    {'label': '2024-06', 'value': '2024-06'},
    {'label': '2024-07', 'value': '2024-07'},
]


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
locations_path = "https://cgemqjpjhg.execute-api.eu-central-1.amazonaws.com/v1/info/nester/"
glb_base_url = "http://partnersupport.neacon.eu/dshm/"

# Define globally used vars
# ========================
glb_location_names = []
glb_all_location_names = []
glb_dateslider_marks_dict = {}
glb_dataset_correct = pd.DataFrame()
glb_dataset_error = pd.DataFrame()
glb_merged_dataset = pd.DataFrame()

# ==================================================
# INITIAL load of dataset
# ==================================================
load_dataset(glb_base_url, glb_periods_list[0]['value'])


# ==================================================
# LAYOUT DEFINITIONS
# ==================================================
# ========================================= #
#                                           #
# Define the web/html layout for the app    #
#                                           #
# - more details are defined in:            #
#   .\html_layouts\*.py                     #
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
        rows.MONTH_RADIO_ROW(id_name='radio-item-selection',
                             SelectionText="Selecteer gewenste periode",
                             RadioItemOptions=glb_periods_list,
                             RadioItemValue="2024-02"),
        html.Br([], ),

        rows.LOCATION_SELECTION_ROW("Selecteer lokatie(s)", glb_location_names, glb_all_location_names),
        html.Br([], ),

        rows.DATESLIDER_SELECTION_ROW("Selecteer datum range", glb_dateslider_marks_dict, 0, len(glb_dateslider_marks_dict)-1),
        html.Br([], ),

        # showing measured power values
        rows.GRAPHS_ROW("current_fig", graph_modebar('current_graph'), empty_fig),
        rows.GRAPHS_ROW("cumulative_fig", graph_modebar('cumulative_graph'), empty_fig),

        # showing number of received data messages per module per day
        rows.GRAPHS_ROW("errordots_mod_fig", graph_modebar('errordots_graph'), empty_fig, ),  # showing per module info regarding data messages
        rows.GRAPHS_ROW("modulesdots_fig", graph_modebar('modulesdots_graph'), empty_fig, ),  # showing received messages per hour block per day. Size of dot is number of messages
        rows.GRAPHS_ROW("errordots_day_fig", graph_modebar('errordots_graph'), empty_fig, ),  # showing errors per hour per day.
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

# ==================================================
# UPDATE update_data_period SELECTION
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('location-selection-row', 'value'),  # updated locations
    Output('location-selection-row', 'options'),

    Output('date-slider-selection-row', 'marks'),  # updated dates
    Output('date-slider-selection-row', 'max'),
    Output('date-slider-selection-row', 'value'),

    # Changes in (one of) these fires this callback
    # =============================================
    Input('radio-item-selection', 'value')

    # Values passed without firing callback
    # =============================================
    # State('','')

    # Remarks
    # =============================================
    # Input vars in function should start with i_
    # State vars in function should start with s_
    # Output vars from function should start with o_
)
def update_data_period(i_period_to_use):
    global glb_all_location_names
    global glb_location_names
    global glb_dateslider_marks_dict

#    print('update_data_period')
#    print(i_period_to_use)
    load_dataset(glb_base_url, i_period_to_use)

#    print("updated data set")
#    print(glb_all_location_names)
#    print(glb_location_names)
#    print(glb_dateslider_marks_dict)

    return (
            glb_all_location_names,
            glb_location_names,

            glb_dateslider_marks_dict,  # marks
            len(glb_dateslider_marks_dict),  # max
            [0, len(glb_dateslider_marks_dict) - 1]  # value

            )

# ==================================================
# UPDATE current_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('current_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection-row', 'value'),  # use value from switch
    Input('date-slider-selection-row', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')

    # Remarks
    # =============================================
    # Input vars in function should start with i_
    # State vars in function should start with s_
    # Output vars from function should start with o_
)
def current_fig(
    # Input()
    # =============================================
    i_data_to_show_list,
    i_dates_to_use,

    # State()
    # =============================================
):
    global glb_dataset_correct
    global glb_dateslider_marks_dict
    global glb_location_names
    global glb_all_location_names

#    print('current_fig')
#    print(data_to_show_list)
#    print(glb_dataset_correct.columns)

#    print(" == aa ==")
#    print(glb_dateslider_marks_dict)

    start_date_str = glb_dateslider_marks_dict[i_dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[i_dates_to_use[1]]['label']

    mask = (glb_dataset_correct['datum_str'] >= start_date_str) & (glb_dataset_correct['datum_str'] <= end_date_str)
    dates_subset_df = glb_dataset_correct.loc[mask]

    output_fig = px.line(dates_subset_df[dates_subset_df["IMEI_str"].isin(i_data_to_show_list)],
                         x="date-time_str",
                         y="payload_1",
                         color='uniek_id',
                         title="Gemeten opbrengst in deze maand",
                         labels={'date-time_str': 'datum / tijdstip',
                                 'payload_1': 'gemeten kWh',
                                 'uniek_id': 'DeviceId|Lokatie'},
                         markers=True,
                         )

    #    output_fig.update_traces(line=dict(dash="dot", width=4, color="red"),
    #                             marker=dict(color="darkblue", size=20, opacity=0.8))
    output_fig.update_traces(marker=dict(opacity=0.5))

#    print("== current-fig ==")
#    print(glb_dateslider_marks_dict)

    return output_fig


# ==================================================
# UPDATE cumulative_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('cumulative_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection-row', 'value'),  # use value from switch
    Input('date-slider-selection-row', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
    
    # Remarks
    # =============================================
    # Input vars in function should start with i_
    # State vars in function should start with s_
    # Output vars from function should start with o_
)
def cumulative_fig(
    # Input()
    # =============================================
    i_data_to_show_list,
    i_dates_to_use,

    # State()
    # =============================================
):
    global glb_dataset_correct
    global glb_dateslider_marks_dict

#    print('cumulative_fig')
#    print(i_dates_to_use)
#    print(glb_dateslider_marks_dict)

    start_date_str = glb_dateslider_marks_dict[i_dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[i_dates_to_use[1]]['label']

    mask = (glb_dataset_correct['datum_str'] >= start_date_str) & (glb_dataset_correct['datum_str'] <= end_date_str)
    dates_subset_df = glb_dataset_correct.loc[mask]

    output_fig = px.line(dates_subset_df[dates_subset_df["IMEI_str"].isin(i_data_to_show_list)],
                         x="date-time_str",
                         y="payload_2",
                         color='uniek_id',
                         title="Cumulatieve opbrengst in deze maand",
                         labels={'date-time_str': 'datum / tijdstip',
                                 'payload_2': 'gemeten kWh',
                                 'uniek_id': 'DeviceId|Lokatie'},
                         markers=True,
                         )

#    output_fig.update_traces(line=dict(dash="dot", width=4, color="red"),
#                             marker=dict(color="darkblue", size=20, opacity=0.8))

    output_fig.update_traces(marker=dict(opacity=0.5))

    return output_fig


# ==================================================
# UPDATE errordots_day_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('errordots_day_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection-row', 'value'),  # use value from switch
    Input('date-slider-selection-row', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
    
    # Remarks
    # =============================================
    # Input vars in function should start with i_
    # State vars in function should start with s_
    # Output vars from function should start with o_
)
def error_dots_day_fig(
    # Input()
    # =============================================
    i_data_to_show_list,
    i_dates_to_use,

    # State()
    # =============================================
):
    global glb_dataset_error
    global glb_dateslider_marks_dict

#    print('error_dots_day_fig')

#    print('error_dots_fig')
#    print(data_to_show_list)
#    print(dates_to_use)
#    print(glb_dataset_error)

    start_date_str = glb_dateslider_marks_dict[i_dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[i_dates_to_use[1]]['label']

    mask = (glb_dataset_error['datum_str'] >= start_date_str) & (glb_dataset_error['datum_str'] <= end_date_str)
    dates_subset_df = glb_dataset_error.loc[mask]

#    print("== error_dots_day_fig ==")
#    print(i_data_to_show_list)
#    print(dates_subset_df.columns)

    output_fig = px.scatter(dates_subset_df[dates_subset_df["IMEI_str"].isin(i_data_to_show_list)],
                            x="datum_dt",
                            y='uur_str',
                            color='uniek_id_err_msg',
                            title="Aantal Error Messages per uur per module",
                            labels={'datum_dt': 'datum',
                                    'uur_str': 'tijdstip',
                                    'uniek_id_err_msg': 'DeviceId|Locatie|ErrorMsg'},
                            category_orders={
                                   "uur_str": ['23', '22', '21', '20', '19', '18', '17', '16', '15', '14', '13', '12',
                                               '11', '10', '09', '08', '07', '06', '05', '04', '03', '02', '01', '00']
                                },
                            )
    return output_fig


# ==================================================
# UPDATE errordots_mod_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('errordots_mod_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection-row', 'value'),  # use value from switch
    Input('date-slider-selection-row', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')

    # Remarks
    # =============================================
    # Input vars in function should start with i_
    # State vars in function should start with s_
    # Output vars from function should start with o_
)
def error_dots_mod_fig(
    # Input()
    # =============================================
    i_data_to_show_list,
    i_dates_to_use,

    # State()
    # =============================================
):
    global glb_merged_dataset
    global glb_dateslider_marks_dict

    #    print('error_dots_mod_fig')
    #    print('error_dots_fig')
    #    print(data_to_show_list)
    #    print(dates_to_use)
    #    print(glb_dataset_error)

    start_date_str = glb_dateslider_marks_dict[i_dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[i_dates_to_use[1]]['label']

    mask = (glb_merged_dataset['datum_str'] >= start_date_str) & (glb_merged_dataset['datum_str'] <= end_date_str)
    dates_subset_df = glb_merged_dataset.loc[mask].copy()
    dates_subset_df = dates_subset_df[dates_subset_df["IMEI_str"].isin(i_data_to_show_list)]

    # print(dates_subset_df[['uniek_id', 'IMEI_str', 'datum_dt']].columns)

    # now get the count of messages per IMEI_str per day and flatten the df
    pivoted_subset = pd.pivot_table(dates_subset_df[['uniek_id', 'datum_dt', 'msg_type', 'IMEI_str']],
                                    index=['datum_dt', 'uniek_id', 'msg_type'],
                                    values=['IMEI_str'],
                                    aggfunc='count',
                                    )

    pivot_flat = pd.DataFrame(pivoted_subset.to_records())

    # print(pivot_flat.columns)
    # print(pivot_flat.head())

    pivot_flat.rename(columns={'IMEI_str': 'Count'}, inplace=True)

    uniek_id_list = pivot_flat['uniek_id'].unique().tolist()
    datum_dt_list = pivot_flat['datum_dt'].unique().tolist()
    for an_id in uniek_id_list:
        # print(an_id)
        sub_pivot_flat = pivot_flat.loc[pivot_flat["uniek_id"] == an_id]  # select the records related to an_id
        dates_list = sub_pivot_flat['datum_dt'].unique().tolist()  # create a list of dates that are present
        # print(dates_list)
        append_dates_list = list(set(datum_dt_list) - set(dates_list))  # find missing dates to append
        for append_date in append_dates_list:
            new_row = {'uniek_id': an_id, 'datum_dt': append_date, 'Count': 0}
            # print(new_row)
            # Use the loc method to add the new row to the DataFrame
            pivot_flat.loc[len(pivot_flat)] = new_row

    pivot_flat.sort_values(by=['datum_dt', 'uniek_id'], ignore_index=True, inplace=True)

    max_count = pivot_flat.loc[pivot_flat['msg_type'] == 'correct', 'Count'].max()  # get max value of correct messages

    pivot_flat['Status'] = "Sending data"
    pivot_flat['Color'] = "#000000"  # black

    pivot_flat.loc[pivot_flat['Count'] == max_count, 'Status'] = 'Sending maximum data'
    pivot_flat.loc[pivot_flat['Count'] < max_count/2, 'Status'] = 'Sending some data'
    pivot_flat.loc[pivot_flat['Count'] < max_count/4, 'Status'] = 'Sending insufficient data'
    pivot_flat.loc[pivot_flat['Count'] == 0, 'Status'] = 'Sending no data'

    pivot_flat.loc[pivot_flat['msg_type'] == 'error', 'Status'] = 'Sending data with errors'

    #    terms = ['mbus_none', '"mbus_none"']
#    pivot_flat.loc[pivot_flat['uniek_id'].str.contains('|'.join(terms)), 'Status'] = 'Sending data with errors'

    # Using Dictionary for mapping
    color_map = {'Sending maximum data': '#006400',  # dark green
                 'Sending data': '#00ff00',  # green
                 'Sending some data': '#ff6200',  # dark orange
                 'Sending insufficient data': '#ff8c00',  # orange
                 'Sending no data': '#ff0000',  # red
                 "Sending data with errors": '#0000ff'  # blue
                 }

    #pivot_flat['Color'] = pivot_flat['Status'].map(color_map)
    pivot_flat['Size'] = pivot_flat['Count'].fillna(0)
    pivot_flat['Size'] = pivot_flat['Count'].replace([0, 1, 2, 3], 4)  # replace Count with 4 to see the dot

    # print(pivot_flat)
    # print(pivot_flat.columns)

    output_fig = px.scatter(pivot_flat,
                            x="datum_dt",
                            y='uniek_id',
                            color='Status',
                            size='Size',
                            title="Status datacommunicatie per module",
                            hover_name='uniek_id',  # column data shown bold in hoverbox
                            hover_data={'uniek_id': False,  # customize hover text, don't show all columns
                                        'Count': True,
                                        'Status': True,
#                                        'Color': False,
                                        'Size': False,
                                        'datum_dt': True
                                        },
                            color_discrete_map=color_map,
                            labels={'datum_dt': 'datum',
                                    'uniek_id': 'DeviceId|Locatie',
                                    'Status': 'Unit communication status'},
                            category_orders={"Status": ['Sending data',  # order in legend
                                                        'Sending some data',
                                                        'Sending insufficient data',
                                                        'Sending no data',
                                                        'Sending data with errors',
                                                        'Sending maximum data'
                                                        ]}
                            )

    output_fig.layout.update(showlegend=True)
    # output_fig.update_traces(marker=dict(
    #                              symbol="circle",  # name of icon in icon set or "circle"
    #                              size=[
    #                                  16
    #                                  if x in ["Sending maximum data"]
    #                                  else 10
    #                                  if x in ['Sending data', 'Sending some data', 'Sending insufficient data']
    #                                  else 6
    #                                  if x in ['Sending data with errors', 'Sending no data']
    #                                  else 4
    #                                  for x in list(pivot_flat['Status'])
    #                              ],
    #                              color=[
    #                                  "#00FF00" if x == "Sending data"  # green
    #                                  else "#FF6200" if x == "Sending some data"  # dark orange
    #                                  else "#FF8C00" if x == "Sending insufficient data"  # orange
    #                                  else "#FF0000" if x == "Sending no data"  # red
    #                                  else "#0000FF" if x == "Sending data with errors"  # blue
    #                                  else "#FF00FF"  # magenta
    #                                  for x in list(pivot_flat["Status"])
    #                              ],
    #                              opacity=1,
    #                          ),
    #                          )
    # #output_fig.update_traces(marker=dict(color=list(pivot_flat['Color'])))

    return output_fig


# ==================================================
# UPDATE modulesdots_fig GRAPH
# ==================================================
@app.callback(
    # Where the results of the function end up
    # =======================================
    Output('modulesdots_fig', 'figure'),  # updated figure based on input changes

    # Changes in (one of) these fires this callback
    # =============================================
    Input('location-selection-row', 'value'),  # use value from switch
    Input('date-slider-selection-row', 'value'),  # use value from switch

    # Values passed without firing callback
    # =============================================
    # State('','')
    
    # Remarks
    # =============================================
    # Input vars in function should start with i_
    # State vars in function should start with s_
    # Output vars from function should start with o_
)
def module_dots_fig(
    # Input()
    # =============================================
    i_data_to_show_list,
    i_dates_to_use,


    # State()
    # =============================================
):

    global glb_dataset_correct
    global glb_dateslider_marks_dict

#    print('module_dots_fig')
#    print('error_dots_fig')
#    print(data_to_show_list)
#    print(dates_to_use)
#    print(glb_dataset_error)

    start_date_str = glb_dateslider_marks_dict[i_dates_to_use[0]]['label']
    end_date_str = glb_dateslider_marks_dict[i_dates_to_use[1]]['label']

    # Select the datapoints within the given dates
    mask = (glb_dataset_correct['datum_str'] >= start_date_str) & (glb_dataset_correct['datum_str'] <= end_date_str)
    dates_subset_df = glb_dataset_correct.loc[mask]

    # select the datapoints for the IEMI's
    pivot_df = pd.pivot_table(dates_subset_df[dates_subset_df["IMEI_str"].isin(i_data_to_show_list)],
                              values='payload_type',
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
                            title="Aantal berichten (per uur) van alle modules samen",
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

    print("[INFO     ] Python app finished")

    if mem_insights_needed:
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        print("[ Top 10 ]")
        for stat in top_stats[:10]:
            print(stat)

        # stopping the library
        tracemalloc.stop()
