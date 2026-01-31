import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc

# Load and clean data
df = pd.read_excel("Dash CW-2.xlsx")
df.columns = df.columns.str.strip()
df.rename(columns={
    'Age Group': 'age_group',
    'Gender': 'gender',
    'Occupation/Status': 'occupation',
    'Average hours of sleep per night': 'sleep_hours',
    'How often do you exercise per week?': 'exercise_days',
    'Average daily screen time (hours)': 'screen_time',
    'Average daily study/work hours': 'study_hours',
    'How often do you eat fast food?': 'fast_food_freq',
    'How many glasses of water do you drink daily': 'water_intake',
    'Rate your diet quality': 'diet_quality',
    'How often do you feel stressed?': 'stress_level',
    'Rate your energy level throughout the day': 'energy_level',
    'How would you rate your overall health?': 'overall_health',
    'Overall satisfaction with your lifestyle': 'lifestyle_satisfaction'
}, inplace=True)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# KPI cards
def create_stat_card(title, series, color="primary"):
    count = series.count()
    mean = round(series.mean(),1)
    median = series.median()
    min_val = series.min()
    max_val = series.max()
    return dbc.Card(
        dbc.CardBody([
            html.H6(title, className="card-title"),
            html.P(f"Count: {count}", className="card-text"),
            html.P(f"Mean: {mean}", className="card-text"),
            html.P(f"Median: {median}", className="card-text"),
            html.P(f"Min: {min_val}, Max: {max_val}", className="card-text")
        ]),
        color=color, inverse=True, style={"textAlign": "center"}
    )

# Layout
app.layout = dbc.Container([
    html.H1("Lifestyle & Health Habits Dashboard", style={'textAlign': 'center', 'marginBottom': '20px'}),

    # KPI Row
    dbc.Row([
        dbc.Col(create_stat_card("Sleep Hours", df['sleep_hours']), width=3),
        dbc.Col(create_stat_card("Stress Level", df['stress_level'], color="danger"), width=3),
        dbc.Col(create_stat_card("Lifestyle Satisfaction", df['lifestyle_satisfaction'], color="success"), width=3),
        dbc.Col(create_stat_card("Diet Quality", df['diet_quality'], color="warning"), width=3),
    ], style={"marginBottom": "30px"}),

    # Charts
    dbc.Row([
        # Overall Health
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Overall Health by Age Group"),
                    html.Label("Filter Gender:"),
                    dcc.Checklist(
                        id='bar_gender_filter',
                        options=[{'label': 'Male', 'value': 'Male'},
                                 {'label': 'Female', 'value': 'Female'},
                                 {'label': 'All', 'value': 'All'}],
                        value=['All'], inline=True
                    ),
                    html.Label("Filter Occupation:"),
                    dcc.Dropdown(
                        id='bar_occ_filter',
                        options=[{'label': o, 'value': o} for o in df['occupation'].unique()],
                        placeholder="Select occupation"
                    ),
                    dcc.Graph(id='bar_chart', style={"height": "400px"})
                ]),
                style={"marginBottom": "20px"}
            ), width=6
        ),
        # Exercise Pie
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Exercise Frequency Distribution"),
                    html.Label("Filter Gender:"),
                    dcc.Dropdown(
                        id='pie_gender_filter',
                        options=[{'label': g, 'value': g} for g in df['gender'].unique()],
                        placeholder="Select gender"
                    ),
                    dcc.Graph(id='pie_chart', style={"height": "400px"})
                ]),
                style={"marginBottom": "20px"}
            ), width=6
        )
    ]),

    dbc.Row([
        # Sleep Hours Line
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Sleep Hours Distribution"),
                    html.Label("Filter Age Group:"),
                    dcc.Dropdown(
                        id='line_age_filter',
                        options=[{'label': g, 'value': g} for g in df['age_group'].unique()],
                        placeholder="Select age group"
                    ),
                    dcc.Graph(id='line_chart', style={"height": "400px"})
                ]),
                style={"marginBottom": "20px"}
            ), width=6
        ),
        # Drill-down Table (Drill Down Insights)
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H5("Drill Down Insights"),
                    dash_table.DataTable(
                        id='occupation_table',
                        columns=[{"name": "Occupation", "id": "occupation"},
                                 {"name": "Count", "id": "count"}],
                        data=[],  # will be populated by callback
                        row_selectable="single",
                        style_table={'height': '300px', 'overflowY': 'auto'},
                        style_cell={'textAlign': 'center'},
                    ),
                    html.Label("Filter Age Group:"),
                    dcc.Dropdown(
                        id='table_age_filter',
                        options=[{'label': g, 'value': g} for g in df['age_group'].unique()],
                        placeholder="Select age group"
                    ),
                    html.Label("Filter Gender:"),
                    dcc.Dropdown(
                        id='table_gender_filter',
                        options=[{'label': g, 'value': g} for g in df['gender'].unique()],
                        placeholder="Select gender"
                    ),
                    dcc.Graph(id='occupation_detail_chart', style={"height": "400px"})
                ]),
                style={"marginBottom": "20px"}
            ), width=6
        )
    ])
], fluid=True)

