
# https://pypi.python.org/pypi/googlefinance.client/1.3.0
# https://github.com/pdevty/googlefinance-client-python/blob/master/googlefinance/client.py
# pip install googlefinance.client
from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data
import pandas 
import json
import yaml
import numpy
import datetime

"""params = [
    # Dow Jones
    {
        'q': ".DJI",
        'x': "INDEXDJX",
    },
    # NYSE COMPOSITE (DJ)
    {
        'q': "NYA",
        'x': "INDEXNYSEGIS",
    },
    # S&P 500
    {
        'q': ".INX",
        'x': "INDEXSP",
    }
]
period = "1Y"
interval = 60*30 # 30 minutes
# get open, high, low, close, volume time data (return pandas dataframe)
df = get_prices_time_data(params, period, interval)
print(df)
#                      .DJI_Open  .DJI_High  .DJI_Low  .DJI_Close  .DJI_Volume  \
# 2016-07-19 23:00:00   18503.12   18542.13  18495.11    18522.47            0
# 2016-07-19 23:30:00   18522.44   18553.30  18509.25    18546.27            0
# 2016-07-20 00:00:00   18546.20   18549.59  18519.77    18539.93            0
# 2016-07-20 00:30:00   18540.24   18549.80  18526.99    18534.18            0
# 2016-07-20 01:00:00   18534.05   18540.38  18507.34    18516.41            0
# ...                        ...        ...       ...         ...          ... """

parameters = [
	{'q': 'C', 'x': 'INDEXNYSEGIS'},
	{'q': 'MS', 'x': 'INDEXNYSEGIS'}
]

def make_determination(day, rows):
	open = []
	close = []
	high = []
	low = []
	volume = []
	delta_open_close = []
	delta_high_low = []
	v = []
	for row in rows:
		open.append(row['Open'])
		close.append(row['Close'])
		high.append(row['High'])
		low.append(row['Low'])
		volume.append(row['Volume'])
		delta_open_close.append(row['Open']-row['Close'])	#not abs val
		delta_high_low.append(row['High']-row['Low'])
		
		#v += ((row['High'] - row['Low']) * row['Volume'])
		#try:
		#	v.append((row['High'] - row['Low']) / row['Low'])
		#except:
		#	print day, row
		#	raw_input('wtf?')
	#std = numpy.std(values)
	#mean = numpy.mean(values)
	
	#coefficient_of_variation = std / mean
	#print coefficient_of_variation
	
	#return numpy.std(delta_high_low) / numpy.mean(delta_high_low)
	#return numpy.std(v)
	
	close_mean_full = numpy.mean(close)
	close_mean_partial = numpy.mean(close[-10:])
	return (close_mean_full-close_mean_partial) / close_mean_full

	
	
def main():
	period = '5Y'
	interval_in_seconds = 60*60
	# get open, high, low, close, volume time data (return pandas dataframe)
	#df = get_prices_time_data(symbols, period, interval_in_seconds)
	dataframe = get_prices_data(parameters, period)	#daily prices
	#columns are symbol_type, where type is in {Open, High, Low, Close, Volume}
	#print dataframe
	
	
	#https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_json.html
	dataframe_json_string = dataframe.to_json(orient='index')
	data_json = yaml.safe_load(dataframe_json_string)
	row_keys = data_json.keys()		#the string versions of the time stamps
	row_keys.sort(key=int)
	
	window_size = 90
	for parameter in parameters:
		symbol = parameter['q']
		print symbol, '------------------------'
		day_ratings = []
		previous_rows = []
		for row_key in row_keys:
			day_string = datetime.datetime.fromtimestamp(int(row_key)/1000).strftime('%Y-%m-%d')
			row = {}	#just the fields for this symbol... its easier to work with
			for k in data_json[row_key]:
				k_split = k.split('_')
				if symbol == k_split[0]:
					row[k_split[1]] = data_json[row_key][k]
			if row['Low'] == 0 or row['High'] == 0 or row['Open'] == 0 or row['Close'] == 0 or row['Volume'] == 0: #not sure why this is in here?? ...Citi, 2017-07-30 which is a Sunday, but that may be just a day off thing?
				continue
			
			previous_rows.append(row)
			if len(previous_rows) > window_size:
				previous_rows = previous_rows[1:]
			determination = make_determination(day_string, previous_rows)
			day_ratings.append([determination, row_key, day_string])
		#end for all rows
		day_ratings.sort(reverse=True)
		for dr in day_ratings[:25]:
			print dr
			
	
	
	
if __name__ == '__main__':
	main()