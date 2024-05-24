import streamlit as st
import pandas as pd
import plotly.express as px

# Function to load the uploaded CSV file
@st.cache(allow_output_mutation=True)
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        st.write(df.head())  # Display the first few rows for debugging
        return df.copy()  
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Adding a title
st.title('Following State Layoffs!')

# Load WARN data
# For Streamlit Cloud, ensure the file is in the correct location
warn_data_path = 'warn_notices.csv'  # Ensure the CSV file is in the same directory as the app
warn_data = load_data(warn_data_path)

# State population data
population_data = {
    "State": ["California", "Texas", "Florida", "New York", "Pennsylvania", "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan", 
              "New Jersey", "Virginia", "Washington", "Arizona", "Tennessee", "Massachusetts", "Indiana", "Missouri", "Maryland", "Wisconsin"],
    "Population": [38889770, 30976754, 22975931, 19469232, 12951275, 12516863, 11812173, 11145304, 10975017, 10041241,
                   9320865, 8752297, 7841283, 7497004, 7204002, 7020058, 6892124, 6215144, 6196525, 5931367]
}

population_df = pd.DataFrame(population_data)

# Function to process data to count layoffs by state
def process_data(layoff_df, population_df):
    if 'State' in layoff_df.columns and 'Number of Workers' in layoff_df.columns:
        layoff_df['Number of Workers'] = pd.to_numeric(layoff_df['Number of Workers'], errors='coerce')
        state_layoffs = layoff_df.groupby('State')['Number of Workers'].sum().reset_index()
        state_layoffs.columns = ['State', 'Total Layoffs']
        
        merged_df = state_layoffs.merge(population_df, on='State')
        merged_df['Layoff Rate'] = (merged_df['Total Layoffs'] / merged_df['Population']) * 100000
        return merged_df
    else:
        st.error("The data does not contain the required columns.")
        return None

# Function to process data for the line graph
def process_data_for_line_graph(df):
    if 'WARN Received Date' in df.columns and 'Number of Workers' in df.columns:
        df['WARN Received Date'] = pd.to_datetime(df['WARN Received Date'], errors='coerce')
        df = df.dropna(subset=['WARN Received Date'])
        df['Number of Workers'] = pd.to_numeric(df['Number of Workers'], errors='coerce')
        line_data = df.groupby('WARN Received Date')['Number of Workers'].sum().reset_index()
        return line_data
    else:
        st.error("The data does not contain the required 'WARN Received Date' or 'Number of Workers' columns.")
        return None

# Calculating layoff likelihood
def calculate_layoff_likelihood(state, industry, warn_df):
    filtered_df = warn_df[(warn_df['State'] == state) & (warn_df['Industry'] == industry)]
    total_layoffs = filtered_df['Number of Workers'].sum()
    total_companies = filtered_df['Company'].nunique()
    return total_layoffs, total_companies

# Sidebar for tabs
tabs = st.sidebar.radio("Select a tab", ('Home', 'Layoff Likelihood'))

if tabs == 'Home':
    st.write("Welcome to the Home Tab!")
    
    if warn_data is not None and population_df is not None:
        st.write("Below Are Some Visuals For You To Explore!")
        
        # Process data for other visualizations
        state_layoff_rates = process_data(warn_data, population_df)
        
        # Line graph
        line_data = process_data_for_line_graph(warn_data)
        if line_data is not None:
            line_fig = px.line(
                line_data,
                x='WARN Received Date',
                y='Number of Workers',
                title='Layoffs Over Time',
                labels={'Number of Workers': 'Number of Workers Laid Off'}
            )
            st.plotly_chart(line_fig)

        if state_layoff_rates is not None:
            # Bar plot
            bar_fig = px.bar(
                state_layoff_rates,
                x='State',
                y='Layoff Rate',
                title='Layoff Rates by State (per 100,000 people)',
                labels={'Layoff Rate': 'Layoff Rate (per 100,000 people)'},
                color='Layoff Rate',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(bar_fig)
            
            # Bubble plot
            bubble_fig = px.scatter(
                state_layoff_rates,
                x='State',
                y='Layoff Rate',
                size='Layoff Rate',
                color='Layoff Rate',
                hover_name='State',
                size_max=60,
                title='Layoff Rates by State (per 100,000 people)',
                labels={'Layoff Rate': 'Layoff Rate (per 100,000 people)'},
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(bubble_fig)
            
            # Heatmap 
            # heatmap_fig = px.choropleth(
            #     state_layoff_rates,
            #     locations='State',
            #     locationmode="USA-states",
            #     color='Total Layoffs',
            #     hover_name='State',
            #     hover_data=['Total Layoffs', 'Population', 'Layoff Rate'],
            #     color_continuous_scale='Reds',
            #     title='Number of Workers Laid Off by State'
            # )
            # st.plotly_chart(heatmap_fig)

elif tabs == 'Layoff Likelihood':
    st.write("Check your layoff likelihood based on state and industry.")
    
    if warn_data is not None:
        
        state = st.selectbox('Select your state', warn_data['State'].unique())
        industry = st.selectbox('Select your industry', warn_data['Industry'].dropna().unique())

        # Calculate the likelihood
        if st.button('Check Layoff Likelihood'):
            total_layoffs, total_companies = calculate_layoff_likelihood(state, industry, warn_data)
            st.write(f"In {state}, the total number of workers laid off in the {industry} industry is {total_layoffs} from {total_companies} companies.")

        
        if st.checkbox('Show filtered data'):
            st.dataframe(warn_data[(warn_data['State'] == state) & (warn_data['Industry'] == industry)])
