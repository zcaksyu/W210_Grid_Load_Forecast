import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import requests
import json
from dateutil import tz
import holidays
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import LSTM
import tensorflow.keras.layers as ly
from tensorflow.keras.utils import plot_model
from tensorflow.keras.models import Model

class WeatherRequest():
    """Request weather data from the NWS

    Parameters
    ----------
    zone: str
        A string based representation of the NYISO zone
    historical: bool
        defaults to False, flip to True to get historical data instead of
        forecast data
    """

    def __init__(self, zone, historical=False):
        self.zone = zone.lower()
        self.historical = historical
        self.raw_results = None
        self.hourly_results = None

        # Build based on forecast vs observation
        if self.historical is False:
            self.get_forecast()
            self.build_hourly_forecast_objects()
        else:
            self.get_observation()
            self.build_hourly_observation_objects()

    def get_forecast(self):
        """Gets forecast data from NWS"""
        # zone forecast dictionary provides urls keyed to several likely
        # inputs for each zone
        zone_forecast_dictionary = {
            # Zone A
            "buffalo": "https://api.weather.gov/gridpoints/BUF/39,49/forecast/hourly?units=us",
            "west": "https://api.weather.gov/gridpoints/BUF/39,49/forecast/hourly?units=us",
            "zone a": "https://api.weather.gov/gridpoints/BUF/39,49/forecast/hourly?units=us",
            "a": "https://api.weather.gov/gridpoints/BUF/39,49/forecast/hourly?units=us",
            # Zone B
            "rochester": "https://api.weather.gov/gridpoints/BUF/74,62/forecast/hourly?units=us",
            "genesee": "https://api.weather.gov/gridpoints/BUF/74,62/forecast/hourly?units=us",
            "genese": "https://api.weather.gov/gridpoints/BUF/74,62/forecast/hourly?units=us",
            "gens": "https://api.weather.gov/gridpoints/BUF/74,62/forecast/hourly?units=us",
            "zone b": "https://api.weather.gov/gridpoints/BUF/74,62/forecast/hourly?units=us",
            "b": "https://api.weather.gov/gridpoints/BUF/74,62/forecast/hourly?units=us",
            # Zone C
            "syracuse": "https://api.weather.gov/gridpoints/BGM/52,101/forecast/hourly?units=us",
            "central": "https://api.weather.gov/gridpoints/BGM/52,101/forecast/hourly?units=us",
            "centrl": "https://api.weather.gov/gridpoints/BGM/52,101/forecast/hourly?units=us",
            "cent": "https://api.weather.gov/gridpoints/BGM/52,101/forecast/hourly?units=us",
            "zone c": "https://api.weather.gov/gridpoints/BGM/52,101/forecast/hourly?units=us",
            "c": "https://api.weather.gov/gridpoints/BGM/52,101/forecast/hourly?units=us",
            # Zone D
            "plattsburg": "https://api.weather.gov/gridpoints/BTV/78,62/forecast/hourly?units=us",
            "north": "https://api.weather.gov/gridpoints/BTV/78,62/forecast/hourly?units=us",
            "nrth": "https://api.weather.gov/gridpoints/BTV/78,62/forecast/hourly?units=us",
            "zone d": "https://api.weather.gov/gridpoints/BTV/78,62/forecast/hourly?units=us",
            "d": "https://api.weather.gov/gridpoints/BTV/78,62/forecast/hourly?units=us",
            # Zone E
            "utica": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            "mohawk valley": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            "mohawk": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            "mhk vl": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            "mhkv": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            "zone e": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            "e": "https://api.weather.gov/gridpoints/BGM/75,110/forecast/hourly?units=us",
            # Zone F
            "albany": "https://api.weather.gov/gridpoints/ALY/49,108/forecast/hourly?units=us",
            "capital": "https://api.weather.gov/gridpoints/ALY/49,108/forecast/hourly?units=us",
            "capt": "https://api.weather.gov/gridpoints/ALY/49,108/forecast/hourly?units=us",
            "zone f": "https://api.weather.gov/gridpoints/ALY/49,108/forecast/hourly?units=us",
            "f": "https://api.weather.gov/gridpoints/ALY/49,108/forecast/hourly?units=us",
            # Zone G
            "poughkeepsie": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            "hudson valley": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            "hudson": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            "hud vl": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            "hudv": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            "zone g": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            "g": "https://api.weather.gov/gridpoints/ALY/61,11/forecast/hourly?units=us",
            # Zone H
            "newburgh": "https://api.weather.gov/gridpoints/OKX/31,60/forecast/hourly?units=us",
            "millwood": "https://api.weather.gov/gridpoints/OKX/31,60/forecast/hourly?units=us",
            "millwd": "https://api.weather.gov/gridpoints/OKX/31,60/forecast/hourly?units=us",
            "milw": "https://api.weather.gov/gridpoints/OKX/31,60/forecast/hourly?units=us",
            "zone h": "https://api.weather.gov/gridpoints/OKX/31,60/forecast/hourly?units=us",
            "h": "https://api.weather.gov/gridpoints/OKX/31,60/forecast/hourly?units=us",
            # Zone I
            "yonkers": "https://api.weather.gov/gridpoints/OKX/35,44/forecast/hourly?units=us",
            "dunwoodie": "https://api.weather.gov/gridpoints/OKX/35,44/forecast/hourly?units=us",
            "dunwod": "https://api.weather.gov/gridpoints/OKX/35,44/forecast/hourly?units=us",
            "dunw": "https://api.weather.gov/gridpoints/OKX/35,44/forecast/hourly?units=us",
            "zone i": "https://api.weather.gov/gridpoints/OKX/35,44/forecast/hourly?units=us",
            "i": "https://api.weather.gov/gridpoints/OKX/35,44/forecast/hourly?units=us",
            # Zone J
            "new york city": "https://api.weather.gov/gridpoints/OKX/41,32/forecast/hourly?units=us",
            "nyc": "https://api.weather.gov/gridpoints/OKX/41,32/forecast/hourly?units=us",
            "n.y.c.": "https://api.weather.gov/gridpoints/OKX/41,32/forecast/hourly?units=us",
            "zone j": "https://api.weather.gov/gridpoints/OKX/41,32/forecast/hourly?units=us",
            "j": "https://api.weather.gov/gridpoints/OKX/41,32/forecast/hourly?units=us",
            # Zone K
            "islip": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            "li": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            "long island": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            "lisl": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            "longil": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            "zone k": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            "k": "https://api.weather.gov/gridpoints/OKX/63,42/forecast/hourly?units=us",
            }
        url = zone_forecast_dictionary[self.zone]

        response_json = self._send_request(url)
        
        #import json
        #json_object = json.dumps(response_json, indent=4)
        #with open("sample.json", "w") as outfile:
        #    outfile.write(json_object)
        #for e in response_json["properties"]: print(e);  input()
        
        forecasts = response_json["properties"]["periods"]
        self.raw_results = forecasts
        
    def get_observation(self):
        """Gets observation data from NWS"""
        # zone observation dictionary provides urls keyed to several likely
        # inputs for each zone
        zone_observation_dictionary = {
            # Zone A
            "buffalo": "https://api.weather.gov/zones/forecast/NYZ010/observations",
            "west": "https://api.weather.gov/zones/forecast/NYZ010/observations",
            "zone a": "https://api.weather.gov/zones/forecast/NYZ010/observations",
            "a": "https://api.weather.gov/zones/forecast/NYZ010/observations",
            # Zone B
            "rochester": "https://api.weather.gov/zones/forecast/NYZ003/observations",
            "genesee": "https://api.weather.gov/zones/forecast/NYZ003/observations",
            "genese": "https://api.weather.gov/zones/forecast/NYZ003/observations",
            "gens": "https://api.weather.gov/zones/forecast/NYZ003/observations",
            "zone b": "https://api.weather.gov/zones/forecast/NYZ003/observations",
            "b": "https://api.weather.gov/zones/forecast/NYZ003/observations",
            # Zone C
            "syracuse": "https://api.weather.gov/zones/forecast/NYZ018/observations",
            "central": "https://api.weather.gov/zones/forecast/NYZ018/observations",
            "centrl": "https://api.weather.gov/zones/forecast/NYZ018/observations",
            "cent": "https://api.weather.gov/zones/forecast/NYZ018/observations",
            "zone c": "https://api.weather.gov/zones/forecast/NYZ018/observations",
            "c": "https://api.weather.gov/zones/forecast/NYZ018/observations",
            # Zone D
            "plattsburg": "https://api.weather.gov/zones/forecast/NYZ028/observations",
            "north": "https://api.weather.gov/zones/forecast/NYZ028/observations",
            "nrth": "https://api.weather.gov/zones/forecast/NYZ028/observations",
            "zone d": "https://api.weather.gov/zones/forecast/NYZ028/observations",
            "d": "https://api.weather.gov/zones/forecast/NYZ028/observations",
            # Zone E
            "utica": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            "mohawk valley": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            "mohawk": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            "mhk vl": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            "mhkv": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            "zone e": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            "e": "https://api.weather.gov/zones/forecast/NYZ037/observations",
            # Zone F
            "alb": "https://api.weather.gov/zones/forecast/NYZ052/observations",
            "albany": "https://api.weather.gov/zones/forecast/NYZ052/observations",
            "capitl": "https://api.weather.gov/zones/forecast/NYZ052/observations",
            "capt": "https://api.weather.gov/zones/forecast/NYZ052/observations",
            "zone f": "https://api.weather.gov/zones/forecast/NYZ052/observations",
            "f": "https://api.weather.gov/zones/forecast/NYZ052/observations",
            # Zone G
            "poughkeepsie": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            "hudson valley": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            "hudson": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            "hud vl": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            "hudv": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            "zone g": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            "g": "https://api.weather.gov/zones/forecast/NYZ065/observations",
            # Zone H
            "newburgh": "https://api.weather.gov/zones/forecast/NYZ067/observations",
            "millwood": "https://api.weather.gov/zones/forecast/NYZ067/observations",
            "millwd": "https://api.weather.gov/zones/forecast/NYZ067/observations",
            "milw": "https://api.weather.gov/zones/forecast/NYZ067/observations",
            "zone h": "https://api.weather.gov/zones/forecast/NYZ067/observations",
            "h": "https://api.weather.gov/zones/forecast/NYZ067/observations",
            # Zone I
            "yonkers": "https://api.weather.gov/zones/forecast/NYZ071/observations",
            "dunwoodie": "https://api.weather.gov/zones/forecast/NYZ071/observations",
            "dunwod": "https://api.weather.gov/zones/forecast/NYZ071/observations",
            "dunw": "https://api.weather.gov/zones/forecast/NYZ071/observations",
            "zone i": "https://api.weather.gov/zones/forecast/NYZ071/observations",
            "i": "https://api.weather.gov/zones/forecast/NYZ071/observations",
            # Zone J
            "nyc": "https://api.weather.gov/zones/forecast/NYZ072/observations",
            "n.y.c.": "https://api.weather.gov/zones/forecast/NYZ072/observations",
            "coned": "https://api.weather.gov/zones/forecast/NYZ072/observations",
            "new york city": "https://api.weather.gov/zones/forecast/NYZ072/observations",
            "zone j": "https://api.weather.gov/zones/forecast/NYZ072/observations",
            "j": "https://api.weather.gov/zones/forecast/NYZ072/observations",
            # Zone K
            "islip": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            "li": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            "long island": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            "lisl": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            "longil": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            "zone k": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            "k": "https://api.weather.gov/zones/forecast/NYZ080/observations",
            }
        url = zone_observation_dictionary[self.zone]

        response_json = self._send_request(url)
        self.raw_results = response_json["features"]

    def _send_request(self, api_url):
        """Sends the actual request to NWS and returns the JSON data

        Parameters
        ----------
        api_url: str
            The URL for the NWS API request

        Returns
        -------
        dict
            The JSON response in a dictionary format
        """
        header = {"User-Agent": "Capstone, emily.r.fernandes@berkeley.edu"}

        response = requests.get(api_url, headers=header)
        return response.json()

    def build_hourly_forecast_objects(self):
        """Iterates through the raw results and builds hourly objects for
        forecast data."""
        output_dict = {}
        for weather_data in self.raw_results:
            forecast_object = ForecastHour(weather_data)
            output_dict[f"{forecast_object.name}"] = forecast_object.fahrenheit
        self.hourly_results = output_dict
        #for k in output_dict.keys(): print(k,output_dict[k])

    def build_hourly_observation_objects(self):
        """Iterates through the raw results and builds hourly objects for
        observation data."""
        output_dict = {}
        for weather_data in self.raw_results:
            observation_object = ObservationHour(weather_data["properties"])
            if observation_object.celsius!=None: 
                output_dict[f"{observation_object.name}"] = round(1.8 * observation_object.celsius + 32)
        self.hourly_results = output_dict

