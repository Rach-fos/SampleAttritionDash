import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc


def load_and_process_data():
    df = pd.read_csv("HRDataset.csv")

    #group smaller departments
    df["Department"] = df["Department"].replace({
        "Admin Offices": "Admin and Executive Offices",
        "Executive Office": "Admin and Executive Offices",
        "Executive Offices": "Admin and Executive Offices"
    })
    #Data changes
    df['Sex'] = df["Sex"].str.strip()
    df['Department'] = df['Department'].str.strip()
    df['DateofHire'] = pd.to_datetime(df["DateofHire"], errors="coerce")
    df["DateofTermination"] = pd.to_datetime(df["DateofTermination"], errors="coerce")
    df["TerminationYear"] = df["DateofTermination"].dt.year
    df['TerminationMonth'] = df['DateofTermination'].dt.month
    df['HireYear'] = df["DateofHire"].dt.year

    return df

# pull Data
df = load_and_process_data()

# lists for dropdowns
DEPARTMENTS = sorted(df["Department"].dropna().unique())
GENDERS = sorted(df["Sex"].dropna().unique())
YEARS = sorted(df["TerminationYear"].dropna().unique())
MIN_YEAR = int(min(YEARS)) if YEARS else 2010
MAX_YEAR = int(max(YEARS)) if YEARS else 2025

#style & title
app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])
server = app.server
app.title = "HR Attrition Dashboard"

#layout
app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Attrition Dashboard", className="display-6 mt-4"),
            html.P('Based on Sample Data by Dr. Carla Patalano and Dr. Rich Huebner', className="text-muted mb-4"),
        ], width=12)

    ]),


    #Top level cards
    dbc.Row([
        #Card 1
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(id='kpi-total', className='card-title'),
                html.Span("Total Employees",  className="small text-muted")
            ])
        ]), width=3),
        #card 2
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(id= "kpi-active", className="card-title"),
                html.Span('Active', className="small text-muted")
            ])
        ]), width=3),
        #card 3
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(id="kpi-terminated", className= "card-title text-danger"),
                html.Span("Terminated", className="small text-muted")
            ])
        ]), width=3),
        #card 4
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4(id="kpi-rate", className="card-title text-warning"),
                html.Span("Attrition Rate", className="small text-muted")
            ])
        ]),  width=3),
    ], className="mb-4"),


    # Filters Row
    dbc.Row([
        #filter 1
        dbc.Col([
            html.Label("Termination Year Range"),
            dcc.RangeSlider(
                id="year-filter",
                min=MIN_YEAR, max=MAX_YEAR, step=1,
                value=[MIN_YEAR, MAX_YEAR],
                
                marks={int(y): str(int(y)) for y in YEARS[:]},
            )
        ], width=4),
        
        #filter 2
        dbc.Col([
            html.Label("Department"),
            dcc.Dropdown(
                id="dept-filter",
                options=[{"label": d, "value": d} for d in DEPARTMENTS],
                multi=True,
                className="text-dark"
            )
        ], width=3),
        #filter 3
        dbc.Col([
            html.Label("Gender"),
            dcc.Dropdown(
                id="gender-filter",
                options=[{"label": g, "value": g} for g in GENDERS],
                multi=True,
                className="text-dark"
            )
        ], width=2),
        
        #filter 4
        dbc.Col([
            html.Label("Termination status"),
            dcc.Dropdown(
                id="termination-filter",
                options=[{"label": "Terminated for Cause", "value": "Terminated for Cause"},
                         {"label": "Voluntarily Terminated", "value": "Voluntarily Terminated"},
                         ],

                multi=True,
                placeholder="All termination types",
                className="text-dark"),
            ],width=2)
        
        
    ], className="mb-5"),


    # first row Charts
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Attrition Over Time"),
                dcc.Graph(id="chart-attrition-year")
            ]))
        ], width=8),
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Attrition by Gender"),
                dcc.Graph(id="chart-attrition-gender")
            ]))
        ], width=4),
    ], className="mb-4"),

    # second row Charts
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Attrition by Department"),
                dcc.Graph(id="chart-attrition-dept")
            ]))
        ], width=6),
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Top Termination Reasons"),
                dcc.Graph(id="chart-termination-reason")
            ]))
        ], width=6),
    ], className="mb-4"),


    # third Row charts
    dbc.Row([
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Salary Comparison"),
                html.Div(id="table-salary")
            ]))
        ], width=4),
        dbc.Col([
            dbc.Card(dbc.CardBody([
                html.H5("Recent Terminations"),
                html.Div(id="table-recent-terms")
            ]))
        ], width=8),
    ], className="mb-4"),
], fluid=True)



