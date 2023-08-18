import pandas as pd
import plotly.express as px
import dash
import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import requests


# STARK_BalanceSheet
df1 = pd.read_csv('C:/Users/ACER/Downloads/5001/stark_select_bl (2).csv')
df1 = pd.DataFrame(df1)
df2=df1[["งบประมาณปี","รวมหนี้สิน","รวมหนี้สิน(%)","รวมส่วนของผู้ถือหุ้นบริษัท(%)",]]
df2 = pd.DataFrame(df2)

# Create a subplot with shared X axis and dual y-axes
fig2 = make_subplots(rows=1, cols=1, specs=[[{'secondary_y': True}]])

# Create traces for Line and Bar charts with customized colors
trace_line = go.Scatter(x=df2["งบประมาณปี"], y=df2["รวมหนี้สิน"], mode='lines+markers', name="รวมหนี้สิน", marker_color='blue')
trace_stack_1 = go.Bar(x=df2["งบประมาณปี"], y=df2["รวมหนี้สิน(%)"], name="รวมหนี้สิน(%)", marker_color='green')
trace_stack_2 = go.Bar(x=df2["งบประมาณปี"], y=df2["รวมส่วนของผู้ถือหุ้นบริษัท(%)"], name="รวมส่วนของผู้ถือหุ้นบริษัท(%)", marker_color='orange')

# Add Line trace to the subplot
fig2.add_trace(trace_line, secondary_y=True)

# Add Bar traces to the subplot
fig2.add_trace(trace_stack_1, secondary_y=False)
fig2.add_trace(trace_stack_2, secondary_y=False)

# Update layout
fig2.update_layout(
    title='อัตราส่วนหนี้สินต่อผู้ถือหุ้น',
    xaxis_title='งบประมาณปี'
)

# Update y-axes titles
fig2.update_yaxes(title_text="รวมหนี้สิน", secondary_y=True)
fig2.update_yaxes(title_text="สัดส่วนหนี้สินและผู้ถือหุ้น", secondary_y=False)

table_data = df1.values.T.tolist()

header_labels = ['งบประมาณปี', 'รวมสินทรัพย์', 'รวมส่วนของผู้ถือหุ้นบริษัท', 'รวมส่วนของผู้ถือหุ้นบริษัท(%)', 'รวมหนี้สิน', 'รวมหนี้สิน(%)']

# Create a table trace
table_trace = go.Table(
    header=dict(values=header_labels),
    cells=dict(values=table_data)
)

app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Graph(figure=fig2, id='graph1'),
    dcc.Graph(figure=go.Figure(data=[table_trace], layout=go.Layout(title='Balance Sheet')), id='graph2')
])

# Define callback to synchronize selections between graphs
@app.callback(
    dash.dependencies.Output('graph1', 'selectedData'),
    dash.dependencies.Input('graph2', 'selectedData')
)
def update_selected_data(selectedData):
    return selectedData

if __name__ == '__main__':
    app.run_server(port=8051, debug=True)




# STARK_CashFlow

# Sample data
cash = {
    "งบประมาณปี": ["ปี2562", "ปี2563", "ปี2564", "ปี2565"],
    "กิจกรรมดำเนินงาน": [676.1, 3003.56, -1225.48, -4629.89],
    "กิจกรรมลงทุน": [-620.13, -6531.81, -406.02, -862.47],
    "กิจกรรมจัดหาเงิน": [720.07, 3272.85, 1560.92, 10719.50],
    "เงินสดสุทธิ": [776.04, -255.4, -70.59, 5227.14]
}

# Create a DataFrame
cf = pd.DataFrame(cash)

# Create line chart traces
cf1 = go.Scatter(x=cf["งบประมาณปี"], y=cf["กิจกรรมดำเนินงาน"], mode='lines+markers', name='กิจกรรมดำเนินงาน')
cf2 = go.Scatter(x=cf["งบประมาณปี"], y=cf["กิจกรรมลงทุน"], mode='lines+markers', name='กิจกรรมลงทุน')
cf3 = go.Scatter(x=cf["งบประมาณปี"], y=cf["กิจกรรมจัดหาเงิน"], mode='lines+markers', name='กิจกรรมจัดหาเงิน')

# Create the layout for the chart
layout = go.Layout(
    title='กระแสเงินสดของบริษัทประจำปี2562 - ปี2565',
    xaxis=dict(title='งบประมาณปี'),
    yaxis=dict(title='เงินสดสุทธิ(หน่วย:ล้านบาท)')
)

# Create a figure and add the traces and layout
cashflow = go.Figure(data=[cf1, cf2, cf3], layout=layout)

