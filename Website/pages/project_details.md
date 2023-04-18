## The Problem

Reliable electricity is one aspect of our daily lives that we often take for granted — when was the last time you thought about what is powering your household lights and appliances?
 
But behind the scenes, electricity generation is quite complex. Because it is not freely available in nature, it must be produced. In order to reliably run an electrical grid and generate the necessary electricity to power our cities, system operators must first know the amount of electrical load that must be served. Failure to properly predict and supply load can result in disruptive blackouts.
 
One of the most recent disruption was the 2021 Great Texas Freeze. Texas suffered a major power crisis when three severe winter storms hit the United States, triggering the worst energy infrastructure failure in Texas state history. The Electric Reliability Council of Texas (ERCOT), which supplies power to 90% of the state, greatly underestimated electric demand. This resulted in at least 57 deaths and over $195 billion in property damage.
 
Therefore, electric load forecasting, which is predicting the amount of electrical power required to meet customer demand, is incredibly important. By better predicting load, we can 
1. __Reduce Liability__: If we have enough electricity, we reduce potential major blackouts, saving billions in property damages.
2. __Decrease Price of Electricity__: Electricity bills can get pricy. By preventing waste, we can optimize for more cost saving measures for consumers.
3. __Increase Reliability__: Better forecasts means we can better plan capacity and ensure consumers are supplied with the required energy to keep their homes running.


#### We are different

While there are already several load forecasting programs on the market, these programs primarily focus on forecasting hourly loads days in advance. Our objective is to provide system operators with load in real time, allowing them to account for more sensitive real-time weather events like sudden drops in wind or a large system of clouds rolling in. Our first use case will be New York City. 

New York Independent System Operator (NYISO) is responsible for operating wholesale power markets in New York and is our intended audience of this project. We plan on working with them after this project to implement this model in their control center.

#### Our Model

__Our model predicts [for the next 90 mins in 5 min intervals] the forecasted electric load with up to 98% accuracy__. Our model was evaluated based on the following criteria:
- __Relative Root Mean Square Error (RRMSE)__
    - This is primarily used to compare different classes of models we worked with.
- __Forecasting Error Distribution__  
    - While we want our forecasts to be as accurate as possible, ramifications for under-predicting is worse than over-forecasting. Too much load results in more expensive electricity but too little load can result in major blackouts.
- __Max Forecasted Error__: Largest error [MWh] between the forecasted and actual value 
    - New York Independent System Operator (NYISO) procures 2,620 MW of reserves for New York State (1,000 MWs for NYC) each day. Reserves are MW NYISO buys on top of the forecasted load to cover contingencies like generators tripping offline or lines unexpected coming out of service. Using reserves to accommodate forecasting error is something NYISO tries to avoid and was baked into our model considerations.

## Data Sources

We used historic and forecasted load, weather and solar data for our model and forecast calculations.

1. __New York State Electric Load__ provided by NYISO
2. __Weather__ provided by National Oceanic & Atmospheric Administration (NOAA CDO)
3. __Solar__ provided by Solcast, 2019. 
    - Global solar irradiance data and PV system power output data. URL https://solcast.com/