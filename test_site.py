from flask import Flask, render_template, request, redirect, url_for
import math
import requests
import time

latArr = []
lonArr = []
distArr = []
bigdatablock = []

app = Flask(__name__)


def distCheck(HOME_LAT,HOME_LON):
    for i in range(len(latArr)):
        x = HOME_LAT-float(latArr[i])
        y = HOME_LON-float(lonArr[i])
        dist = math.pow((math.pow(x,2)+math.pow(y,2)),0.5)
        distArr.append(dist)
        #idk what this distance unit it is, degrees?                
    index_min = min(range(len(distArr)), key=distArr.__getitem__) 
    return int(index_min)

def find_planes(HOME_LAT, HOME_LON, halfRange):
    # Clear global arrays to avoid stale data and index mismatches
    latArr.clear()
    lonArr.clear()
    distArr.clear()

    url = "https://opensky-network.org/api/states/all?"
    paramsList = dict(
        
        lomin = float(HOME_LON) - halfRange, 
        lamin = float(HOME_LAT) - halfRange, 
        lomax = float(HOME_LON) + halfRange, 
        lamax = float(HOME_LAT) + halfRange
    )
    
    response = requests.get(url, params=paramsList).json()
    bigdatablock = response["states"]  # List of aircraft data

    if bigdatablock is not None and len(bigdatablock) > 0:
        strOutput = ""
        for i in bigdatablock:
            latArr.append(i[6])
            lonArr.append(i[5])
    
        #closest plane index
        j = distCheck(HOME_LAT, HOME_LON)
                
        strOutput += "the closest plane is " + str(bigdatablock[j][1]) + "<br>"
        
        timeSinceLastContact= time.time() - bigdatablock[j][3]
        strOutput += "last contact was " + str(int(timeSinceLastContact)) + " seconds ago<br>"

        distKm = distArr[j] * 110 
        strOutput += "dist is approx. " + str("%.4f"%distKm) + " km<br>"
        
        strOutput += "is registered in "+ str(bigdatablock[j][2]) + "<br>"
        
        if bigdatablock[j][8] is not True:
            strOutput +="is flying a heading of "+str(bigdatablock[j][10]) + " deg<br>"
            strOutput +="at an altitude of " + str(bigdatablock[j][7]) + " m<br>"
            strOutput +="at a speed of " + str(bigdatablock[j][9]) + " m/s"
        else:    
            strOutput +="is on the ground"
        #if grounded: say on the ground
        #else: alt, spd, hdg
        return strOutput        

    else:
        return "no nearby planes :( "

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        lon = request.form.get('num1')
        lat = request.form.get('num2')
        result = find_planes(float(lat), float(lon), 1)
        #order matters!
        return redirect(url_for('show_result', result=result))  # Redirect after POST

    return render_template('form.html', result=result)

@app.route('/result')
def show_result():
    result = request.args.get('result')  # Retrieve result from URL args
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)