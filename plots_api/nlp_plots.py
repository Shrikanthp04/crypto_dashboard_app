import re
import time
import dash
import pandas as pd
from io import StringIO
from dash import dcc, html
import plotly.graph_objs as go
from db_qa_api.utils import sk_query
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
from django.templatetags.static import static
from dash.dependencies import Input, Output, State


external_bootstrap_styles = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
static_css_path = "/static/styles.css"
url = static('/images/download.png')

app = DjangoDash('nlp_plots', external_stylesheets=[external_bootstrap_styles, static_css_path, url])

nlp_question = ' '
global_dataframe = None
csv_string = None

app.layout = dbc.Container([
    
    html.Div("Ask Your Query in English", className='text-center fw-bold', style={'color': 'white'}),
    html.Div([
    dcc.Textarea(
            id="input",
            value='',
            placeholder="Please enter your query",
            className="textarea1 form-control mt-2",
            style={
                "width": "55%",
                "height": "45px",
                "resize": "none",
                "outline":"none",
                "border-radius": "4px",
                "border-color": "#bfbfbf",
                "overflow-y": "auto",
                "font-size": "12px",
                "padding":'6px',
            }
        ),
    html.Button('Submit', id='submit-button', n_clicks=0, className="btn btn-primary btn-sm me-3 mt-2 ms-2", style={"height":'45px'}),

    html.Div([
    html.Div(
        "Graph Types",
        style={'font-size': '12px', 'font-weight': 'bold', 'color': '#fff', 'text-align':'center'}
    ),
    dcc.Dropdown(
        id="select-chart",
        options=[
            {'label': 'Table', 'value': 'table'},
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Bar Graph', 'value': 'bar'},
        ],
        value='table',
        style={'width': '88px', 'font-size': '12px', 'padding': '0px', 'margin': '0px'},
        maxHeight=100,
        optionHeight=20,
        clearable=False,
         searchable=False,
    )
    ], className="justify-content-center me-1"),


     html.Div([
         
            html.Div([
                html.Div("x axis", id='x-label', style={'font-size': '12px', 'font-weight': 'bold', 'color': '#fff', 'text-align':'center'}),
                dcc.Dropdown(
                    id='x-axis',
                    placeholder="Select a column",
                    style={'width': '104px', 'font-size': '10px', 'padding': '0px'},
                    maxHeight=100,
                    optionHeight=20,
                    clearable=False,
                    searchable=False,
                )
            ], id='x-axis-dropdown', className='justify-content-center me-2 ms-1'),



            html.Div([
                html.Div("y axis", id='y-label', style={'font-size': '12px', 'font-weight': 'bold', 'color': '#fff', 'text-align':'center'}),
                dcc.Dropdown(
                    id='y-axis',
                    placeholder="Select a column ",
                    style={'width': '104px', 'font-size': '10px', 'padding': '0px'},
                    maxHeight=100,
                    optionHeight=20,
                    clearable=False,
                     searchable=False,
                ),
            ], id='y-axis-dropdown', className='justify-content-center me-1'),
        ], className='d-flex justify-content-center', id='column_selectors'),

        
        html.Div([
            html.Div(" . ", style={'height': '14px'}),
            html.Button('Show', id='show-button', n_clicks=0, className="btn btn-primary btn-sm", style={'height':'34px'}),
        ])

    ], className="d-flex"),

 

    html.Div(id="flex-box-space", children=[
        dcc.Loading(id="loading-2", children=[
            html.Div(id="loading-output-1"),
            html.Div(id="cls-output-2", className='output-example-loading', style={'margin-top': '45px'}),
        ], type="circle"),
    ], style={'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '100%'}),


    html.Div([
        dcc.Graph(id="charts", style={'height': '255px'}, config={
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'toImage', 'zoom2d', 'autoScale2d'],'displaylogo': False
        }),
    ], className='d-flex justify-content-center'),

    html.Div([
        html.Div(id='output-table', style={'margin-right': '10px', 'margin-left': '10px', 'height': '255px'}),
    ], className='d-flex justify-content-center', style={'margin-left': '25px'}),

], fluid=True)


def check_compare(sentence):
    words = sentence.split()
    compare_forms = ["compare", "compares", "comparing", "compared", "comparison", "comparisons", "comparative", "comparatively"]
    return any(word.lower() in compare_forms for word in words)


def extract_selected_cryptos(sentence):
    return [c.upper() for c in re.findall(r'\b([a-zA-Z]{3,4})\b', sentence) if c.upper() in ['BTC', 'ETH', 'USDT']]


def compare_crypto(question, x_value, y_value):
    cryptos = extract_selected_cryptos(question)
    unique_fromsymbol_count = global_dataframe['CRYPTO_TYPES'].nunique()

    fig = go.Figure()
    if unique_fromsymbol_count > 2:
        btc = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[0]]
        eth = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[1]]
        usdt = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[2]]
        fig.add_trace(go.Bar(x=btc[x_value], y=btc[y_value], name=cryptos[0].upper(), text=btc[y_value]))
        fig.add_trace(go.Bar(x=eth[x_value], y=eth[y_value], name=cryptos[1].upper(), text=eth[y_value]))
        fig.add_trace(go.Bar(x=usdt[x_value], y=usdt[y_value], name=cryptos[2].upper(), text=usdt[y_value]))
    else:
        btc = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[0]]
        eth = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[1]]
        fig.add_trace(go.Bar(x=btc[x_value], y=btc[y_value], name=cryptos[0].upper(), text=btc[y_value]))
        fig.add_trace(go.Bar(x=eth[x_value], y=eth[y_value], name=cryptos[1].upper(), text=eth[y_value]))

    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(
        uniformtext_minsize=8, uniformtext_mode='hide',
        template='plotly_dark',
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(family='Arial', size=12),
        showlegend=True,
        xaxis=dict(
            title=x_value,
            visible=True,
            showgrid=False,
            tickfont=dict(family='Arial', size=12),
        ),
        yaxis=dict(
            title=y_value,
            visible=True,
            showgrid=True,
            tickfont=dict(family='Arial', size=12),
            gridcolor='rgba(255, 255, 255, 0.1)',
        ),
    )
    return fig


