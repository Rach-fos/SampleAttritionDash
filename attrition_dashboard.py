import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table

# Load data
df = pd.read_csv("HRDataset.csv")

df["Department"] = df["Department"].replace({
    "Admin Offices": "Admin and Executive Offices",
    "Executive Office": "Admin and Executive Offices",
    "Executive Offices": "Admin and Executive Offices"})

# Clean data and add columns
df["Sex"] = df["Sex"].astype(str).str.strip()
df["DateofHire"] = pd.to_datetime(df["DateofHire"], errors="coerce")
df["DateofTermination"] = pd.to_datetime(df["DateofTermination"], errors="coerce")

df["TerminationYear"] = df["DateofTermination"].dt.year
df['TerminationMonth'] = df['DateofTermination'].dt.month
df['HireYear'] = df["DateofHire"].dt.year

#  Overall metrics (unfiltered)
total_employees = len(df)
terminated_employees = int(df["Termd"].sum())
active_employees = int(total_employees - terminated_employees)
overall_attrition_rate = round(terminated_employees / total_employees * 100, 1)

# Filter options
departments = sorted(df["Department"].dropna().unique())
genders = sorted(df["Sex"].dropna().unique())
years = sorted(df["TerminationYear"].dropna().unique())

if years:
    min_year, max_year = int(min(years)), int(max(years))
else:
    min_year = max_year = None


# Dash app setup
app = Dash(__name__)
server = app.server
app.title = "Attrition Metrics"

CARD_STYLE = {
    "backgroundColor": "lightgrey",
    "borderRadius": "10px",
    "padding": "16px",
    "boxShadow": "0 4px 10px rgba(15, 23, 42, 0.08)",
    "marginBottom": "16px",
}

KPI_LABEL_STYLE = {
    "fontSize": "12px",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
    "color": "#6b7280",
    "marginBottom": "4px",
}

KPI_VALUE_STYLE = {
    "fontSize": "26px",
    "fontWeight": "600",
}

