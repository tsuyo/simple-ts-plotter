import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import base64

def main():
    st.title("Simple Time Series Plotter")
    
    # File uploader component
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=["csv", "xlsx"],
        help="Upload a file with a 'Time' column and numeric data columns"
    )
    
    if uploaded_file is None:
        return

    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, parse_dates=['Time'])
        else:
            df = pd.read_excel(uploaded_file, parse_dates=['Time'])
                
        # Select date range
        min_date = df['Time'].min().date()
        max_date = df['Time'].max().date()
            
        # Configure date range picker layout
        date_container = st.container()
        with date_container:
            # Create two columns for center alignment
            # [1, 4] is the ratio of each column
            date_cols, sel_col = st.columns([1, 4])
            with date_cols:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
                with col2:
                    end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
            with sel_col:
                # Moving average window size selector
                window_size = st.slider("Moving Average Window Size", min_value=1, max_value=100, value=5)

        # Filter data based on selected data range
        mask = (df['Time'].dt.date >= start_date) & (df['Time'].dt.date <= end_date)
        filtered_df = df[mask]
            
        # Create plot
        fig = go.Figure()
            
        # Plot each column (ecluding Time column)
        columns_to_plot = filtered_df.columns[1:]
        for column in columns_to_plot:
            smoothed_data = filtered_df[column].rolling(window=window_size).mean()
            fig.add_trace(
                go.Scatter(
                    x=filtered_df['Time'],
                    y=smoothed_data,
                    mode='lines',
                    name=column,
                    line=dict(width=3, smoothing=1.0)
                )
            )
            
        # Configure plot layout
        fig.update_layout(
            title=f"{start_date} to {end_date} ({uploaded_file.name})",
            xaxis_title="Time",
            yaxis_title="Values",
            xaxis_rangeslider_visible=True,
            height=800,
            hovermode="x unified"
        )
        fig.update_traces(hovertemplate="%{y}")
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Displya data table
        st.subheader("Data Table")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    st.set_page_config(
        page_title="Simple Time Series Plotter",
        page_icon="📈",
        layout="wide"
    )
    main()
