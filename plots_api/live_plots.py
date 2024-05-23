import pandas as pd
from dash import dcc, html
import plotly.graph_objs as go
import dash_bootstrap_components as dbc 
from datetime import datetime, timedelta
from django_plotly_dash import DjangoDash
from dash.dependencies import Input, Output
from django.templatetags.static import static
from db_qa_api.utils import sk_execute_sql_query


external_bootstrap_styles = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"
static_css_path = "/static/styles.css"

url = static('/images/btc.png')
url1 = static('/images/eth.png')
url2 = static('/images/usdt.png')

app = DjangoDash('live_plots', external_stylesheets=[external_bootstrap_styles, url, url1, url2, static_css_path])

def get_date_range():
    end_time = datetime.now() - timedelta(hours=0)
    start_time = end_time - timedelta(minutes=30)
    return start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')

app.layout = html.Div(children=[

         html.Div([
                html.Div([ html.Div('Currency :', className='me-1 text-white fw-bold', style={'margin-left':'16px','margin-top':'3px'}),
                dbc.RadioItems(
                    id='currency-component',
                    options=[
                        {'label': 'USD', 'value': 'USD'},
                        {'label': 'INR', 'value': 'INR'},
                        {'label': 'EUR', 'value': 'EUR'},
                    ],
                    value='USD',
                    className='mt-2 radio_button',
                    inline=True,
                    #labelStyle={'color': 'white', 'font-size':12, 'font-weight': 'bold', 'margin':'0px', 'padding':'0px'},
                    style={'color': 'white', 'font-size':12, 'font-weight': 'bold', 'margin':'0px', 'padding':'0px'},
                ),], className='d-flex'),
               
                #html.Div('Live Price Trend', style={'color':"white",'font-weight': 'bold'}),
                html.Div([ html.Div('Crypto :', className='me-1 text-white fw-bold', style={'margin-left':'20px', "margin-top":'6px'}),
                dcc.Dropdown(
                [{
                    "label": html.Span(
                        [
                            html.Img(src=url, height=20),
                            html.Span("BTC", style={'font-size': 12, 'padding-left': 2, 'color': '#fff'}),
                        ], style={'align-items': 'center', 'justify-content': 'center'}
                    ),
                    "value": "BTC",
                    },
                    {
                    "label": html.Span(
                        [
                            html.Img(src=url1, height=20),
                            html.Span("ETH", style={'font-size': 12, 'padding-left': 2, 'color': '#fff'}),
                        ], style={'align-items': 'center', 'justify-content': 'center'}
                    ),
                    "value": "ETH",
                    },
                    {
                    "label": html.Span(
                        [
                            html.Img(src=url2, height=20),
                            html.Span("USDT", style={'font-size': 12, 'padding-left': 2, 'color': '#fff'}),
                        ], style={'align-items': 'center', 'justify-content': 'center',"margin-bottom":'4px'}
                    ),
                    "value": "USDT",
                    },],
                    value="BTC",
                    id='crypto-component',
                    style={"width": '85px', 'height': '30px', "margin-top": '1px', 'backgroundColor': 'black', 'color': 'white'},
                    clearable=False,
                    className='custom-dropdown',
                    maxHeight='80px',
                    optionHeight=30,
                    searchable=False,
                ),
                ], className='d-flex'),
                html.Div('Live Volume trends of the crypto currency', style={'color':"white",'text-align':'center', 'color':'#111000','font-weight': 'bold'}),
            ], className='d-flex justify-content-between', style={'background-color':'#111000'}),

    html.Div([
             dcc.Graph(id="price-chart", style={'height': '278px',  'border-style':'none'}, className='card col me-1 mt-2', config={
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d','toImage','zoom2d','autoScale2d','displaylogo'],'displaylogo': False,'displayModeBar': False,
            }),
            dcc.Graph(id="volume-chart", style={'height': '278px','border-right-style':'none','border-top-style':'none','border-bottom-style':'none'}, className='card col mt-2', config={
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d','toImage','zoom2d','autoScale2d','dragmode'],'displaylogo': False
            }),

    ], className='d-flex justify-content-between'),

   dcc.Interval(id="intervals-component", interval=30 * 1000, n_intervals=float('inf')),
], style={'background-color':'#000'})


@app.callback(
    [Output("price-chart", "figure"), Output('volume-chart', 'figure')],
    [Input("currency-component", "value"), Input("crypto-component","value"),Input('intervals-component', 'n_intervals')],
)

