import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

# Function to load VIX data from CSV
def load_data():
    try:
        df = pd.read_csv("vix_data.csv", names=["Date", "VIX"], header=None, parse_dates=["Date"])
        df = df.sort_values("Date")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(columns=["Date", "VIX"])

# Function to load the daily report from a text file
def load_report():
    try:
        with open("daily_report.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "Daily report is not available yet."

# Initialize the Dash app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    html.H1("Volatility Index - The Fear Gauge", style={'textAlign': 'center', 'color': 'white'}),

    dcc.Graph(id="graph-vix"),

    dcc.Interval(
        id="interval-update",
        interval=5*60*1000,  # Update every 5 minutes
        n_intervals=0
    ),

    html.Hr(),

    html.H2("Daily Report", style={'textAlign': 'center', 'color': 'white'}),
    html.Pre(id="daily-report", style={
        'color': 'white',
        'padding': '10px',
        'border': '1px solid white',
        'backgroundColor': '#1E1E1E',
        'borderRadius': '5px',
        'whiteSpace': 'pre-line',
        'fontSize': '16px'
    }),

    dcc.Interval(
        id="interval-report",
        interval=60*60*1000,  # Update every hour
        n_intervals=0
    )

], fluid=True, style={'backgroundColor': '#121212', 'padding': '20px'})

# Callback to update the VIX graph with moving averages
@app.callback(
    dash.Output("graph-vix", "figure"),
    [dash.Input("interval-update", "n_intervals")]
)
def update_graph(n_intervals):
    df = load_data()
    if df.empty:
        return px.line(title="No data available")

    # Calculate 5-day and 10-day moving averages
    df["SMA_5"] = df["VIX"].rolling(window=5).mean()
    df["SMA_10"] = df["VIX"].rolling(window=10).mean()

    # Create the figure with VIX and moving averages
    fig = px.line(df, x="Date", y="VIX", title="VIX Evolution",
                  labels={"Date": "Date", "VIX": "Points"},
                  markers=True, line_shape="linear")

    # Add moving average lines
    fig.add_scatter(x=df["Date"], y=df["SMA_5"], mode="lines", name="SMA 5 days", line=dict(color="blue"))
    fig.add_scatter(x=df["Date"], y=df["SMA_10"], mode="lines", name="SMA 10 days", line=dict(color="green"))

    # Ensure VIX remains red
    fig.update_traces(line=dict(color="red", width=2), selector=dict(name="VIX"))
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#121212",
        paper_bgcolor="#121212",
        font=dict(color="white")
    )

    return fig

# Callback to update the daily report
@app.callback(
    dash.Output("daily-report", "children"),
    [dash.Input("interval-report", "n_intervals")]
)
def update_report(n_intervals):
    return load_report()

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)