class ForecastHour():
    """Represents an hour of forecast from the NWS

    Parameters
    ----------
    nws_weather_dictionary: dict
        A dictionary of weather data representing a single hour of forecasts
    """

    def __init__(self, nws_weather_dictionary):
        self.raw_data = nws_weather_dictionary
        self.utc = datetime.fromisoformat(nws_weather_dictionary["startTime"])
        self.fahrenheit = nws_weather_dictionary["temperature"]
        self.description = self.raw_data.get("shortForecast")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.raw_data})"

    @property
    def end(self):
        """Timestamp representing the end of the current hour"""
        return self.utc.astimezone() + timedelta(hours=1)

    @property
    def celsius(self):
        """Temperture converted to celsius"""
        return round((self.fahrenheit - 32) * (5.0/9.0))

    @property
    def hour_beginning(self):
        """Hour presented in HBxx format"""
        return self.utc.strftime("HB%H")

    @property
    def name(self):
        """String representation of a name for the object"""
        return self.utc.strftime("%m-%d-%Y HB%H")

class ObservationHour():
    """Reperesents an hour of observation data from the NWS

    Parameters
    ----------
    nws_weather_dictionary: dict
        A dictionary of weather data representing a single hour of observation
    """

    def __init__(self, nws_weather_dictionary):
        self.raw_data = nws_weather_dictionary
        self.utc = self.naive_utc_to_local()
        self.celsius = nws_weather_dictionary["temperature"]["value"]
        #print(nws_weather_dictionary["temperature"])
        self.description = nws_weather_dictionary["textDescription"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.__class__.__qualname__}({self.raw_data})"

    @property
    def end(self):
        """Timestamp representing the end of the current hour"""
        return self.utc.astimezone() + timedelta(hours=1)

    @property
    def fahrenheit(self):
        """Temperture converted to celsius"""
        return round(1.8 * self.celsius + 32)

    @property
    def hour_beginning(self):
        """Hour presented in HBxx format"""
        return self.utc.strftime("HB%H")

    @property
    def station(self):
        """The station that took the observation"""
        station_string = self.raw_data["station"]
        return station_string[-4:]

    @property
    def name(self):
        """String representation of a name for the object"""
        return self.utc.strftime(f"%m-%d-%Y HB%H {self.station}")

    def naive_utc_to_local(self):
        """NWS returns UTC time at +0000, we want to convert it to NY's
        local time offset before using it"""
        naive = datetime.fromisoformat(self.raw_data["timestamp"])
        local_zone = tz.gettz("America/New_York")
        aware = naive.astimezone(tz=local_zone)
        return aware

