import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards
import plotly.express as px
import plotly.graph_objects as go

# Set Streamlit page config
st.set_page_config(
    page_title="Kaspin Technical test",
    layout="wide",
    initial_sidebar_state="collapsed",  # This sets the sidebar to be collapsed by default
)

# Load the data
df = pd.read_csv("./log.csv")
logo = "./images/kaspin.svg"
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")


# Row 1 - Top Metrics
def top_metric():
    total = len(df)
    mode = len(df["mode"].value_counts())
    peak_hour = df["timestamp"].dt.hour.value_counts().idxmax()
    peak_hour_count = df["timestamp"].dt.hour.value_counts().max()

    day_of_week_map = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    peak_day = df["timestamp"].dt.dayofweek.value_counts().idxmax()
    peak_day_name = day_of_week_map[peak_day]
    peak_day_count = df["timestamp"].dt.dayofweek.value_counts().max()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label="All Activity",
        value=total,
        delta="Total all record in dataset",
        delta_color="off",
    )
    col2.metric(
        label="Activity Mode",
        value=mode,
        delta="All types of activity in dataset",
        delta_color="off",
    )
    col3.metric(
        label="Activity Peak Hour",
        value=f"{peak_hour}:00",
        delta=f"{peak_hour_count} recorded activity",
    )
    col4.metric(
        label="Busiest Day of the Week",
        value=peak_day_name,
        delta=f"{peak_day_count} recorded activity",
    )

    style_metric_cards(border_left_color="#00af81")


# Row 2 - Time Series Plot Using Plotly
def all_time_series():
    df["month_year"] = df["timestamp"].dt.to_period("M")
    activities = df.groupby("month_year").size().reset_index(name="activity_count")
    activities = activities.sort_values(by="month_year", ascending=True)
    activities["month_year"] = activities["month_year"].astype(str)
    st.write()

    # Plot the time series with Plotly and add markers for data points
    fig = px.line(
        activities,
        x="month_year",
        y="activity_count",
        labels={"month_year": "Month and Year", "activity_count": "Activity Count"},
        title="Activity Count Over Time",
        markers=True,
    )

    fig.update_traces(
        line=dict(color="#00af81"),  # Set the line color to #00af81
        fill="tozeroy",  # Fill the area under the line
        fillcolor="rgba(0, 175, 129, 0.3)",  # Set the fill color with 30% opacity
    )
    # Customize the layout to give the chart a card-like appearance
    fig.update_layout(
        plot_bgcolor="#F9F9F9",  # Set the background color to white
        paper_bgcolor="#F9F9F9",  # Set a light background to give a card feel
        margin=dict(l=20, r=20, t=70, b=20),  # Add some padding to the chart
        font=dict(size=14),  # Increase font size for better readability
        title_x=0.05,
        title_y=0.95,
        showlegend=False,  # Hide the legend if there's only one line
        xaxis_title="Time Period",
        yaxis_title="Activity Count",
        xaxis=dict(showgrid=False),  # Hide gridlines
        yaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
        title_font=dict(
            color="#00af81",
            size=30,
            weight=40,  # Change title color to blue  # Set title font size
        ),  # Light gridlines for Y-axis
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)


# Row 3 - Plotly Heatmap for Activity by Time of Day and Day of the Week
def activity_heatmap():
    # Extract the hour and day of the week
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

    # Group by 'day_of_week' and 'hour' to get the count of activities
    activity_heatmap_data = df.groupby(["day_of_week", "hour"]).size().unstack()

    # Reorder the days of the week for a clearer visualization
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    activity_heatmap_data = activity_heatmap_data.reindex(days_order)

    # Fill NaN values with 0
    activity_heatmap_data_filled = activity_heatmap_data.fillna(0)

    # Create the heatmap using Plotly
    fig = go.Figure(
        data=go.Heatmap(
            z=activity_heatmap_data_filled.values,
            x=activity_heatmap_data_filled.columns,
            y=activity_heatmap_data_filled.index,
            colorscale="algae",
            colorbar=dict(title="Count"),
        )
    )

    # Customize the layout to match Seaborn-like presentation
    fig.update_layout(
        title="Activity Levels by Time of Day and Day of the Week",
        xaxis_title="Hour of the Day",
        yaxis_title="Day of the Week",
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        margin=dict(l=20, r=20, t=70, b=20),
        font=dict(size=14),
        title_x=0.05,
        title_y=0.95,
        title_font=dict(
            color="#00af81",
            size=20,
            weight=30,  # Change title color to blue  # Set title font size
        ),
    )

    # Display the heatmap in Streamlit
    st.plotly_chart(fig)