# Layout
app.layout = html.Div(
    style={"backgroundColor": "#f4f5f7", "minHeight": "100vh", "padding": "24px"},
    children=[
        html.Div(
            style={"maxWidth": "1200px", "margin": "0 auto"},
            children=[
                html.H1(
                    "Attrition Metrics",
                    style={"fontSize": "28px", "marginBottom": "4px"},
                ),
                html.Div(
                    "Based on Sample Data by Dr. Carla Patalano and Dr. Rich Huebner",
                    style={"color": "#6b7280", "marginBottom": "24px"},
                ),

                # KPI cards
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                        "gap": "16px",
                        "marginBottom": "24px",
                    },
                    children=[
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Total Employees", style=KPI_LABEL_STYLE),
                                html.Div(
                                    id="kpi-total",
                                    style=KPI_VALUE_STYLE,
                                    children=str(total_employees),
                                ),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Active Employees", style=KPI_LABEL_STYLE),
                                html.Div(
                                    id="kpi-active",
                                    style=KPI_VALUE_STYLE,
                                    children=str(active_employees),
                                ),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Terminated (Attrition)", style=KPI_LABEL_STYLE),
                                html.Div(
                                    id="kpi-terminated",
                                    style=KPI_VALUE_STYLE,
                                    children=str(terminated_employees),
                                ),
                                html.Div(
                                    id="kpi-attrition-rate",
                                    style={
                                        "fontSize": "11px",
                                        "display": "inline-block",
                                        "marginTop": "6px",
                                        "padding": "3px 8px",
                                        "borderRadius": "999px",
                                        "backgroundColor": "#eff6ff",
                                        "color": "#1d4ed8",
                                    },
                                    children=f"Attrition rate: {overall_attrition_rate}%",
                                ),
                            ],
                        ),
                    ],
                ),

                # Filters
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1.2fr 1.0fr 1.2fr 1.8fr",
                        "gap": "16px",
                        "marginBottom": "24px",
                    },
                    children=[
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Filter by Department", style=KPI_LABEL_STYLE),
                                dcc.Dropdown(
                                    id="dept-filter",
                                    options=[
                                        {"label": d, "value": d} for d in departments
                                    ],
                                    multi=True,
                                    placeholder="All departments",
                                ),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Filter by Gender", style=KPI_LABEL_STYLE),
                                dcc.Dropdown(
                                    id="gender-filter",
                                    options=[
                                        {"label": g, "value": g} for g in genders
                                    ],
                                    multi=True,
                                    placeholder="All genders",
                                ),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Filter by Employment Status", style=KPI_LABEL_STYLE),

                                dcc.Dropdown(
                                    id="status-filter",
                                    options=[
                                        {"label": "Terminated for Cause", "value": "Terminated for Cause"},
                                        {"label": "Voluntarily Terminated", "value": "Voluntarily Terminated"},
                                    ],
                                    multi=True,
                                    placeholder="All termination types",
                                ),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div("Filter by Termination Year", style=KPI_LABEL_STYLE),
                                (
                                    dcc.RangeSlider(
                                        id="year-filter",
                                        min=min_year,
                                        max=max_year,
                                        step=1,
                                        value=[min_year, max_year],
                                        marks={
                                            int(y): str(int(y)) for y in years
                                        },
                                        tooltip={"placement": "bottom", "always_visible": False},
                                    )
                                    if years
                                    else html.Div(
                                        "No termination years available",
                                        style={"fontSize": "12px", "color": "#9ca3af"},
                                    )
                                ),
                            ],
                        ),
                    ],
                ),

                # Charts row
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "2fr 1.4fr",
                        "gap": "20px",
                        "marginBottom": "24px",
                    },
                    children=[
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div(
                                    "Attrition by Year",
                                    style={"fontSize": "16px", "marginBottom": "4px"},
                                ),
                                html.Div(
                                    "Number of terminations per year (filtered)",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#6b7280",
                                        "marginBottom": "10px",
                                    },
                                ),
                                dcc.Graph(id="chart-attrition-year", style={"height": "280px"}),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div(
                                    "Attrition by Department",
                                    style={"fontSize": "16px", "marginBottom": "4px"},
                                ),
                                html.Div(
                                    "Terminated employees by department (filtered)",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#6b7280",
                                        "marginBottom": "10px",
                                    },
                                ),
                                dcc.Graph(id="chart-attrition-dept", style={"height": "280px"}),
                            ],
                        ),
                    ],
                ),

                # Second charts row
                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "1.2fr 1.8fr",
                        "gap": "20px",
                        "marginBottom": "24px",
                    },
                    children=[
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div(
                                    "Attrition by Gender",
                                    style={"fontSize": "16px", "marginBottom": "4px"},
                                ),
                                html.Div(
                                    "Terminated employees by gender (filtered)",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#6b7280",
                                        "marginBottom": "10px",
                                    },
                                ),
                                dcc.Graph(id="chart-attrition-gender", style={"height": "260px"}),
                            ],
                        ),
                        html.Div(
                            style=CARD_STYLE,
                            children=[
                                html.Div(
                                    "Top Termination Reasons",
                                    style={"fontSize": "16px", "marginBottom": "4px"},
                                ),
                                html.Div(
                                    "Most frequent reasons employees left (filtered)",
                                    style={
                                        "fontSize": "12px",
                                        "color": "#6b7280",
                                        "marginBottom": "10px",
                                    },
                                ),
                                dcc.Graph(id="chart-termination-reason", style={"height": "260px"}),
                            ],
                        ),
                    ],
                ),