def weather_dict():
    W = WeatherRequest('J',True)
    Historical_Weather = W.hourly_results
    W = WeatherRequest('J',False)
    Forecast_Weather = W.hourly_results
    
    keys = list(Historical_Weather.keys())+list(Forecast_Weather.keys())
    Complete_Weather = {}; station_order=['KEWR','KJFK','KLGA','KNYC','KTEB']
    for i,k in enumerate(keys):
        try:   
            k_hist = k[0:-5]
            try:        Complete_Weather[k_hist]=Historical_Weather[f"{k_hist} {station_order[0]}"]
            except:
                try:    Complete_Weather[k_hist]=Historical_Weather[f"{k_hist} {station_order[1]}"]
                except:
                    try:    Complete_Weather[k_hist]=Historical_Weather[f"{k_hist} {station_order[2]}"]
                    except:
                        try:    Complete_Weather[k_hist]=Historical_Weather[f"{k_hist} {station_order[3]}"]
                        except: Complete_Weather[k_hist]=Historical_Weather[f"{k_hist} {station_order[4]}"]
        except:Complete_Weather[k]=Forecast_Weather[k]
    return Complete_Weather
def get_national_holidays(start_date, end_date, country):
    # Get the Bank Holidays for the given country
    holiday_days = holidays.CountryHoliday(country)
    # Create a list of dates between the start and end date
    date_range = pd.date_range(start_date, end_date)
    # Filter the dates to only include Bank Holidays
    national_holidays = [str(date)[0:10] for date in date_range if date in holiday_days]
    return national_holidays