# Callback to populate drill-down table with all occupations
@app.callback(
    Output('occupation_table', 'data'),
    Input('bar_occ_filter', 'value')
)
def update_occupation_table(occupation_selected):
    dff = df.copy()
    if occupation_selected:
        dff = dff[dff['occupation'] == occupation_selected]
    table_data = dff.groupby('occupation').size().reset_index(name='count').to_dict('records')
    return table_data

# Callback to update drill-down insights chart safely
@app.callback(
    Output('occupation_detail_chart', 'figure'),
    [Input('occupation_table', 'selected_rows'),
     Input('table_age_filter', 'value'),
     Input('table_gender_filter', 'value'),
     Input('occupation_table', 'data')]
)
def update_detail_chart(selected_rows, age_selected, gender_selected, table_data):
    dff = df.copy()

    # Only use selected row if it's valid
    if selected_rows and len(selected_rows) > 0 and selected_rows[0] < len(table_data):
        occupation_name = table_data[selected_rows[0]]['occupation']
        dff = dff[dff['occupation'] == occupation_name]

    if age_selected:
        dff = dff[dff['age_group'] == age_selected]
    if gender_selected:
        dff = dff[dff['gender'] == gender_selected]

    # Average sleep_hours and stress_level
    avg_values = dff[['sleep_hours', 'stress_level']].mean().reset_index()
    avg_values.columns = ['variable', 'average']
    fig = px.bar(avg_values, x='variable', y='average',
                 title=f"Drill Down Insights for {dff['occupation'].iloc[0] if not dff.empty else 'All'}",
                 text='average')
    return fig

# Other callbacks remain unchanged
@app.callback(
    Output('bar_chart', 'figure'),
    [Input('bar_gender_filter', 'value'),
     Input('bar_occ_filter', 'value')]
)
def update_bar(gender_selected, occupation_selected):
    dff = df.copy()
    if 'All' not in gender_selected:
        dff = dff[dff['gender'].isin(gender_selected)]
    if occupation_selected:
        dff = dff[dff['occupation'] == occupation_selected]
    fig = px.bar(dff, x='age_group', y='overall_health', color='age_group',
                 title='Average Overall Health by Age Group', barmode='group')
    return fig

@app.callback(
    Output('pie_chart', 'figure'),
    Input('pie_gender_filter', 'value')
)
def update_pie(gender_selected):
    dff = df.copy()
    if gender_selected:
        dff = dff[dff['gender'] == gender_selected]
    fig = px.pie(dff, names='exercise_days', title='Exercise Frequency Distribution')
    return fig

@app.callback(
    Output('line_chart', 'figure'),
    Input('line_age_filter', 'value')
)
def update_line(age_selected):
    dff = df.copy()
    if age_selected:
        dff = dff[dff['age_group'] == age_selected]
    fig = px.line(dff.groupby('sleep_hours').size().reset_index(name='count'),
                  x='sleep_hours', y='count', markers=True,
                  title='Sleep Hours Distribution')
    return fig

if __name__ == '__main__':
    app.run(debug=True)