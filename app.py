import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.graph_objects as do
import os

app = dash.Dash(__name__,
	external_stylesheets=[dbc.themes.DARKLY],
	meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title='Airbnb Listings Webmap - Tokyo'
server = app.server

map_token = os.environ.get('MAPBOX_TOKEN')
map_style = os.environ.get('MAPBOX_STYLE')

data = pd.read_csv('tokyo_airbnb_listings (cleaned).csv')

neighbour_list = list(data['neighbourhood'].unique())
neighbour_opts = [{'label':k, 'value':k} for k in neighbour_list]

room_list = list(data['room_type'].unique())
room_opts  = [{'label':k, 'value':k} for k in room_list]

price_list = ['<5 000','<10 000', '<30 000','<50 000','<80 000', 'All prices']
price_val = ['5000', '10000', '30000', '50000', '80000', '500000']
price_opts  = [{'label':k, 'value':l} for k,l in zip(price_list,price_val)]

navbar = dbc.Row([
	dbc.Col([
		dbc.Row(html.H4("Airbnb Listings Webmap - Tokyo", className='ml-3 my-2'),
		style={'height':'100%'})
	],
	md=6,
	align='center'),
	dbc.Col([
		dcc.Dropdown(
				id='neighbor-select',
				placeholder='Select neighbourhood',
				clearable=False,
				options=neighbour_opts
			)
	],
	md=2,
	align='center',
	style={'color':'#000000'}),
	dbc.Col([
		dcc.Dropdown(
				id='room-select',
				placeholder='Select room type',
				clearable=False,
				options=room_opts
			)
	],
	md=2,
	align='center',
	style={'color':'#000000'}),
	dbc.Col([
		dcc.Dropdown(
				id='price-select',
				placeholder='Price range',
				clearable=False,
				options=price_opts
			)
	],
	md=2,
	align='center',
	style={'color':'#000000'}),
],
style={'backgroundColor':'#385A7D'}
)


body = dbc.Container([
	navbar,
	dbc.Row([
		dbc.Col([
			dbc.Row([
				dbc.Col(
					dbc.Col(dcc.Graph(id="card1",responsive=True,config={'displayModeBar': False}, style={'height':'100%'})
					,className='my-3 rounded-lg',style={'backgroundColor':'#303030','height':'90%'}),md=6
				),
				dbc.Col(
					dbc.Col(dcc.Graph(id="card2",responsive=True,config={'displayModeBar': False}, style={'height':'100%'})
					,className='my-3 rounded-lg',style={'backgroundColor':'#303030','height':'90%'}),md=6
				)
			],
			justify="center",
			style={'height':'50vh'}
			),
			dbc.Row([
				dbc.Col(
					dbc.Col(dcc.Graph(id="reviewed",responsive=True,config={'displayModeBar': False}, style={'height':'100%'})
					,className='my-3 rounded-lg',style={'backgroundColor':'#303030','height':'90%'},align="center"),md=6
				),
				dbc.Col(
					dbc.Col(dcc.Graph(id="available",responsive=True,config={'displayModeBar': False}, style={'height':'100%'})
					,className='my-3 rounded-lg',style={'backgroundColor':'#303030','height':'90%'}),md=6
				)
			],
			style={'height':'50vh'}
			),
		],
		className='px-4',
		md=6),
		dbc.Col([
			dbc.Row([
				dcc.Graph(id='map',config={'displayModeBar': False}, style={'width':'100%'})
			],style={'backgroundColor':'#01B685','height':'100%'})
		],
		md=6)
	],
	style={'height':'93vh'})
], fluid=True)



def serve_layout():
	return html.Div([body])

app.layout = serve_layout

@app.callback(
	[Output('map','figure'),
	Output('card1','figure'),
	Output('card2','figure'),
	Output('reviewed','figure'),
	Output('available','figure')],
	[Input('neighbor-select','value'),
	Input('room-select','value'),
	Input('price-select','value')]
)
def update_map(neighbor,room,price):
	if (neighbor is None)  or (room is None) or (price is None):
		notice = do.Figure(do.Indicator(
			mode= 'number',
			value= 0,
			title = {"text": 'Please apply filters','font':{'color':'#ffffff','size':15}},
			number={'font':{'color':'#ffffff'}}))
		notice.update_layout(margin= do.layout.Margin(t=0,b=0), plot_bgcolor='#303030', paper_bgcolor='#303030')
		
		return notice,notice,notice,notice,notice

	init_df = data[(data['neighbourhood']==neighbor)&(data['room_type']==room)&(data['price'] < int(price))]
	df_lat = list(init_df['latitude'])
	df_lon = list(init_df['longitude'])
	df_name = list(init_df['name'])
	df_host = list(init_df['host_name'])
	df_price = list(init_df['price'])
	df_nite = list(init_df['minimum_nights'])
	df_rev = list(init_df['number_of_reviews'])
	df_last = list(init_df['last_review'])
	df_ava = list(init_df['availability_365'])
	midpoint = (np.average(init_df['latitude']), np.average(init_df['longitude']))
	
	df_reviewed = init_df['number_of_reviews'].max()
	df_available = init_df['availability_365'].max()
	colored = np.array(['#29EA8B']*init_df.shape[0])
	colored[init_df['number_of_reviews'] == df_reviewed] = '#3498db'
	colored[init_df['availability_365'] == df_available] = '#f39c12'
	
	sized = np.array([7]*init_df.shape[0])
	sized[init_df['number_of_reviews'] == df_reviewed] = 20
	sized[init_df['availability_365'] == df_available] = 20
	
	hover_text = ['Name: '+'{}'.format(t) + '<br>Host: '+'{}'.format(u) + '<br>Price: '+'{}'.format(v) + '<br>Minimum Nights: '+'{}'.format(w) + '<br>No. of Reviews: '+'{}'.format(x) + '<br>Last Review: '+'{}'.format(y) + '<br>Available days per year: '+'{}'.format(z) for t,u,v,w,x,y,z in zip(df_name,df_host,df_price,df_nite,df_rev,df_last,df_ava)]
	
	map1 = do.Figure()
	map1.add_trace(
		do.Scattermapbox(
			lat=df_lat,
			lon=df_lon,
			mode='markers',
			marker=do.scattermapbox.Marker(
				size=sized,
				color=colored,
				opacity=0.7
				),
			text= hover_text,
			hoverinfo='text',
			showlegend= False
		)
	)
	map1.update_layout(
		mapbox= do.layout.Mapbox(
			accesstoken= map_token,
			center= do.layout.mapbox.Center(
				lat= midpoint[0],
				lon= midpoint[1]
			),
			zoom= 13,
			style= map_style
		),
		margin= do.layout.Margin(
			l=0,
			r=0,
			t=0,
			b=0
		)
	)
	
	card1 = do.Figure(do.Indicator(
			mode= 'number',
			value= len(init_df),
			title = {"text": 'Number of Listings','font':{'color':'#ffffff'}},
			number={'font':{'color':'#ffffff', 'size':70}}))
	card1.update_layout(margin= do.layout.Margin(t=40,b=0), plot_bgcolor='#303030', paper_bgcolor='#303030')
	
	card2 = do.Figure(do.Indicator(
			mode= 'number',
			value= np.average(init_df['price']),
			title = {"text": 'Average Price','font':{'color':'#ffffff'}},
			number={'valueformat':'.1f','font':{'color':'#ffffff', 'size':70}}))
	card2.update_layout(margin= do.layout.Margin(t=40,b=0), plot_bgcolor='#303030', paper_bgcolor='#303030')
	
	reviewed = do.Figure(do.Indicator(
			mode= 'number',
			value= df_reviewed,
			title = {"text": "<span style='font-size:0.95em;color:white'>Most Reviews</span><br><span style='font-size:0.7em;color:#3498db'>{}</span>".format(init_df.loc[init_df['number_of_reviews'] == df_reviewed].name.values[0])},
			number={'font':{'color':'#ffffff'}}))
	reviewed.update_layout(margin= do.layout.Margin(t=58,b=0), plot_bgcolor='#303030', paper_bgcolor='#303030')
	
	availbl = do.Figure(do.Indicator(
			mode= 'number',
			value= df_available,
			title = {"text": "<span style='font-size:0.95em;color:white'>Highly Available (days/year)</span><br><span style='font-size:0.7em;color:#f39c12'>{}</span>".format(init_df.loc[init_df['availability_365'] == df_available].name.values[0])},
			number={'font':{'color':'#ffffff'}}))
	availbl.update_layout(margin= do.layout.Margin(t=58,b=0), plot_bgcolor='#303030', paper_bgcolor='#303030')
	
	return map1,card1,card2,reviewed,availbl



if __name__ == "__main__":
    app.run_server(debug=True)