def enforce_5min(df,c_time=''):
    try:    df[c_time]=pd.to_datetime(df[c_time])
    except: df=df
    
    try:    
        df.index = df[c_time]
        df = df.drop_duplicates(subset=c_time)
    except: df=df
    
    df = df.asfreq('5T')
    try:    df = df.drop(columns=[c_time])
    except: df=df
    df = df.interpolate(method='linear', order=1, limit=10, limit_direction='both').bfill().ffill()
    #df = df.bfill().ffill()
    return df
    
#Collect last 90 Mins of NYISO Load (Collect Timestamps from here)
def return_NYISO_Load():
    #Request Today's Load 
    str_dt = datetime.now().strftime('%Y%m%d')
    url = f"http://mis.nyiso.com/public/csv/pal/{str_dt}pal.csv"
    
    #Format to DF
    r = requests.get(url, stream=True)
    if r.ok:        
        v=''
        for chunk in r.iter_content(chunk_size=1024 * 8): v=v+chunk.decode()
        v_new = []
        for ln in  v.split('\n'):
            vv = ln.replace('"','').replace('\r','').split(',') 
            if vv!=['']:v_new.append(vv)#;print(vv) 

    df = pd.DataFrame(v_new[1:],columns=v_new[0])
    
    #Collect only NYC and Enfore 5 Minute Freq and Interpolate
    df = df[df['Name']=='N.Y.C.']
    df = df[df['Load'].astype(str)!='']
    df = df[['Load', "Time Stamp"]]
    df["Load"] = df["Load"].astype(float)
    df['Time Stamp'] = pd.to_datetime(df['Time Stamp'],format="%m/%d/%Y %H:%M:%S")
    df = enforce_5min(df, 'Time Stamp')   
    
    df = df.iloc[-18:]    
    t = np.array(df.index)
    load = df['Load'].astype(float).values
    return t,load