# Callbacks
@app.callback(
    [
        Output('kpi-total', "children"),
        Output("kpi-active", "children"),
        Output('kpi-terminated', "children"),
        Output("kpi-rate", "children"),
        Output("chart-attrition-year", "figure"),
        Output("chart-attrition-gender", "figure"),
        Output("chart-attrition-dept", "figure"),
        Output("chart-termination-reason", "figure"),
        Output("table-salary", "children"),
        Output("table-recent-terms", "children"),
    ],

    [
        Input("dept-filter", "value"),
        Input("gender-filter", "value"),
        Input("year-filter", "value"),
        Input('termination-filter','value'),
    ]
)
def update_dashboard(depts, genders, year_range, termination_filter):

    # make a copy
    dff = df.copy()

    # Apply Filters
    if depts:
        dff = dff[dff["Department"].isin(depts)]
    if genders:
        dff = dff[dff["Sex"].isin(genders)]

    # Split into Active/Terminated
    dff_active = dff[dff["Termd"] == 0]
    dff_term = dff[dff["Termd"] == 1]

    if termination_filter:
        dff_term = dff_term[
            dff_term["EmploymentStatus"].isin(termination_filter)
    ]
        
    if year_range:
        dff_term = dff_term[
            (dff_term["TerminationYear"] >= year_range[0]) &
            (dff_term["TerminationYear"] <= year_range[1])
            ]

    ## TOP OVERALL METRICS
    count_term = len(dff_term)
    count_total = len(dff)
    count_active = count_total - count_term
    rate = round((count_term / count_total * 100), 1) if count_total > 0 else 0

    ## ATTRITION CHARTS
    #Timeline (cumulative)
    total_headcount = len(dff)
    if not dff_term.empty and total_headcount > 0:
        #all years
        present_years = dff_term['TerminationYear'].unique()

        #monthly terms
        actual_terminations = dff_term.groupby(["TerminationYear", "TerminationMonth"]).size().reset_index(
            name="MonthlyTerminations")

        #index the months
        all_months = range(1, 13)
        complete_index_data = [
            (year, month)
            for year in present_years
            for month in all_months
        ]

        complete_index = pd.DataFrame(
            complete_index_data,
            columns=['TerminationYear', 'TerminationMonth']
        )
        timeline_df = pd.merge(
            complete_index,
            actual_terminations,
            on=['TerminationYear', 'TerminationMonth'],
            how='left'
        ).fillna(0)

        #change to integer
        timeline_df['MonthlyTerminations'] = timeline_df['MonthlyTerminations'].astype(int)

        #Calculate cumm. term rate
        timeline_df['CumulativeTerminations'] = timeline_df.groupby('TerminationYear')['MonthlyTerminations'].cumsum()
        timeline_df['CumulativeRate'] = (timeline_df['CumulativeTerminations'] / total_headcount) * 100

        #coloring
        timeline_df["TerminationYear"] = timeline_df["TerminationYear"].astype(str)
        ordered_years = sorted(present_years, reverse=True)
        ordered_years_str = [str(y) for y in ordered_years]

        # Create line chart
        fig_year = px.line(
            timeline_df,
            x='TerminationMonth',
            y='CumulativeRate',
            color='TerminationYear',
            markers=True,
            title='Cumulative Termination Rate (%) by Month per Year',
            template='plotly_dark',
            category_orders={"TerminationYear": ordered_years_str}
        )
        month_names = {i: pd.to_datetime(i, format="%m").strftime("%b") for i  in range(1, 13)}
        fig_year.update_xaxes(
            tickvals=list(range(1, 13 )),
            ticktext=list(month_names.values()),
            title='Month of Termination'
        )
        fig_year.update_yaxes(title="Cumulative Termination Rate (%)", tickformat=".1f")

    else:
        fig_year = px.line(title="No Data")


    #Gender Pie
    fig_gender = px.pie(
        dff_term, names="Sex", hole=0.4,
        color_discrete_map={"M": "#3498db", "F": "#e74c3c"},template='plotly_dark',)



    #Dept Bar
    if not dff_term.empty:
        dept_counts = dff_term["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig_dept = px.bar(dept_counts, x="Count", y="Department", orientation='h',template='plotly_dark')
    else:
        fig_dept = px.bar(title="No Data")

    #Reasons
    if not dff_term.empty:
        reasons = dff_term["TermReason"].value_counts().nlargest(10).reset_index()
        reasons.columns = ["Reason", "Count"]
        fig_reason = px.bar(reasons, x="Count", y="Reason", orientation='h', template="plotly_dark")
    else:
        fig_reason = px.bar(title="No Data")

    # transparent backgrounds
    for fig in [fig_year, fig_gender, fig_dept, fig_reason]:
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    # TABLES

    #Salary Table
    avg_active = dff_active["Salary"].mean() if not dff_active.empty else 0
    avg_term = dff_term["Salary"].mean() if not dff_term.empty else 0

    salary_data = pd.DataFrame({
        "Status": ["Active", "Terminated"],
        "Avg Salary": [f"${avg_active:,.2f}", f"${avg_term:,.2f}"]
    })


    table_salary = dbc.Table.from_dataframe(salary_data, striped=True, bordered=True, hover=True, size="sm")

    # Recent Terms Table
    if not dff_term.empty:
        recent_df = dff_term.sort_values('DateofTermination', ascending=False).head(10)
        recent_df = recent_df[['Employee_Name', 'Department', "TermReason", 'DateofTermination']]
        recent_df["DateofTermination"] = recent_df['DateofTermination'].dt.strftime('%Y-%m-%d')
        table_recent = dbc.Table.from_dataframe(recent_df, striped=True, bordered=True, hover=True, size='sm')
    else:
        table_recent = html.Div('No terminations found matching criteria.', className='text-muted p-2')

    return str(count_total), str(count_active), str(
        count_term), f"{rate}%", fig_year, fig_gender, fig_dept, fig_reason, table_salary, table_recent

if __name__ == "__main__":
    app.run(debug=True)
