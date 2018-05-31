from flask import Flask
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

@app.route('/load')
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

if __name__ == '__main__':
    app.run(debug=True)