def return_solar_data(url_type):
    
    # api_key = "rcJVj9RL-a6TKHOd07kMvAJGSWpmXYUA"
    # #api_key = "FuPQMZl6ZqVlZ70Qug1i6X9oevjzxgND"
    # #api_key = "wj4V2dP8klYCQVHvhUilFyT-9-d111xi"
    
    # lat = '40.712775'
    # lon = '-74.005973'
    # unmetered_lat = "-33.856784"
    # unmetered_lon = "151.215297"
    # lat = unmetered_lat
    # lon = unmetered_lon
    # hr = 168

    # if url_type=='Actual':
    #     #url = f"https://api.solcast.com.au/world_radiation/estimated_actuals?latitude={lat}&longitude={lon}&hours={hr}&output_parameters=air_temp,dni,ghi&format=json".format(lat=unmetered_lat, lon=unmetered_lon, hr=168)
    #     url = f"https://api.solcast.com.au/data/live/radiation_and_weather?api_key={api_key}&latitude={lat}&longitude={lon}&output_parameters=air_temp,dni,ghi&format=json"
    # else:
    #     url = f"https://api.solcast.com.au/world_radiation/forecasts?api_key={api_key}&latitude={lat}&longitude={lon}&hours=168&output_parameters=air_temp,dni,ghi&format=json"
    
    # response = requests.get(url)
    # data = json.loads(response.text)    
    # df = pd.DataFrame(data['forecasts'])
    df = pd.read_csv("solar_data.csv")
    print(df)
    #Create Datetime Index & enforce 5 Min Freq
    df["period_end"] = pd.to_datetime(df["period_end"], utc=True).dt.tz_convert('US/Eastern')
    df["period_end"] = df["period_end"].apply(lambda x: x + timedelta(hours=5))
    df = df[['dni',"period_end"]]
    print(df)
    df = enforce_5min(df, 'period_end')
    df.index = [ pd.to_datetime(str(e)[:-7]) for e in df.index ]
    print(df)

    return df


def return_datetime_flags(t):
    now_i = datetime.now()
    td = timedelta(days=1)
    holidays = get_national_holidays(now_i-td , now_i+td , 'US')
    
    uw = ['04:00','04:05','04:10','04:15','04:20','04:25',
          '04:30','04:35','04:40','04:45','04:50','04:55',
          '05:00','05:05','05:10','05:15','05:20','05:25',
          '05:30']
    
    ow = ['06:15','06:20','06:25',
          '06:30','06:35','06:40','06:45','06:50','06:55',
          '07:00','07:05','07:10','07:15','07:20','07:25',
          '07:30','07:35','07:40','07:45',
          '16:30','16:35','16:40','16:45','16:50','16:55',
          '17:00','17:05','17:10','17:15','17:20','17:25','17:30']
    
    uw_v=[]; ow_v=[]; holiday_weekend = []
    for dt in t:
        e = str(dt.hour).zfill(2)+":"+str(dt.minute).zfill(2)

        if e in uw: uw_i=1
        else:       uw_i=0
        
        if e in ow: ow_i=1
        else:       ow_i=0
        
        if dt.weekday() in [5,6]:   we_h_v = 1
        else:                       we_h_v = 0
        
        if str(dt)[0:10] in holidays: we_h_v = 1
    
        
        uw_v.append(uw_i)
        ow_v.append(ow_i)
        holiday_weekend.append(we_h_v)
    
    return np.array(uw_v), np.array(ow_v), np.array(holiday_weekend)