# THIRD ROW — Engagement Chart + Salary Table
html.Div(
    style={
        "display": "grid",
        "gridTemplateColumns": "1.7fr 1fr",
        "gap": "20px",
        "marginBottom": "24px",
    },
    children=[
        # Engagement line chart
        html.Div(
            style=CARD_STYLE,
            children=[
                html.Div(
                    "Engagement Survey Scores of Terminated vs Active Employees",
                    style={"fontSize": "16px", "marginBottom": "4px"},
                ),
                html.Div(
                    "Average engagement scores by department (filtered)",
                    style={
                        "fontSize": "12px",
                        "color": "#6b7280",
                        "marginBottom": "10px",
                    },
                ),
                dcc.Graph(id="chart-engagement", style={"height": "300px"}),
            ],
        ),

        # Average salary table
        html.Div(
            style=CARD_STYLE,
            children=[
                html.Div(
                    "Average Salary: Active vs Terminated",
                    style={"fontSize": "16px", "marginBottom": "4px"},
                ),
                html.Div(
                    "Average salaries based on current (filtered)",
                    style={
                        "fontSize": "12px",
                        "color": "#6b7280",
                        "marginBottom": "10px",
                    },
                ),
                dash_table.DataTable(
                    id="salary-table",
                    columns=[
                        {"name": "Status", "id": "Status"},
                        {"name": "Average Salary", "id": "AverageSalary"},
                    ],
                    data=[],
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": "#eef2ff",
                        "fontWeight": "600",
                        "fontSize": "12px",
                    },
                    style_cell={
                        "fontSize": "12px",
                        "padding": "6px 8px",
                        "border": "1px solid #e5e7eb",
                        "textAlign": "left",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "even"},
                            "backgroundColor": "#f9fafb",
                        }
                    ],
                ),
            ],
        ),
    ],
),

                # Recent terminations table
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.Div(
                            "Recent Terminations",
                            style={"fontSize": "16px", "marginBottom": "4px"},
                        ),
                        html.Div(
                            "Last 10 termination records matching current filters",
                            style={
                                "fontSize": "12px",
                                "color": "#6b7280",
                                "marginBottom": "10px",
                            },
                        ),
                        dash_table.DataTable(
                            id="termination-table",
                            columns=[
                                {"name": "Employee", "id": "Employee_Name"},
                                {"name": "Department", "id": "Department"},
                                {"name": "Termination Reason", "id": "TermReason"},
                                {"name": "Termination Date", "id": "DateofTermination"},
                                {"name": "Manager", "id": "ManagerName"},
                            ],
                            data=[],
                            page_size=10,
                            style_table={"overflowX": "auto"},
                            style_header={
                                "backgroundColor": "#eef2ff",
                                "fontWeight": "600",
                                "fontSize": "12px",
                            },
                            style_cell={
                                "fontSize": "12px",
                                "padding": "6px 8px",
                                "border": "1px solid #e5e7eb",
                                "textAlign": "left",
                            },
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "even"},
                                    "backgroundColor": "#f9fafb",
                                }
                            ],
                        ),
                    ],
                ),
            ],
        )
    ],
)