def hourly_activity_bar_chart():
    # Count the activities by hour
    hourly_activity_count = df["timestamp"].dt.hour.value_counts().sort_index()

    # Convert the Series to a DataFrame
    hourly_activity_df = pd.DataFrame(
        {
            "hour": hourly_activity_count.index,
            "activity_count": hourly_activity_count.values,
        }
    )

    # Sort the DataFrame by activity count to get the top 3 highest values
    top_3_values = hourly_activity_df.nlargest(5, "activity_count")[
        "activity_count"
    ].values

    # Create a list of colors, highlighting the top 3 highest values
    colors = [
        "#acb1b5" if value not in top_3_values else "#00af81"
        for value in hourly_activity_df["activity_count"]
    ]

    # Create a bar chart using Plotly
    fig = px.bar(
        hourly_activity_df,
        x="hour",
        y="activity_count",
        labels={"hour": "Hour of the Day", "activity_count": "Activity Count"},
        title="Hourly Activity Count",
    )

    # Update the bar chart with custom colors
    fig.update_traces(marker_color=colors)

    # Customize the layout to give the chart a card-like appearance
    fig.update_layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        margin=dict(l=20, r=20, t=70, b=20),
        font=dict(size=14),
        title_x=0.05,
        title_y=0.95,
        xaxis_title="Hour of the Day",
        yaxis_title="Activity Count",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#E5E5E5"),
        title_font=dict(
            color="#00af81",
            size=20,
            weight=30,  # Change title color to blue  # Set title font size
        ),
    )

    # Display the bar chart in Streamlit
    st.plotly_chart(fig)


def analyze_failed_activities():
    # Filter for failed activities
    failures = df[df["status"] == 1]
    failures_by_activity = failures["mode"].value_counts()
    total_failures = failures_by_activity.sum()

    # Combine smaller failures into an "Other" category
    failures_combined = failures_by_activity[
        failures_by_activity / total_failures >= 0.03
    ]
    other_failures = failures_by_activity[
        failures_by_activity / total_failures < 0.03
    ].sum()
    failures_combined = pd.concat(
        [
            failures_combined,
            pd.Series({"Other (all <3% error)": other_failures}),
        ]
    )

    # Create a pie chart using Plotly
    fig = px.pie(
        failures_combined,
        values=failures_combined.values,
        names=failures_combined.index,
        title="Failed Activities by Type",
        color_discrete_sequence=px.colors.sequential.Aggrnyl,
    )

    fig.update_traces(textposition="inside", textinfo="percent+label", hole=0.2)

    # Customize the layout to give it a card-like appearance
    fig.update_layout(
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        margin=dict(l=20, r=20, t=70, b=20),
        font=dict(size=14),
        title_x=0.05,
        title_y=0.95,
        title_font=dict(
            color="#00af81",
            size=20,
            weight=30,  # Change title color to blue  # Set title font size
        ),  # Font size for better readability
    )

    # Display the pie chart in Streamlit
    st.plotly_chart(fig)


def calculate_success_failure_rates():
    # Group data by activity type (mode) and status (0 = success, 1 = failure)
    grouped = df.groupby(["mode", "status"]).size().unstack(fill_value=0)

    # Calculate success and failure counts
    grouped["Total"] = grouped[0] + grouped[1]
    grouped["Success Rate (%)"] = (grouped[0] / grouped["Total"]) * 100
    grouped["Failure Rate (%)"] = (grouped[1] / grouped["Total"]) * 100

    # Keep only relevant columns and sort by Success Rate
    return (
        grouped[["Total", "Success Rate (%)", "Failure Rate (%)"]]
        .sort_values(by="Success Rate (%)", ascending=False)
        .reset_index()
    )


def failure_analysis_by_day_and_time():
    # Filter for failed activities
    failures = df[df["status"] == 1]

    # Analyze failures by day of the week
    failures_by_day = (
        failures["timestamp"]
        .dt.day_name()
        .value_counts()
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        )
    )

    # Analyze failures by hour of the day
    failures_by_hour = failures["timestamp"].dt.hour.value_counts().sort_index()

    return failures_by_day, failures_by_hour