def extract_selected_currencies(sentence):
    return [c.upper() for c in re.findall(r'\b([a-zA-Z]{3})\b', sentence) if c.upper() in ['USD', 'INR', 'EUR']]



def compare_currency(question, x_value, y_value):
    currencies = extract_selected_currencies(question)
    unique_fromsymbol_count = global_dataframe['CURRENCY_TYPES'].nunique()

    fig = go.Figure()
    if unique_fromsymbol_count > 2:
        usd = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[0]]
        inr = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[1]]
        eur = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[2]]
        fig.add_trace(go.Bar(x=usd[x_value], y=usd[y_value], name=currencies[0].upper(), text=usd[y_value]))
        fig.add_trace(go.Bar(x=inr[x_value], y=inr[y_value], name=currencies[1].upper(), text=inr[y_value]))
        fig.add_trace(go.Bar(x=eur[x_value], y=eur[y_value], name=currencies[2].upper(), text=eur[y_value]))
    else:
        usd = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[0]]
        inr = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[1]]
        fig.add_trace(go.Bar(x=usd[x_value], y=usd[y_value], name=currencies[0].upper(), text=usd[y_value]))
        fig.add_trace(go.Bar(x=inr[x_value], y=inr[y_value], name=currencies[1].upper(), text=inr[y_value]))
    
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    fig.update_layout(
        uniformtext_minsize=8, uniformtext_mode='hide',
        template='plotly_dark',
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(family='Arial', size=12),
        showlegend=True,
        xaxis=dict(
            title=x_value,
            visible=True,
            showgrid=False,
            tickfont=dict(family='Arial', size=12),
        ),
        yaxis=dict(
            title=y_value,
            visible=True,
            showgrid=True,
            tickfont=dict(family='Arial', size=12),
            gridcolor='rgba(255, 255, 255, 0.1)',
        ),
    )
    return fig


