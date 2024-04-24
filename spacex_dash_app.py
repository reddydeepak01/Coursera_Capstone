# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
    
 # Create a dash application
app = dash.Dash(__name__)

spacex_df.rename(columns = {'Launch Site':'LaunchSite'}, inplace = True)

site = []

for x in spacex_df['LaunchSite']:
    if x not in site:
        site.append(x)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'coCCAFS SLC-40lor': '#503D36',
                                            'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options = [{'label': 'All Sites', 'value':'ALL'}, * [{'label': i, 'value': i} for i in site]], 
                                value = 'Select a Site', placeholder = 'Select Site', searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                min = 0, max = 10000, step = 1000, marks = {i:f'{i}' for i in range(0,10000+1, 1000)
                                }, value = [min_payload, max_payload] ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df[spacex_df['LaunchSite'] == entered_site]
    filtered_df = filtered_df.groupby(['LaunchSite','class']).count().reset_index()
    filtered_df.rename(columns = {'Unnamed: 0':'success_failure_rate'}, inplace = True)
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values = 'class', names = 'LaunchSite', title = 'Spacex data')
        return fig
    else:
        fig_1 = px.pie(filtered_df, values = 'success_failure_rate', names = 'class', 
                     title = f'{entered_site} success and failure rate')
        return fig_1
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id="success-payload-scatter-chart", component_property="figure")
            ,[Input(component_id="site-dropdown", component_property="value"), 
               Input(component_id="payload-slider", component_property="value")])

def get_scatter_chart(entered_site, payload_slider): 
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= min_payload) & (spacex_df['Payload Mass (kg)'] <= max_payload)]
    payload_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_slider[0]) & (filtered_df['Payload Mass (kg)'] <= payload_slider[1])]
    if entered_site == 'ALL':
        fig = px.scatter(payload_df, x="Payload Mass (kg)", y="class", color="Booster Version Category",
                     hover_name="LaunchSite", title='Success payload scatter', size_max=60)
        return fig
    else:
        payload_site_df = payload_df[payload_df['LaunchSite'] == entered_site]
        fig = px.scatter(payload_site_df,x="Payload Mass (kg)", y="class", color="Booster Version Category",
                     hover_name="LaunchSite", title = f'{entered_site} success and failure rate', size_max=60)
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(port=8052, debug = True)