def row2():
    col1, col2 = st.columns((7, 3))
    with col1:
        all_time_series()
    with col2:
        sort_order = st.selectbox(
            "Activity Count:", options=["Descending", "Ascending"], index=0
        )
        most_counts = df["mode"].value_counts().reset_index()
        most_counts.columns = ["mode", "activity count"]
        if sort_order == "Ascending":
            most_counts = most_counts.sort_values(by="activity count", ascending=True)
        else:
            most_counts = most_counts.sort_values(by="activity count", ascending=False)
        st.dataframe(most_counts, use_container_width=True)


def row3():
    col1, col2 = st.columns(2)
    with col1:
        activity_heatmap()
    with col2:
        hourly_activity_bar_chart()


def row4():
    # Assuming 'status' column where 0 = success and 1 = failure
    total_activities = len(df)
    success_count = len(df[df["status"] == 0])
    failure_count = len(df[df["status"] == 1])

    # Calculate the success and failure rates
    success_rate = (success_count / total_activities) * 100
    failure_rate = (failure_count / total_activities) * 100

    # Display metrics
    col1, col2 = st.columns(2)
    col1.metric(
        label="Success Rate",
        value=f"{success_rate:.2f}%",
        delta=f"{success_count} successful operations",
    )
    col2.metric(
        label="Failure/Error Rate",
        value=f"{failure_rate:.2f}%",
        delta=f"{failure_count} failed operations",
        delta_color="inverse",
    )


def row5():
    col1, col2 = st.columns((6, 4))

    with col1:
        analyze_failed_activities()

    with col2:
        st.write("#### Success and Failure Rates by Activity")

        # Calculate and display the success and failure rates per activity
        success_failure_df = calculate_success_failure_rates()
        st.dataframe(success_failure_df, use_container_width=True)


def row6():
    col1, col2 = st.columns(2)

    # Get the failure data
    failures_by_day, failures_by_hour = failure_analysis_by_day_and_time()

    # Plot failures by day of the week (col1)
    with col1:
        max_value_day = failures_by_day.max()

        # Assign colors: highlight the max value with a different color
        colors_day = [
            "#acb1b5" if value < max_value_day else "#00af81"
            for value in failures_by_day
        ]

        # Create the bar chart for failures by day of the week
        fig_day = px.bar(
            x=failures_by_day.index,
            y=failures_by_day.values,
            labels={"x": "Day of the Week", "y": "Failure Count"},
            title="Failures by Day of the Week",
        )

        # Update the bar chart with custom colors
        fig_day.update_traces(marker_color=colors_day)

        # Customize the layout to give the chart a card-like appearance
        fig_day.update_layout(
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            margin=dict(l=20, r=20, t=70, b=20),
            font=dict(size=14),
            title_x=0.05,
            title_y=0.95,
            title_font=dict(
                color="#00af81",
                size=20,
                weight=30,  # Change title color to blue  # Set title font size
            ),
        )
        st.plotly_chart(fig_day)

    # Plot failures by time of the day (col2)
    with col2:
        # Determine the maximum value for the hour of the day
        max_value_hour = failures_by_hour.max()

        # Assign colors: highlight the max value with a different color
        colors_hour = [
            "#acb1b5" if value < max_value_hour else "#00af81"
            for value in failures_by_hour
        ]

        # Create the bar chart for failures by hour of the day
        fig_hour = px.bar(
            x=failures_by_hour.index,
            y=failures_by_hour.values,
            labels={"x": "Hour of the Day", "y": "Failure Count"},
            title="Failures by Time of the Day",
        )

        # Update the bar chart with custom colors
        fig_hour.update_traces(marker_color=colors_hour)

        # Customize the layout to give the chart a card-like appearance
        fig_hour.update_layout(
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            margin=dict(l=20, r=20, t=70, b=20),
            font=dict(size=14),
            title_x=0.05,
            title_y=0.95,
            title_font=dict(
                color="#00af81",
                size=20,
                weight=30,  # Change title color to blue  # Set title font size
            ),
        )
        st.plotly_chart(fig_hour)


# Display the metrics and plot
st.logo(logo, icon_image=logo)
st.sidebar.write("# Muhammad Afifudin")
st.sidebar.write(" 📧 27afifudin@gmail.com")
st.sidebar.link_button(
    "Check out my Linkedin", "https://www.linkedin.com/in/afifufifudin"
)
st.title("📠 Log Activity Dashboard")
top_metric()
row2()
row3()
st.title("⚠️ Activity Failure Monitoring")
row4()
row5()
row6()
