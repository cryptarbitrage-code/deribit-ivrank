# Deribit IVRank and IVPercentile
Python code that calculates the IVR and IVP of the Deribit DVOL index.

Dash and plotly used to display the charts in a browser.

<img src="images/screenshot 1.PNG">

One year of DVOL data is displayed on a candlestick chart, 
while the IVR and IVP are shown underneath on gauge dash components.

# The calculations

DVOL values are used to calculate IVR and IVP such that:

iv_rank = (current_vol - year_min) / (year_max - year_min) * 100

iv_percentile = (periods_lower / total_periods) * 100

where:

current_vol = the current value of DVOL

year_min = the lowest value for DVOL over the last year

year_max = the highest value for DVOL over the last year

periods_lower = the number of periods that DVOL closed lower than the current value

total_periods = the total number of periods in the data

# Endpoints used
get_volatility_index_data