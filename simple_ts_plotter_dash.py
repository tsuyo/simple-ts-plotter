from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import plotly.graph_objects as go

import base64
import io

import pandas as pd

# Create a Dash application
app = Dash(__name__)

# Define the layout of the application
app.layout = html.Div(
    [
        dcc.Store(id="contents"),
        dcc.Store(id="filename"),
        html.H1("Simple Time Series Plotter"),
        # uploader
        dcc.Upload(
            id="file-upload",
            children=html.Div(["Drag and Drop or Select a file"]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "10px",
                "textAlign": "center",
                "margin-bottom": "15px",
            },
            multiple=False,
        ),
        # date picker
        html.Label("Date Range: "),
        dcc.DatePickerRange(id="date-picker-range"),
        # graph
        html.Div(
            id="time-series-graph-container",
            children=html.Div(
                "No Graph", style={"text-align": "center", "margin": "20px"}
            ),
        ),
        # table
        html.Div(
            id="time-series-table-container",
            children=html.Div(
                "No Table", style={"text-align": "center", "margin": "20px"}
            ),
        ),
    ]
)


# Define a call back and update the graph when a date range is selected
@app.callback(
    Output("time-series-graph-container", "children"),
    Output("time-series-table-container", "children"),
    Input("date-picker-range", "start_date"),
    Input("date-picker-range", "end_date"),
    State("contents", "data"),
    State("filename", "data"),
    prevent_initial_call=True,
)
def update_graph(start_date, end_date, contents, filename):
    # print("call update_graph()")

    df = contents_to_df(contents, filename)

    # Filter dataframe by the selected date range
    filtered_df = df[(df["Time"] >= start_date) & (df["Time"] <= end_date)]

    # Create a graph object
    fig = go.Figure()

    # Plot each column (Time: x axis、Others: y axis)
    columns_to_plot = filtered_df.columns[1:]  # Plot other than Time column
    window_size = 5
    for column in columns_to_plot:
        filtered_df[column] = filtered_df[column].rolling(window=window_size).mean()
        fig.add_trace(
            go.Scatter(
                x=filtered_df["Time"],
                y=filtered_df[column],
                mode="lines",
                name=column,
                line=dict(width=3, smoothing=1.0),
            )
        )

    # Define a layout
    fig.update_layout(
        title=f"{start_date[:10]} to {end_date[:10]} ({filename})",
        xaxis_title="Time",
        yaxis_title="Values",
        xaxis_rangeslider_visible=True,  # scroll bar
        height=800,
        hovermode="x unified",
    )
    fig.update_traces(hovertemplate="%{y}")

    table = html.Div(
        [
            dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=20,
            ),
            # html.Hr(),  # horizontal line
            # # For debugging, display the raw contents provided by the web browser
            # html.Div("Raw Content"),
            # html.Pre(
            #     contents[0:200] + "...",
            #     style={"whiteSpace": "pre-wrap", "wordBreak": "break-all"},
            # ),
        ]
    )

    return dcc.Graph(figure=fig, style={"width": "100%"}), table


@callback(
    Output("date-picker-range", "min_date_allowed"),
    Output("date-picker-range", "max_date_allowed"),
    Output("date-picker-range", "start_date"),
    Output("date-picker-range", "end_date"),
    Output("contents", "data"),
    Output("filename", "data"),
    Input("file-upload", "contents"),
    Input("file-upload", "filename"),
    prevent_initial_call=True,
)
def upload_file(contents, filename):
    # print("call upload_file()")

    df = contents_to_df(contents, filename)

    min_date_allowed = df["Time"].min()
    max_date_allowed = df["Time"].max()
    start_date = df["Time"].min()
    end_date = df["Time"].max()

    return min_date_allowed, max_date_allowed, start_date, end_date, contents, filename


def contents_to_df(contents, filename):
    _, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")), parse_dates=["Time"])
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), parse_dates=["Time"])
        return df
    except Exception as e:
        print(e)
        raise e


# Run the application
if __name__ == "__main__":
    app.run_server(debug=True)