def update_line_charts(selected_currency,selected_crypto, n_intervals):
    fig = go.Figure()
    fig1 = go.Figure()
    
    sql_query = f"""SELECT fromsymbol, price, volume24hour, LASTUPDATE 
                    FROM dbo.cryptocurrency_dwh 
                    WHERE fromsymbol = '{selected_crypto}'
                    AND tosymbol = '{selected_currency}' 
                    AND LASTUPDATE BETWEEN '{get_date_range()[0]}' AND '{get_date_range()[1]}' 
                    ORDER BY LASTUPDATE"""

    df_crypto = sk_execute_sql_query(sql_query)
    
    
    df_crypto['LASTUPDATE'] = pd.to_datetime(df_crypto['LASTUPDATE'])

   



    currency_symbol = '$' if selected_currency == 'USD' else '₹' if selected_currency == 'INR' else '€'

    fig.update_layout(
        title={'text': '<b>Live Price Trend</b>', 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top', 'y':0.99},
        titlefont={'size': 15},
        template='plotly_dark',
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(family='Arial', size=12),
        showlegend=True,
        xaxis=dict(
            title='<b>Time</b>',
            visible=True,
            showgrid=False,
            tickfont=dict(family='Arial', size=12),
        ),
        yaxis=dict(
            title=f"<b>Price</b>",
            visible=True,
            showgrid=True,
            tickprefix=f'{currency_symbol}',
            ticksuffix = '  ',
            tickfont=dict(family='Arial', size=12),
            gridcolor='rgba(255, 255, 255, 0.1)',
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        )
    )

    
    fig1.update_layout(
        title={'text': '<b>Live Volume Trend</b>', 'xanchor': 'left', 'yanchor': 'top', 'y':0.99, 'x':0.5},
        titlefont={'size': 15},
        template='plotly_dark',
        margin=dict(t=0, l=0, r=0, b=0),
        font=dict(family='Arial', size=12),
        showlegend=True,
        xaxis=dict(
            title='<b>Time</b>',
            visible=True,
            #color='black',
            #showline=True,
            showgrid=False,
            showticklabels=True,
            #linecolor='black',
            #linewidth=1,
            #ticks='outside',
            tickfont=dict(family='Arial', size=12),
            #range=[0,24],
        ),
        yaxis=dict(
            title=f"<b>Volume</b>",
            visible=True,
            #color='black',
            #showline=True,
            showgrid=True,
            #showticklabels=True,
            #linecolor='black',
            #linewidth=1,
            ticksuffix = '  ',
            #ticks='outside',
            tickfont=dict(family='Arial', size=12),
            gridcolor='rgba(255, 255, 255, 0.1)',
           range=[df_crypto['volume24hour'].min()-(df_crypto['volume24hour'].min())/90,df_crypto['volume24hour'].max()+df_crypto['volume24hour'].max()/90 ]
        ),
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        ),
    )
    #fig1.update_yaxes(tickformat=".3f", title='Value (x1000)')

    if selected_crypto == 'BTC':
        fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['LASTUPDATE']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=df_crypto['price'], name='BTC', mode='lines+text', line_shape='spline', line_color='#F7931A'))
    elif selected_crypto == 'ETH':
        fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['LASTUPDATE']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=df_crypto['price'], name='ETH', mode='lines+text', line_shape='spline', line_color='#627EEA'))
    elif selected_crypto == 'USDT':
        fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['LASTUPDATE']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=df_crypto['price'], name='USDT', mode='lines+text', line_shape='spline', line_color='#26A17B'))
    
    # global price_global

    # last_price = 0
    # if not df_crypto.empty:
    #     last_price = df_crypto['PRICE'].iloc[0]

    # if price_global != last_price:
    #     print(price_global)
    #     print(last_price)
    #     price_global = last_price
    #     if selected_crypto == 'BTC':
    #         fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=df_crypto['PRICE'], name='BTC', mode='lines+text', line_shape='spline', line_color='#F7931A'))
    #     elif selected_crypto == 'ETH':
    #         fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=df_crypto['PRICE'], name='ETH', mode='lines+text', line_shape='spline', line_color='#627EEA'))
    #     else:
    #         fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=df_crypto['PRICE'], name='USDT', mode='lines+text', line_shape='spline', line_color='#26A17B'))
    # else:
    #     print(" else ",price_global)
    #     print("else " ,last_price)
    #     if selected_crypto == 'BTC':
    #         fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=[price_global], name='BTC', mode='lines+text', line_shape='spline', line_color='#F7931A'))
    #     elif selected_crypto == 'ETH':
    #         fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=[price_global], name='ETH', mode='lines+text', line_shape='spline', line_color='#627EEA'))
    #     else:
    #         fig.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=[price_global], name='USDT', mode='lines+text', line_shape='spline', line_color='#26A17B'))

    


    if selected_crypto == 'BTC':
        fig1.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['LASTUPDATE']).dt.strftime('%Y-%m-%d %H:%M:%S'),y=df_crypto['volume24hour'],name='BTC Volume',mode='lines+text',line_shape='spline',line_color='#F7931A',fill='tozeroy',fillcolor='rgba(247, 147, 26, 0.2)'))
    elif selected_crypto == 'ETH':   
        fig1.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['LASTUPDATE']).dt.strftime('%Y-%m-%d %H:%M:%S'),y=df_crypto['volume24hour'],name='ETH Volume',mode='lines+text',line_shape='spline',line_color='#627EEA',fill='tozeroy',fillcolor='rgba(98, 126, 234, 0.2)'))
    elif selected_crypto == 'USDT':
        fig1.add_trace(go.Scatter(x=pd.to_datetime(df_crypto['LASTUPDATE']).dt.strftime('%Y-%m-%d %H:%M:%S'),y=df_crypto['volume24hour'],name='USDT Volume',mode='lines+text',line_shape='spline',line_color='#26A17B',fill='tozeroy',fillcolor='rgba(38, 161, 123, 0.2)'))

   
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(btc['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=btc['volume24hour'.upper()], name='BTC Volume', mode='lines+text', line_shape='spline', line_color='#428bca'))
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(eth['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=eth['volume24hour'.upper()], name='ETH Volume', mode='lines+text', line_shape='spline', line_color='#ffb74d'))
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(usdt['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=usdt['volume24hour'.upper()], name='USDT Volume', mode='lines+text', line_shape='spline', line_color='#2ecc71'))
    
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(btc['lastupdate']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=btc['volume24hour'], name='BTC Volume', marker_color='rgb(228,26,28)',fill='tozeroy', fillpattern=dict(shape="x", bgcolor="rgba(0,0,0,0)", fgcolor="rgb(228,26,28)", fgopacity=0.5)))
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(eth['lastupdate']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=eth['volume24hour'], name='ETH Volume', marker_color='green',fill='tozeroy', fillpattern=dict(shape=".", bgcolor="rgba(0,0,0,0)", fgcolor="green", fgopacity=0.5)))
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(usdt['lastupdate']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=usdt['volume24hour'], name='USDT Volume', marker_color='#511CFB',fill='tozeroy',fillpattern=dict(shape="/", bgcolor="rgba(0,0,0,0)", fgcolor="#511CFB", fgopacity=0.5)))   

    # fig1.add_trace(go.Scatter(x=pd.to_datetime(btc['lastupdate']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=btc['volume24hour'], name='BTC Volume', marker_color='#428bca',fill='tozeroy'))
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(eth['lastupdate']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=eth['volume24hour'], name='ETH Volume', marker_color='#ffb74d',fill='tozeroy'))
    # fig1.add_trace(go.Scatter(x=pd.to_datetime(usdt['lastupdate']).dt.strftime('%Y-%m-%d %H:%M:%S'), y=usdt['volume24hour'], name='USDT Volume', marker_color='#2ecc71',fill='tozeroy'))   

    # fig1.add_trace(go.Bar(x=pd.to_datetime(btc['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=btc['volume24hour'.upper()], name='BTC Volume', marker_color='RGB(247, 147, 26)'))
    # fig1.add_trace(go.Bar(x=pd.to_datetime(eth['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=eth['volume24hour'.upper()], name='ETH Volume', marker_color='RGB(98, 126, 234)'))
    # fig1.add_trace(go.Bar(x=pd.to_datetime(usdt['lastupdate'.upper()]).dt.strftime('%Y-%m-%d %H:%M:%S'), y=usdt['volume24hour'.upper()], name='USDT Volume', marker_color='RGB(38, 161, 123)'))

   
    return [fig, fig1]