def generate_table(dataframe):
    global csv_string  
    
    df = dataframe.copy()
    if df is None or df.empty:
        return html.Div("No data available for selected query", className="alert alert-warning")
    
    num_cols = df.select_dtypes(include='number').columns
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: '{:,.0f}'.format(x) if abs(x) < 1000 else '{:,.2f}K'.format(x / 1000) if abs(x) < 1000000 else '{:,.2f}M'.format(x / 1000000) if abs(x) < 1000000000 else '{:,.2f}B'.format(x / 1000000000) if abs(x) < 1000000000000 else '{:,.2f}T'.format(x / 1000000000000))

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_string = csv_buffer.getvalue()
    
    return html.Div(
        [
            html.Div(
                [ 
                    html.Table([
                        html.Thead(
                            html.Tr([
                                html.Th(col, style={'padding-left': '20px', 'background-color': '#009879'}) if col != df.columns[-1] else html.Th([col , html.Button(html.Img(src=url, style={'width': '20px', 'height': '20px', 'background-color': '#009879', 'border': 'none'}), id="btn-download", style={'background-color': '#009879', 'border': 'none', 'float': 'right'})], style={'padding-left': '20px', 'background-color': '#009879'}) for col in df.columns
                            ])),
                        html.Tbody([
                            html.Tr([
                                html.Td(df.iloc[i][col]) if col != df.columns[0] else html.Td(style={'padding-left': '20px'}, children=df.iloc[i][col]) if col != df.columns[-1] else html.Td(style={'padding-right': '20px'}, children=df.iloc[i][col]) for col in df.columns
                            ]) for i in range(len(df))
                        ])
                    ], className='styled-table'),
                ],
                className="table-container"
            ),
            dcc.Download(id="download-dataframe")
        ],
        style={'maxHeight': '255px', 'overflowY': 'auto', 'overflowX': 'hidden', 'border-radius':'10px'},
    )


@app.callback(
    Output("download-dataframe", "data"),
    [Input("btn-download", "n_clicks")],
    prevent_initial_call=True
)
def download_dataframe(n_clicks):
    global csv_string 
    if n_clicks is not None:
        return dict(content=csv_string, filename="dataframe.csv")
    

@app.callback(
    [Output('x-axis', 'options'),
     Output('x-axis-dropdown', 'style'),
     Output('y-axis', 'options'),
     Output('y-axis-dropdown', 'style')],
    [Input("select-chart", "value"),
     Input("submit-button", "n_clicks")],
    [State("input", "value")]
)
def update_axis(selected_chart, submit_n_clicks, query):
    global global_dataframe
    if not selected_chart or selected_chart == 'table':
        return [], {'display': 'none'}, [], {'display': 'none'}
    
    if submit_n_clicks > 0 and check_compare(query):
        selected_chart = 'bar'

    options = [{'label': col, 'value': col} for col in global_dataframe.columns] if global_dataframe is not None and not global_dataframe.empty else []
    return options, {'display': 'block'}, options, {'display': 'block'}


