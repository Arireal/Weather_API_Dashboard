import streamlit as st
import plotly.express as px
from backend import get_data
from collections import defaultdict

# Add title, text input, slider, selectbox, and subheader
st.title("Weather Forecast for the Next Days")
place = st.text_input("Place:")
days = st.slider("Forecast Days:", min_value=1, max_value=5,
                 help="Select the number of forecast days")
option = st.selectbox("Select data to view",
                      ("Temperature", "Sky"))
st.subheader(f"{option} for the next {days} days in {place}")

if place:
    try:
        # Get the temperature/sky data
        filtered_data = get_data(place, days)

        # Limit the data to the number of forecast days selected (8 intervals per day)
        nr_values = min(days * 8, len(filtered_data))  # Ensure we don't exceed available data
        filtered_data = filtered_data[:nr_values]

        # Group data by day
        grouped_data = defaultdict(list)
        for entry in filtered_data:
            date_part = entry["dt_txt"].split()[0]  # Get only the date (YYYY-MM-DD)
            grouped_data[date_part].append(entry)

        # Ensure that only the requested number of days is shown
        grouped_data = dict(list(grouped_data.items())[:days])

        if option == "Temperature":
            for date, entries in grouped_data.items():
                st.write(f"### {date}")
                temperatures = [entry["main"]["temp"] / 10 for entry in entries]
                times = [entry["dt_txt"].split()[1] for entry in entries]
                figure = px.line(x=times, y=temperatures,
                                 labels={"x": "Time", "y": "Temperature (C)"})
                st.plotly_chart(figure)

        if option == "Sky":
            images = {
                "Clear_day": "images/clear.png",
                "Clear_night": "images/clear_night.png",
                "Clouds": "images/cloud.png",
                "Rain": "images/rain.png",
                "Snow": "images/snow.png"
            }

            for date, entries in grouped_data.items():
                st.write(f"### {date}")
                cols = st.columns(len(entries))  # Create as many columns as there are time slots
                for i, entry in enumerate(entries):
                    sky_condition = entry["weather"][0]["main"]
                    time = entry["dt_txt"].split()[1]
                    hour = int(time.split(":")[0])

                    # Determine whether it's day or night based on time
                    if 6 <= hour < 18:
                        image_key = f"{sky_condition}_day"
                    else:
                        image_key = f"{sky_condition}_night"

                    # Use a default image if the specific day/night image does not exist
                    image = images.get(image_key, images.get(sky_condition, "images/default.png"))

                    # Display time and image side by side
                    with cols[i]:
                        st.write(time)
                        try:
                            st.image(image, width=70)
                        except Exception as e:
                            st.write(f"Error loading image for {sky_condition}: {e}")

    except KeyError:
        st.write("This city is not available on our list. Please type another.")
