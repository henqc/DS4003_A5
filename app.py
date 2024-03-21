#Install all needed dependencies
import pandas as pd
import numpy as np 
import plotly.express as px
import seaborn as sns
from dash import Dash, dcc, html, Input, Output

#Read in csv into a pandas data frame
df = pd.read_csv("gdp_pcap.csv")
# load the CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 
#Initialize the Dash app
app = Dash(__name__, external_stylesheets=stylesheets)

# Define a function to convert the k to thousands
# Will take any instance of k and remove it and return the correct numeric version
# If k is not present it will return the proper numeric
def convert(x):                              
    if isinstance(x, str) and 'k' in x.lower():             
        return float(x[:-1]) * 1000                         
    return float(x)                
                         
# Convert all columns
convert_cols = {str(year): convert for year in range(1800, 2101)}      
# Reread in csv with the necessary converter 
df = pd.read_csv("gdp_pcap.csv", converters = convert_cols)   

#sorting years to get the min and max years
years = sorted(int(year) for year in df.columns if year.isdigit())

# Callback to update the graph based on dropdown and slider inputs
@app.callback(
    Output('line graph', 'figure'),
    [Input('country dropdown', 'value'),
    Input('year slider', 'value')]
)

#Link between the graph and the dropdown and slider components
def update_graph(selected_countries, selected_years):
    # If no countries are selected default to an empty graph
    if not selected_countries:
        selected_countries = []
    # Defulat to having full range selected
    if not selected_years:
        selected_years = [min(years), max(years)]
    # Filter the data frame by which countries are currently selected
    filtered_df = df[df['country'].isin(selected_countries)]
    # Filter the year array for only the range of years selected in the slider
    filtered_years = [str(year) for year in range(selected_years[0], selected_years[1] + 1)]
    # Filter the data frame to keep only the selected years and add country col back
    filtered_df = filtered_df[['country'] + filtered_years]
    # Melt the filtered DataFrame into a plottable form
    df_plottable = pd.melt(filtered_df, id_vars=['country'], value_vars=filtered_years, var_name='year', value_name='gdp')
    # Ensure year is treated as an integer (although some of them are weird objects so I dont really know how to deal with them)
    df_plottable['year'] = df_plottable['year'].astype(int)
    # Create the plot
    fig = px.line(df_plottable, 
                  x='year', 
                  y='gdp', 
                  color='country', 
                  line_group='country',
                  title='GDP Per Capita Over Time',
                  labels={'gdp': 'GDP per Capita', 'year': 'Years'})
    
    
    return fig

#sorting years to get the min and max years
years = sorted(int(year) for year in df.columns if year.isdigit())
#App layout to define the structure of the web page
app.layout = html.Div([
    #Contaier div to store all the components
    html.Div(children=[
        #Title describing the purpose of the web app
        html.H1('UI Components for Gapminder Dataset'),
        #Description of the data and app 
        html.P('''
        This dashboard allows you to explore the GDP per capita. You can select multiple countries and a range of years to see trends in the GDP per capita. A visulization will be displayed in the form of a line graph.
        '''),
        #Header for country dropdown with a small margin on the top to seperate it from the title
        html.H2('Select Countries and a Range of Years', style = {'margin-top': '3%'}) ,
        
        html.Div(children=[
            html.Div(
                # Country dropdown component
                dcc.Dropdown(
                    # Identifier for the country dropdown component
                    id='country dropdown',  
                    #Using the dataframe to populate the options by creating key value pairs with unique contry names
                    options=[{'label': country, 'value': country} for country in df['country'].unique()],  
                    #Custom placeholder text to describe what actions to take as a user
                    placeholder = 'Select One or More Countries',
                    # Allows user to select multiple countries at once
                    multi=True,  
                # Styling to fit half the width
                ), className = 'six columns'
            ),

            # Year range slider
            html.Div(
                dcc.RangeSlider(
                    # Identifier for the year range slider component
                    id='year slider',
                    # Lower bound as determined from our sorted year array 
                    min=years[0],
                    # Upper bound as determined from our sorted year array 
                    max=years[-1],
                    # Default to having full range selected
                    value=[years[0], years[-1]],
                    # Put a mark every 10 years for readability
                    marks={str(year): str(year) for year in years[::50]},
                # Styling to fit half the width
                ), className = 'six columns'
                
            ),  
            # Styling to fit entire width
        ], className = 'twelve columns'),

        # Line Graph
        html.Div(
            # Display graph on web app 
            dcc.Graph(id='line graph'),
            # Styling to fit entire width
            className = 'twelve columns'
        ),

    #Styling for the container div that has all components stored in column direction and centers them
    ], style={'display': 'flex', 'alignItems': 'center', 'height': '100vh', 'flex-direction': 'column'}),  
])

#Run the app
if __name__ == '__main__':
    app.run(debug=True)