@app.callback(
    [Output("charts", "figure"),
     Output("charts", "style"),
     Output("output-table", "style"),
     Output("output-table", "children"),
     Output("x-axis", "value"),
     Output("y-axis", "value"),
     Output("select-chart", "value"),
     Output("cls-output-2", "children"),Output("cls-output-2", "style"),
     Output("loading-output-1", "children"),Output("loading-output-1", "style"), Output("flex-box-space", 'style'),],
    [Input("submit-button", "n_clicks"),
     Input("show-button", 'n_clicks'),
     Input("loading-2", "loading_state"),],
    [State("input", "value"),
     State("select-chart", "value"),
     State("x-axis", "value"),
     State("y-axis", "value")]
)
def update_charts(submit_n_clicks, show_n_clicks, loading_state, query, selected_chart, x_value=None, y_value=None):
    global nlp_question, global_dataframe
    reset_x_value = None
    reset_y_value = None
    reset_chart_value = selected_chart
    ctx = dash.callback_context

    if submit_n_clicks > 0 and ctx.triggered:
        if "submit-button" == ctx.triggered[0]['prop_id'].split('.')[0]:
            reset_x_value = None
            reset_y_value = None
            reset_chart_value = selected_chart
            query = query.strip() if query else ''
            formatted_query = re.sub(r'\s+', ' ', query)

            if formatted_query == '':
                time.sleep(1)
                return (
                    {}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, 
                    html.Div("Please Enter Your Query, Input Cannot be Empty.", className="alert alert-warning"), 
                    reset_x_value, reset_y_value, 'table', 
                    None, {'display': 'none'} if loading_state is not None else {'display': 'block'}, 
                    None, {'display': 'none', 'margin-top': '0px'} if loading_state is not None else {'display': 'block', 'margin-top': '45px'}, 
                    {'display': 'none', 'width': '0px', 'height': '0px', 'flex-direction': 'row', 'align-items': 'start'} if loading_state is not None else {'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '100%'})

            if formatted_query != nlp_question:
                selected_chart = 'table'
                nlp_question = formatted_query
                sql_query, df = sk_query(nlp_question)
                
                if df.empty or df is None:  
                    time.sleep(1)
                    return (
                        {}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, 
                        html.Div("No data available for selected query", className="alert alert-warning"), 
                        reset_x_value, reset_y_value, 'table', 
                        None, {'display': 'none'} if loading_state is not None else {'display': 'block'}, 
                        None, {'display': 'none', 'margin-top': '0px'} if loading_state is not None else {'display': 'block', 'margin-top': '45px'}, 
                        {'display': 'none', 'width': '0px', 'height': '0px', 'flex-direction': 'row', 'align-items': 'start'} if loading_state is not None else {'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '100%'})
        
                if 'LASTUPDATE' in df.columns:
                    df['LASTUPDATE'] = pd.to_datetime(df['LASTUPDATE'],format="%Y-%m-%d %H:%M:%S")
                    df['DATE'] = df['LASTUPDATE'].dt.date
                    df['TIME'] = df['LASTUPDATE'].dt.time
                    df['TIME'] = df['TIME'].astype(str)

                    df['TIME'] = df['TIME'].str.split('.').str[0]
                    #df['TIME'] = df['TIME'].str.split(':').str[:2].str.join(':')
                    df.drop('LASTUPDATE', inplace=True, axis=1)
                  
                
                if 'TOSYMBOL' in df.columns:
                    df.rename(columns={"TOSYMBOL": "CURRENCY_TYPES"}, inplace=True)

                if 'FROMSYMBOL' in df.columns:
                    df.rename(columns={"FROMSYMBOL": "CRYPTO_TYPES"}, inplace=True)

                
                num_cols = df.select_dtypes(include='number').columns
                df[num_cols] = df[num_cols].round(2)
                                        
                global_dataframe = df
               
                if check_compare(nlp_question):
                    selected_chart = 'bar'
                    x_value = None
                    y_value = None
                    if x_value is None or y_value is None:
                        return (
                        {}, {'display': 'none'}, {'display': 'block', 'height': '255px'},html.Div("Please select the x axis and y axis columns for comparison chart", className="alert alert-warning"), 
                        reset_x_value, reset_y_value, selected_chart, 
                        None, {'display': 'none'} if loading_state is not None else {'display': 'block'}, 
                        None, {'display': 'none', 'margin-top': '0px'} if loading_state is not None else {'display': 'block', 'margin-top': '45px'}, 
                        {'display': 'none', 'width': '0px', 'height': '0px', 'flex-direction': 'row', 'align-items': 'start'} if loading_state is not None else {'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '100%'})

                    x_val = x_value
                    y_val = y_value
                    if len(extract_selected_cryptos(nlp_question)) > 1:    
                        fig = compare_crypto(nlp_question, x_val, y_val)
                    if len(extract_selected_currencies(nlp_question)) > 1:
                        fig = compare_currency(nlp_question, x_val, y_val)    
                    
                    return (
                        fig, {'display': 'block', 'height': '255px'}, {'display': 'none'}, None, 
                        x_value, y_value, selected_chart, 
                        None, {'display': 'none'} if loading_state is not None else {'display': 'block'}, 
                        None, {'display': 'none', 'margin-top': '0px'} if loading_state is not None else {'display': 'block', 'margin-top': '45px'}, 
                        {'display': 'none', 'width': '0px', 'height': '0px', 'flex-direction': 'row', 'align-items': 'start'} if loading_state is not None else {'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '100%'})

                return (
                    {}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, generate_table(global_dataframe), 
                    reset_x_value, reset_y_value, 'table', 
                    None, {'display': 'none'} if loading_state is not None else {'display': 'block'}, 
                    None, {'display': 'none', 'margin-top': '0px'} if loading_state is not None else {'display': 'block', 'margin-top': '45px'}, 
                    {'display': 'none', 'width': '0px', 'height': '0px', 'flex-direction': 'row', 'align-items': 'start'} if loading_state is not None else {'display': 'flex', 'flex-direction': 'column', 'align-items': 'center', 'width': '100%'})

    if show_n_clicks > 0 and ctx.triggered:
        if "show-button" == ctx.triggered[0]['prop_id'].split('.')[0]:
            if selected_chart == 'table':
                reset_x_value = None
                reset_y_value = None
                time.sleep(1)
                if global_dataframe is None or global_dataframe.empty:
                    return (
                        {}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("No data available for selected query", className="alert alert-warning"), 
                        reset_x_value, reset_y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, 
                        None, {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                        { 'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                else:
                    return (
                        {}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, generate_table(global_dataframe), 
                        reset_x_value, reset_y_value, selected_chart, None, {'display':'none'} if loading_state is not None else {'display':'block'}, 
                        None, {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                        {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
        
            if selected_chart == 'line':
                time.sleep(1)
                if not x_value and not y_value:
                    return ({}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("Please select the x axis and y axis columns", className="alert alert-warning"), 
                            x_value, y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                elif not x_value:
                    return ({}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("Please select the x axis column", className="alert alert-warning"), 
                            x_value, y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                elif not y_value:
                    return ({}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("Please select the y axis column", className="alert alert-warning"), 
                            x_value, y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                else:
                    fig = go.Figure()
                    if check_compare(nlp_question):
                        cryptos = extract_selected_cryptos(nlp_question)
                        currencies = extract_selected_currencies(nlp_question)
                        if len(extract_selected_cryptos(nlp_question)) > 2:  
                            btc = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[0]]
                            eth = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[1]]
                            usdt = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[2]]
                            fig.add_trace(go.Scatter(x=btc[x_value], y=btc[y_value], mode='lines+text', line_shape='spline', line_color='#F7931A', name=cryptos[0].upper()))
                            fig.add_trace(go.Scatter(x=eth[x_value], y=eth[y_value], mode='lines+text', line_shape='spline', line_color='#627EEA', name=cryptos[1].upper()))
                            fig.add_trace(go.Scatter(x=usdt[x_value], y=usdt[y_value], mode='lines+text', line_shape='spline', line_color='#26A17B', name=cryptos[2].upper()))
                        elif len(extract_selected_cryptos(nlp_question)) > 1: 
                            btc = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[0]]
                            eth = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[1]]
                            fig.add_trace(go.Scatter(x=btc[x_value], y=btc[y_value], mode='lines+text', line_shape='spline', line_color='#428bca', name=cryptos[0].upper()))
                            fig.add_trace(go.Scatter(x=eth[x_value], y=eth[y_value], mode='lines+text', line_shape='spline', line_color='#F7931A', name=cryptos[1].upper()))

                        if len(extract_selected_currencies(nlp_question)) > 2:
                            usd = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[0]]
                            inr = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[1]]
                            eur = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[2]]
                            fig.add_trace(go.Scatter(x=usd[x_value], y=usd[y_value], mode='lines+text', line_shape='spline', line_color='#F7931A', name=currencies[0].upper()))
                            fig.add_trace(go.Scatter(x=inr[x_value], y=inr[y_value], mode='lines+text', line_shape='spline', line_color='#627EEA', name=currencies[1].upper()))
                            fig.add_trace(go.Scatter(x=eur[x_value], y=eur[y_value], mode='lines+text', line_shape='spline', line_color='#26A17B', name=currencies[2].upper()))

                        elif len(extract_selected_currencies(nlp_question)) > 1:
                            usd = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[0]]
                            inr = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[1]]
                            fig.add_trace(go.Scatter(x=usd[x_value], y=usd[y_value], mode='lines+text', line_shape='spline', line_color='#428bca', name=currencies[0].upper()))
                            fig.add_trace(go.Scatter(x=inr[x_value], y=inr[y_value], mode='lines+text', line_shape='spline', line_color='#F7931A', name=currencies[1].upper()))
                        
                        fig.update_layout(
                        template='plotly_dark',
                        margin=dict(t=0, l=0, r=0, b=0),
                        font=dict(family='Arial', size=12),
                        showlegend=True,
                        xaxis=dict(
                            title=f'{x_value}',
                            visible=True,
                            showgrid=False,
                            tickfont=dict(family='Arial', size=12),
                        ),
                        yaxis=dict(
                            title=f"{y_value}",
                            visible=True,
                            showgrid=True,
                            tickfont=dict(family='Arial', size=12),
                            gridcolor='rgba(255, 255, 255, 0.1)',
                        ),
                    )
                        
                    else:    
                        fig.add_trace(go.Scatter(x=global_dataframe[x_value], y=global_dataframe[y_value], mode='lines+text', line_shape='spline', line_color='#428bca', marker=dict(size=10),))
                        
                        fig.update_layout(
                        showlegend=False,
                        template='plotly_dark',
                        margin=dict(t=0, l=0, r=0, b=0),
                        font=dict(family='Arial', size=12),
                        xaxis=dict(
                            title=f'{x_value}',
                            visible=True,
                            showgrid=False,
                            tickfont=dict(family='Arial', size=12),
                        ),
                        yaxis=dict(
                            title=f"{y_value}",
                            visible=True,
                            showgrid=True,
                            tickfont=dict(family='Arial', size=12),
                            gridcolor='rgba(255, 255, 255, 0.1)',
                        ),
                        )
                    
                    return (fig, {'display': 'block', 'height': '255px'}, {'display': 'none'}, [], x_value, y_value, selected_chart, None, {'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})

            if selected_chart == 'bar':
                time.sleep(1)
                if not x_value and not y_value:
                    return ({}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("Please select the x axis and y axis columns", className="alert alert-warning"), 
                            x_value, y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                elif not x_value:
                    return ({}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("Please select the x axis column", className="alert alert-warning"), 
                            x_value, y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                elif not y_value:
                    return ({}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, html.Div("Please select the y axis column", className="alert alert-warning"), 
                            x_value, y_value, selected_chart,None,{'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                elif x_value and y_value:
                    fig = go.Figure()
                    if check_compare(nlp_question):
                        cryptos = extract_selected_cryptos(nlp_question)
                        currencies = extract_selected_currencies(nlp_question)
                        if len(extract_selected_cryptos(nlp_question)) > 2:  
                            btc = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[0]]
                            eth = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[1]]
                            usdt = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[2]]
                            fig.add_trace(go.Bar(x=btc[x_value], y=btc[y_value], name=cryptos[0].upper(), text=btc[y_value]))
                            fig.add_trace(go.Bar(x=eth[x_value], y=eth[y_value], name=cryptos[1].upper(), text=eth[y_value]))
                            fig.add_trace(go.Bar(x=usdt[x_value], y=usdt[y_value], name=cryptos[2].upper(), text=usdt[y_value]))
                        elif len(extract_selected_cryptos(nlp_question)) > 1: 
                            btc = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[0]]
                            eth = global_dataframe[global_dataframe['CRYPTO_TYPES'] == cryptos[1]]
                            fig.add_trace(go.Bar(x=btc[x_value], y=btc[y_value], name=cryptos[0].upper(), text=btc[y_value]))
                            fig.add_trace(go.Bar(x=eth[x_value], y=eth[y_value], name=cryptos[1].upper(), text=eth[y_value]))

                        if len(extract_selected_currencies(nlp_question)) > 2:
                            usd = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[0]]
                            inr = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[1]]
                            eur = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[2]]
                            fig.add_trace(go.Bar(x=usd[x_value], y=usd[y_value], name=currencies[0].upper(), text=usd[y_value]))
                            fig.add_trace(go.Bar(x=inr[x_value], y=inr[y_value], name=currencies[1].upper(), text=inr[y_value]))
                            fig.add_trace(go.Bar(x=eur[x_value], y=eur[y_value], name=currencies[2].upper(), text=eur[y_value]))

                        elif len(extract_selected_currencies(nlp_question)) > 1:
                            usd = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[0]]
                            inr = global_dataframe[global_dataframe['CURRENCY_TYPES'] == currencies[1]]
                            fig.add_trace(go.Bar(x=usd[x_value], y=usd[y_value], name=currencies[0].upper(), text=usd[y_value]))
                            fig.add_trace(go.Bar(x=inr[x_value], y=inr[y_value], name=currencies[1].upper(), text=inr[y_value]))
                        
                        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                        fig.update_layout(
                        uniformtext_minsize=8, uniformtext_mode='hide',
                        template='plotly_dark',
                        margin=dict(t=0, l=0, r=0, b=0),
                        font=dict(family='Arial', size=12),
                        showlegend=True,
                        xaxis=dict(
                            title=f'{x_value}',
                            visible=True,
                            showgrid=False,
                            tickfont=dict(family='Arial', size=12),
                        ),
                        yaxis=dict(
                            title=f"{y_value}",
                            visible=True,
                            showgrid=True,
                            tickfont=dict(family='Arial', size=12),
                            gridcolor='rgba(255, 255, 255, 0.1)',
                            range=[eth[y_value].min(), btc[y_value].max() + btc[y_value].max()/10]
                        ),
                    )
                        
                    else:    
                        fig.add_trace(go.Bar(x=global_dataframe[x_value], y=global_dataframe[y_value], text=global_dataframe[y_value]))
                        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                        fig.update_layout(
                        uniformtext_minsize=8, uniformtext_mode='hide',
                        showlegend=False,
                        template='plotly_dark',
                        margin=dict(t=0, l=0, r=0, b=0),
                        font=dict(family='Arial', size=12),
                        xaxis=dict(
                            title=f'{x_value}',
                            visible=True,
                            showgrid=False,
                            tickfont=dict(family='Arial', size=12),
                        ),
                        yaxis=dict(
                            title=f"{y_value}",
                            visible=True,
                            showgrid=True,
                            tickfont=dict(family='Arial', size=12),
                            gridcolor='rgba(255, 255, 255, 0.1)',
                            range=[global_dataframe[y_value].min(), global_dataframe[y_value].max() + global_dataframe[y_value].max()/10]
                        ),
                        )
                    
                    return (fig, {'display': 'block', 'height': '255px'}, {'display': 'none'}, [], x_value, y_value, selected_chart, None, {'display':'none'} if loading_state is not None else {'display':'block'}, None, 
                            {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
                            {'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})
                
    return (
        {}, {'display': 'none'}, {'display': 'block', 'height': '255px'}, 
        html.Div(), reset_x_value, reset_y_value, reset_chart_value, None,
        {'display':'none'} if loading_state is not None else {'display':'block'}, None, 
        {'display':'none','margin-top':'0px'} if loading_state is not None else {'display':'block','margin-top':'45px'}, 
        { 'display': 'none','width': '0px','height': '0px','flex-direction':'row','align-items':'start'} if loading_state is not None else { 'display': 'flex','flex-direction': 'column','align-items': 'center','width': '100%'})