# Define custom styles using CSS
custom_styles = {
    'graph-container': {
        'margin': '20px',   # Adjust the margin around the graph container
        'padding': '20px',  # Adjust the padding inside the graph container
    },
    'score-card-container': {
        'margin': '20px',   # Adjust the margin around the score card container
        'padding': '10px',  # Adjust the padding inside the score card container
    },
    'score-card': {
        'border': '1px solid black',
        'padding': '5px',   # Adjust the padding inside the score card table
    }
}

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Graph(
        id='cashflow-chart',
        figure=cashflow,
        style=custom_styles['graph-container'],  # Apply custom styles to the graph container
    ),
    html.Div(
        id='score-card-container',
        children=[
            html.Table(id='score-card', style=custom_styles['score-card']),  # Apply custom styles to the score card table
        ],
        style=custom_styles['score-card-container'],  # Apply custom styles to the score card container
    )
])
# Define callback to update the score card table
@app.callback(
    Output('score-card', 'children'),
    [Input('cashflow-chart', 'hoverData')]
)
def update_score_card(hoverData):
    if hoverData is None:
        return []

    point_index = hoverData['points'][0]['pointIndex']
    year = cf.loc[point_index, 'งบประมาณปี']
    cash_value = cf.loc[point_index, 'เงินสดสุทธิ']
    cash_from_operations = cf.loc[point_index, 'กิจกรรมจัดหาเงิน']
    
    score_card = html.Table([
        html.Tr([html.Th('ปี'), html.Th('เงินสดสุทธิ'), html.Th('เงินสดจากกิจกรรมจัดหาเงิน')]),
        html.Tr([html.Td(year), html.Td(cash_value), html.Td(cash_from_operations)])
    ], style={'border': '1px solid black'})  # Apply border style
    
    return score_card

def update_score_card(hoverData):
    if hoverData is None:
        return []

    point_index = hoverData['points'][0]['pointIndex']
    year = cf.loc[point_index, 'งบประมาณปี']
    cash_value = cf.loc[point_index, 'เงินสดสุทธิ']
    cash_from_operations = cf.loc[point_index, 'กิจกรรมจัดหาเงิน']
    
    score_card = html.Table([
        html.Tr([
            html.Th('ปี', style={'padding': '5px', 'background-color': 'lightgray', 'vertical-align': 'middle'}),
            html.Th('เงินสดสุทธิ', style={'padding': '5px', 'background-color': 'lightgray', 'vertical-align': 'middle'}),
            html.Th('เงินสดจากกิจกรรมจัดหาเงิน', style={'padding': '5px', 'background-color': 'lightgray', 'vertical-align': 'middle'})
        ]),
        html.Tr([
            html.Td(year, style={'padding': '5px', 'vertical-align': 'middle'}),
            html.Td(cash_value, style={'padding': '5px', 'vertical-align': 'middle'}),
            html.Td(cash_from_operations, style={'padding': '5px', 'vertical-align': 'middle'})
        ])
    ], style={'border': '1px solid black', 'border-collapse': 'collapse'})  # Apply border style
    
    return score_card

# Run the app
if __name__ == '__main__':
    app.run_server(port = 8052,debug=True)




# STRAK_PL

# Sample data
stark_pl = {
    "งบประมาณปี": ["ปี2562", "ปี2563", "ปี2564", "ปี2565"],
    "รวมรายได้": [11607.71, 16917.68, 27129.64, 25312.98],
    "%Total Revenue": [100, 100, 100, 100],
    "กำไร(ขาดทุน)สุทธิ": [123.92, 1608.66, 2783.11, -6612.13],
    "%กำไร(ขาดทุน)สุทธิ": [1.07, 9.51, 10.26, -26.12]
}

pl = pd.DataFrame(stark_pl)

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.Div(id='scorecard', style={'border': '1px solid black','textAlign': 'center', 'fontSize': 24}),
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='table-chart'),
])
# Update the scorecard
@app.callback(
    Output('scorecard', 'children'),
    Input('bar-chart', 'clickData')
)
def update_scorecard(clickData):
    if clickData:
        selected_year = clickData['points'][0]['x']
        scorecard_value = pl.loc[pl['งบประมาณปี'] == selected_year, "%กำไร(ขาดทุน)สุทธิ"].values[0]
        return f"%กำไร(ขาดทุน)สุทธิ: {scorecard_value}%"
    return "%กำไร(ขาดทุน)สุทธิ: N/A"

# Create a clustered bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    Input('bar-chart', 'selectedData')
)
def update_bar_chart(selectedData):
    selected_points = selectedData['points'] if selectedData else []
    selected_years = [point['x'] for point in selected_points]
    
    fig = go.Figure()

    for column in ["รวมรายได้", "กำไร(ขาดทุน)สุทธิ"]:
        fig.add_trace(go.Bar(
            x=pl["งบประมาณปี"],
            y=pl[column],
            name=column,
            marker_color='purple' if column == "รวมรายได้" else 'pink'
        ))

    fig.update_layout(
        title='เปรียบเทียบรวมรายได้และกำไร(ขาดทุน)สุทธิ ประจำปี2562 - ปี2565',
        xaxis_title='งบประมาณปี',
        yaxis_title='รวมรายได้และกำไร(ขาดทุน)สุทธิ',
        barmode='group'  # Use 'group' for clustered columns
    )

    return fig

# Create a table chart
@app.callback(
    Output('table-chart', 'figure'),
    Input('bar-chart', 'selectedData')
)
def update_table_chart(selectedData):
    selected_points = selectedData['points'] if selectedData else []
    selected_years = [point['x'] for point in selected_points]
    

    table_chart = go.Figure(data=[go.Table(
        header=dict(values=list(stark_pl.keys())),
        cells=dict(values=list(stark_pl.values()))
    )])
    
    return table_chart

# Run the app
if __name__ == '__main__':
    app.run_server(port=8055, debug=True)