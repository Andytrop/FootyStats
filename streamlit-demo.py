import streamlit as st
import pandas as pd
import numpy as np

# Title of the app
st.title("Simple Streamlit Demo")

# Add a header
st.header("Interactive Data Explorer")

# Add some text
st.write("This is a simple demo showing Streamlit's basic features.")

# Create a sidebar with some options
st.sidebar.header("Settings")
name = st.sidebar.text_input("Enter your name", "User")
age = st.sidebar.slider("Select your age", 0, 100, 25)

# Display user input
st.write(f"Hello {name}! You are {age} years old.")

# Create a sample dataframe
data = pd.DataFrame(
    np.random.randn(100, 2),
    columns=['x', 'y']
)

# Add a checkbox to show/hide data
if st.checkbox("Show raw data"):
    st.subheader("Raw Data")
    st.write(data)

# Add a button to generate a chart
if st.button("Generate Chart"):
    st.subheader("Scatter Plot")
    st.line_chart(data)

# Add a selectbox
chart_type = st.selectbox(
    "Choose a chart type",
    ["Line", "Bar", "Area"]
)

# Display different chart based on selection
if chart_type == "Line":
    st.line_chart(data)
elif chart_type == "Bar":
    st.bar_chart(data)
else:
    st.area_chart(data)

# Add a footer
st.write("---")
st.write("Created with Streamlit on March 15, 2025")