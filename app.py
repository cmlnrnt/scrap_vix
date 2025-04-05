import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

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

def get_vix_alert(vix_value):
    if vix_value < 20:
        return dbc.Badge("Faible volatilité", color="success")
    elif vix_value < 30:
        return dbc.Badge("Volatilité modérée", color="warning")
    else:
        return dbc.Badge("Tension élevée sur les marchés", color="danger")

# Initialize the Dash app with a dark theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    html.H1("Volatility Index - The Fear Gauge", style={'textAlign': 'center', 'color': 'white'}),

    html.Div(id="vix-alert", style={'textAlign': 'center', 'marginBottom': '10px'}),

    dcc.DatePickerRange(
        id='date-range',
        display_format='YYYY-MM-DD',
        start_date_placeholder_text='Start',
        end_date_placeholder_text='End'
    ),

    dcc.Graph(id="graph-vix"),
    dcc.Graph(id="graph-variation"),

    dcc.Interval(id="interval-update", interval=5*60*1000, n_intervals=0),

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

    html.Hr(),
    html.Div(id="stats-summary", style={'color': 'white'}),

    html.A("Télécharger les données CSV", href="/vix_data.csv", target="_blank",
           style={'color': 'lightblue', 'display': 'block', 'marginTop': '20px'}),

    dcc.Interval(id="interval-report", interval=60*60*1000, n_intervals=0)

], fluid=True, style={'backgroundColor': '#121212', 'padding': '20px'})

@app.callback(
    Output("vix-alert", "children"),
    Input("interval-update", "n_intervals")
)
def update_alert(n):
    df = load_data()
    if df.empty:
        return ""
    latest_vix = df.iloc[-1]["VIX"]
    return get_vix_alert(latest_vix)

@app.callback(
    Output("graph-vix", "figure"),
    Output("graph-variation", "figure"),
    Output("stats-summary", "children"),
    [Input("interval-update", "n_intervals"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date")]
)
def update_graphs(n, start_date, end_date):
    df = load_data()
    if df.empty:
        return px.line(title="No data available"), px.bar(title="No variation"), ""

    if start_date and end_date:
        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

    df["SMA_5"] = df["VIX"].rolling(window=5).mean()
    df["SMA_10"] = df["VIX"].rolling(window=10).mean()
    df["Variation (%)"] = df["VIX"].pct_change() * 100

    fig_vix = px.line(df, x="Date", y="VIX", title="VIX Evolution",
                      labels={"Date": "Date", "VIX": "Points"},
                      markers=True, line_shape="linear")

    fig_vix.add_scatter(x=df["Date"], y=df["SMA_5"], mode="lines", name="SMA 5 days", line=dict(color="blue"))
    fig_vix.add_scatter(x=df["Date"], y=df["SMA_10"], mode="lines", name="SMA 10 days", line=dict(color="green"))
    fig_vix.update_traces(line=dict(color="red", width=2), selector=dict(name="VIX"))
    fig_vix.update_layout(template="plotly_dark", plot_bgcolor="#121212", paper_bgcolor="#121212",
                          font=dict(color="white"))

    fig_var = px.bar(df, x="Date", y="Variation (%)", title="Variations du VIX",
                     labels={"Date": "Date", "Variation (%)": "%"})
    fig_var.update_layout(template="plotly_dark", plot_bgcolor="#121212", paper_bgcolor="#121212",
                          font=dict(color="white"))

    summary = html.Div([
        html.P(f"VIX actuel : {df.iloc[-1]['VIX']:.2f}"),
        html.P(f"Max 24h : {df['VIX'].tail(288).max():.2f}"),
        html.P(f"Min 24h : {df['VIX'].tail(288).min():.2f}"),
        html.P(f"Moyenne 24h : {df['VIX'].tail(288).mean():.2f}")
    ])

    return fig_vix, fig_var, summary

@app.callback(
    Output("daily-report", "children"),
    Input("interval-report", "n_intervals")
)
def update_report(n_intervals):
    return load_report()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