def format_inputs():
    t,load = return_NYISO_Load()
    current_time = t[-1]
    t = [ datetime.strptime(str(e),'%Y-%m-%dT%H:%M:%S.000000000') for e in t]
    t_f = [e + timedelta(minutes=90) for e in t]
    
    #print(t);    print(load)
    
    #Call Weather API for Weather 
    temp_dict = weather_dict()
    temp_dict_dt = {}
    for k in temp_dict.keys(): 
        dt = pd.to_datetime(k,format ='%m-%d-%Y HB%H')
        temp_dict_dt[dt]=temp_dict[k]
    
    temp_df = pd.DataFrame.from_dict(temp_dict_dt, orient='index')    
    temp_df = enforce_5min(temp_df)
    
    temp = np.array([list(e)[0] for e in temp_df[ temp_df.index.isin(t)].values])
    temp_f = np.array([list(e)[0] for e in temp_df[ temp_df.index.isin(t_f)].values])
    #print(temp)    print(temp_f)
    
    #Call Solar API for Solar 
    #df = return_solar_data('Actual?')
    #except: df = pd.DataFrame()
    #solar = np.array(list(df[df.index.isin(t)].values))
    
    #try:    df = return_solar_data('Forecast')
    #except: df = pd.DataFrame()
    #solar_f = np.array(list(df[df.index.isin(t_f)].values))
    #print(solar);    print(solar_f)
    solar =np.array([39.        ,  43.5       ,  48.        ,  52.5       , 57.        ,  61.5       ,  66.        ,  70.33333333, 74.66666667,  79.        ,  83.33333333,  87.66666667, 92.        ,  96.66666667, 101.33333333, 106.        , 110.66666667, 115.33333333])
    solar_f=np.array([120.        , 121.        , 122.        , 123.        , 124.        , 125.        , 126.        , 119.66666667, 113.33333333, 107.        , 100.66666667,  94.33333333,  88.        ,  77.5       , 67.        ,  56.5       ,  46.        ,  35.5])
    ###########################
    #Create Time Flag & Weekend/Holiday Variables
    uw_v, ow_v,weekend_holiday = return_datetime_flags(t)
    #print(uw_v);    print(ow_v);    print(weekend_holiday)
    #############

    input_list = np.array([load,solar.ravel(),temp,solar_f.ravel(),temp_f,uw_v,ow_v,weekend_holiday])
    print(input_list)
    return input_list

def tranform_data(input_list):
    m = 5574.113154123897;std = 1157.6820234795014
    m_s = 176.74872041098973 ;std_s = 310.4973536354869
    m_t = 56.030910041113;std_t = 16.507268780702415
    m_d = 0;std_d=1
    
    m_list = [m,m_s,m_t,m_s,m_t,m_d,m_d,m_d,m_d]
    std_list = [std,std_s,std_t,std_s,std_t,std_d,std_d,std_d,std_d]

    input_list_xfr = [(ln-m_list[i])/std_list[i]  for i,ln in enumerate(input_list)]
    return input_list_xfr

def untransform_prediction(load):
    m = 5574.113154123897;std = 1157.6820234795014
    return (load * std)+m

def import_model(path):

    def create_LSTM_model(LSTM_i = 4, dropout=0.3, recurrent_dropout=0,
                        var_num = 8,
                        hist_window=18,forecast_window=18):

        model = Sequential()
        model.add(LSTM(LSTM_i, input_shape=(var_num,hist_window),recurrent_dropout = recurrent_dropout))
        model.add(Dense(100))
        model.add(Dropout(dropout))
        model.add(Dense(forecast_window))
        model.compile(loss='mean_squared_error', optimizer='adam')
        return model

    model_name = "lstm_cv_final.h5"

    model = create_LSTM_model(LSTM_i = 500, dropout=0.05, recurrent_dropout=0.1,
                      var_num = 8,
                      hist_window=18,forecast_window=18)
    model.load_weights(f"{model_name}") 
    #model.eval()
    return model

def make_prediction(trans_data, model):
    return untransform_prediction(model.predict(trans_data))

if __name__ == "__main__":
    inputs = format_inputs()
    for ln in inputs: print(ln)
