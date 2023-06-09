# ############################################################################
#
# GEEN FUNCTIES/LOGICA UITVOEREN IN DIT BESTAND.
# ENKEL BEDOELD OM EEN LAYOUT ELEMENT TE DEFINIEREN
# AANPASSINGEN VIA CALLBACK OUTPUTS
#
# @version    v0.0.6  2023-05-31
# @author     pierre@amultis.eu
# @copyright  (C) 2020-2023 Pierre Veelen
#
# ############################################################################
#
# - styling in .\assets\styles.css
#                 python <-> css
#                tagname <-> tagname
#             id=some-id <-> #some-id
#   className=some-class <-> .some-class
#
# ############################################################################

import dash_bootstrap_components as dbc
from dash import html


# https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
def build_footer():
    """
    Returns an HTML Footer element for the application Footer.

    :return: HTML Footer
    """
    return html.Footer(
        children=[footer_row_top(), footer_row_center(), footer_row_bottom()],
        # className="footer",
    )


def footer_row_top():
    return dbc.Row(
        children=[],
        # className="logo-footer-centering",
        id="footer-row-top",
    )


def footer_row_center():
    return dbc.Row(
        children=[
            html.A(
                href="https://amultis.eu/de-aanpak-van/data-analytics-data-visualisatie/",
                target="_blank",
                className="footer-container",
                children=[
                    html.H4(children=["Powered by"], className="footer-element",),
                    html.Img(
                        src="./assets/img/amultis/amultis-logos-01.png",
                        id="amultis-icon",
                        className="footer-element",
                        style={"height": "2em", "display": "inline-block"},
                    ),
                    html.H4(
                        children=["aMultis Data Visualisations"],
                        className="footer-element",
                    ),
                    # html.Img(
                    #     src="assets/ipheion_logo_2020.png",
                    #     id="amultis-text",
                    #     className="footer-element",
                    # ),
                ],
            ),
        ],
        # className="logo-footer-centering",
        id="footer-row-center",
    )


def footer_row_bottom():
    return dbc.Row(
        children=[],
        id="footer-row-bottom",
        # className="logo-footer-centering",
    )
