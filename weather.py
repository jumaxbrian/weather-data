from flask import Flask, jsonify
import pandas as pd
import requests

app = Flask(__name__)

def load_data(woeid, yyyy, mm, dd):
    url = "https://www.metaweather.com/api/location/" + str(woeid) + "/"\
    + str(yyyy) + "/" + str(mm) + "/" + str(dd) + "/" 
    r = requests.get(url)
    print( "Fetching data for " + url )
    if(r.status_code == 200):
        print("Successfully fetched data, saving on disk...")
        date_str = str(yyyy) + "_" + str(mm) + "_" + str(dd)
        filename = str(woeid) + "_" + date_str 
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=256):
                fd.write(chunk)

    return r.status_code

def get_dataframe_from_json(filename):
    df_weather_data = pd.read_json(filename)
    return df_weather_data

def calculate_ratios(weather_dict, counter):
    for key in weather_dict.keys():       
        ratio = (weather_dict[key] * 100)/counter
        weather_dict[key] = round(ratio,2)
    return {"ratios %":weather_dict }

def get_weather_state_data(df_weather_data):
    weather_state_data = {}
    counter = 0
    for row in df_weather_data.itertuples():
        counter += 1
        if(row.weather_state_name in weather_state_data):
            weather_state_data[row.weather_state_name] += 1
        else:
            weather_state_data[row.weather_state_name] = 1
    return {"weather_state_data": weather_state_data, "counter": counter}

def get_analysis(df):
    max_temp = df.the_temp.max()
    min_temp = df.the_temp.min()
    avg_temp = df.the_temp.mean()
    avg_wind = df.wind_speed.mean()
    temp_data = get_weather_state_data(df)
    weather_state_data = temp_data["weather_state_data"]
    counter = temp_data["counter"]
    weather_state_ratios = calculate_ratios(weather_state_data, counter)
    results = {
        "max_temp":max_temp,
        "min_temp":min_temp,
        "avg_temp":avg_temp,
        "avg_wind":avg_wind,
        "weather_state_ratios":weather_state_ratios
    }
    return results

@app.route('/load/', methods=['GET'])
def load():
    # load for cape town
    cape_status_code = load_data(1591691, 2018, 5, 28)

    # load for nairobi
    nbi_status_code = load_data(1528488, 2018, 5, 28)

    output = ""
    if(cape_status_code == 200):
        output += "Cape town details successfully fetched, "
    if(nbi_status_code == 200):
        output += "Nairobi town details successfully fetched "
   
    return output

@app.route('/results', methods=['GET'])
def results():
    df_cape_town = get_dataframe_from_json("1591691_2018_5_28")
    cape_town_analysis = get_analysis(df_cape_town)
    df_nairobi = get_dataframe_from_json("1528488_2018_5_28")
    nairobi_analysis = get_analysis(df_nairobi)
    results = {
        "cape_town": cape_town_analysis,
        "nairobi": nairobi_analysis
    }
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)