# Callbacks
@app.callback(
    [
        Output("kpi-total", "children"),
        Output("kpi-active", "children"),
        Output("kpi-terminated", "children"),
        Output("kpi-attrition-rate", "children"),
        Output("chart-attrition-year", "figure"),
        Output("chart-attrition-dept", "figure"),
        Output("chart-attrition-gender", "figure"),
        Output("chart-termination-reason", "figure"),
        Output("termination-table", "data"),
        Output("chart-engagement", "figure"),
        Output("salary-table", "data"),
    ],
    [
        Input("dept-filter", "value"),
        Input("gender-filter", "value"),
        Input("year-filter", "value"),
        Input("status-filter", "value"),

    ],
)
def update_dashboard(selected_depts, selected_genders, year_range,selected_status):

    # FILTERING ----------------
    dff = df.copy()

    if selected_depts:
        dff = dff[dff["Department"].isin(selected_depts)]

    if selected_genders:
        dff = dff[dff["Sex"].isin(selected_genders)]


    dff_active = dff[dff["Termd"] == 0]
    dff_term = dff[dff["Termd"] == 1]

    if selected_status:
        dff_term = dff_term[
            dff_term["EmploymentStatus"].isin(selected_status)
        ]

    if year_range and years:
        yr_min, yr_max = year_range
        dff_term = dff_term[
            (dff_term["TerminationYear"] >= yr_min) &
            (dff_term["TerminationYear"] <= yr_max)
        ]

    #  KPI CALCULATIONS ----------------
    total = len(dff)
    terminated = int(dff["Termd"].sum())
    active = len(dff_active)
    attr_rate = round((terminated / total * 100), 1) if total > 0 else 0

    # CUMULATIVE ATTRITION LINE CHART ----------------
    if not dff.empty and not dff_term.empty:

        valid_years = sorted(dff_term["TerminationYear"].dropna().unique())
        chart_data = []
        months = pd.DataFrame({"TerminationMonth": range(1, 13)})

        for year in valid_years:
            term_df = dff_term[dff_term["TerminationYear"] == year]
            headcount = len(dff[dff["HireYear"] <= year])

            monthly_terms = (
                term_df.groupby("TerminationMonth")["EmpID"]
                .count()
                .reset_index(name="Terms")
            )

            monthly = months.merge(monthly_terms, on="TerminationMonth", how="left").fillna(0)
            monthly["CumulativeTerms"] = monthly["Terms"].cumsum()

            monthly["CumulativeAttritionRate"] = (
                monthly["CumulativeTerms"] / headcount * 100 if headcount > 0 else 0
            )

            monthly["Year"] = year
            chart_data.append(monthly)

        final_chart_df = pd.concat(chart_data)

        fig_year = px.line(
            final_chart_df,
            x="TerminationMonth",
            y="CumulativeAttritionRate",
            color="Year",
            markers=True,
            labels={"TerminationMonth": "Month"},
        )
        fig_year.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=list(range(1, 13)),
                ticktext=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
            ),
            margin=dict(l=0, r=0, t=40, b=0),
        )

    else:
        fig_year = px.line(title="No data available for current filters")


    # ATTRITION BY DEPARTMENT ----------------

    if not dff_term.empty:

        # Total employees per department (dept/gender filter)
        dept_totals = (
            dff.groupby("Department")["EmpID"]
            .count()
            .reset_index(name="TotalEmployees")
        )

        # Terminations per department (with year filter)
        dept_terms = (
            dff_term.groupby("Department")["EmpID"]
            .count()
            .reset_index(name="Terminated")
        )

        # calculated attrition rate
        dept_attrition = dept_totals.merge(dept_terms, on="Department", how="left")
        dept_attrition["Terminated"] = dept_attrition["Terminated"].fillna(0)
        dept_attrition["AttritionRate"] = (
                dept_attrition["Terminated"] / dept_attrition["TotalEmployees"] * 100
        ).round(1)

        # Sort
        dept_attrition = dept_attrition.sort_values("AttritionRate", ascending=False)

        fig_dept = px.bar(
            dept_attrition,
            x="Department",
            y="AttritionRate",
            labels={"Department": "Department", "AttritionRate": "Attrition Rate (%)"},
        )
        fig_dept.update_layout(
            xaxis_tickangle=-30,
            margin=dict(l=0, r=0, t=20, b=80),
        )

    else:
        fig_dept = px.bar(title="No termination data for current filters")

    # ATTRITION BY GENDER ----------------
    if not dff_term.empty:
        gender_counts = dff_term.groupby("Sex")["EmpID"].count().reset_index(name="Terminations")
        fig_gender = px.pie(
            gender_counts,
            names="Sex",
            values="Terminations",
            color="Sex",
            color_discrete_map={
                "F": "red",
                "M": "darkblue"
            },
            hole=0.45
        )
    else:
        fig_gender = px.pie(names=["No data"], values=[1])


    # TERMINATION REASONS ----------------
    if not dff_term.empty:
        reason_counts = (
            dff_term.groupby("TermReason")["EmpID"]
            .count()
            .reset_index(name="Count")
            .sort_values("Count", ascending=True)
        )
        fig_reason = px.bar(reason_counts, x="Count", y="TermReason", orientation="h")
        fig_reason.update_layout(
            height=265,
            width=700,
            margin=dict(l=40, r=40, t=40, b=40),


        )
    else:
        fig_reason = px.bar(title="No data")



    # Engagement Survey Scores: Terminated vs Active---
    if "EngagementSurvey" in dff.columns:

        # -- Termed employees engagement --
        eng_term = (
            dff_term.groupby("Department")["EngagementSurvey"]
            .mean()
            .reset_index(name="TerminatedEngagement")
        )

        # -- Active employees engagement --
        eng_active = (
            dff_active.groupby("Department")["EngagementSurvey"]
            .mean()
            .reset_index(name="ActiveEngagement")
        )


        eng_compare = pd.merge(eng_active, eng_term, on="Department", how="outer")

        # sort alphabetically by Dept
        eng_compare = eng_compare.sort_values("Department")

        eng_long = eng_compare.melt(
            id_vars="Department",
            value_vars=["ActiveEngagement", "TerminatedEngagement"],
            var_name="EmployeeStatus",
            value_name="AvgEngagement"
        )

        # Rename legend
        eng_long["EmployeeStatus"] = eng_long["EmployeeStatus"].replace({
            "ActiveEngagement": "Active Employees",
            "TerminatedEngagement": "Terminated Employees"
        })

        #  line chart
        # --- Double Bar Chart: Engagement Scores (Active vs Terminated) ---

        fig_engagement = px.bar(
            eng_long,
            x="Department",
            y="AvgEngagement",
            color="EmployeeStatus",
            barmode="group",
            labels={
                "Department": "Department",
                "AvgEngagement": "Average Engagement Score",
                "EmployeeStatus": "Employee Status"
            },

        )

        fig_engagement.update_layout(
            xaxis_tickangle=-25,
            margin=dict(l=0, r=0, t=30, b=80),
            bargap=0.10,  # spacing between bars
            bargroupgap=0.05,  # spacing between groups
        )


    else:
        fig_engagement = px.line(title="EngagementSurvey column not found")



    # --- Average salary table: Active vs Terminated ---
    if not dff_active.empty:
        avg_active_salary = dff_active["Salary"].mean()
    else:
        avg_active_salary = None

    if not dff_term.empty:
        avg_term_salary = dff_term["Salary"].mean()
    else:
        avg_term_salary = None

    salary_table_df = pd.DataFrame(
        [
            {   "Status": "Active",
                "AverageSalary": f"${avg_active_salary:,.2f}"
                if avg_active_salary is not None
                else "N/A",},

            {   "Status": "Terminated",
                "AverageSalary": f"${avg_term_salary:,.2f}"
                if avg_term_salary is not None
                else "N/A",
            },
        ]
    )

    salary_table_data = salary_table_df.to_dict("records")


    # ---------------- RECENT TERMINATIONS TABLE ----------------
    if not dff_term.empty:
        table_df = dff_term.sort_values("DateofTermination", ascending=False).head(10)
        table_df = table_df.copy()
        table_df["DateofTermination"] = table_df["DateofTermination"].dt.strftime("%Y-%m-%d")
        table_data = table_df[
            ["Employee_Name","Department","TermReason","DateofTermination","ManagerName"]
        ].to_dict("records")
    else:
        table_data = []


    # ---------------- FINAL RETURN ----------------
    return (
        str(total),
        str(active),
        str(terminated),
        f"Attrition rate: {attr_rate}%",
        fig_year,
        fig_dept,
        fig_gender,
        fig_reason,
        table_data,
        fig_engagement,
        salary_table_data,
    )

if __name__ == "__main__":
    app.run(debug=True)
