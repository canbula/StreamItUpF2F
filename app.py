from flask import Flask
from flask import render_template
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import io


app = Flask(__name__)


def fetch():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=options)
    link = "http://www.koeri.boun.edu.tr/scripts/lst5.asp"
    browser.get(link)
    raw_text = browser.find_element(By.TAG_NAME, "pre").text
    browser.close()
    return raw_text

'''
0         1         2         3        
012345678901234567890123456789012345678
2023.05.09 20:36:27  37.8108   36.2232 
'''
def parse(raw_text):
    data_buffer = io.StringIO(raw_text)
    widths = [(0, 10), (11, 19), (21, 28), 
              (31, 38), (43, 49), (59, 63), 
              (71, 120)]
    df = pd.read_fwf(data_buffer, colspecs=widths, 
                     skiprows=[i for i in range(6)], 
                     header=None)
    df.columns = ["Date", "Time", 
                  "Latitude", "Longitude", 
                  "Depth", "Magnitude", "Location"]
    return df


@app.route("/")
def main():
    raw_text = fetch()
    df = parse(raw_text)
    return render_template("index.html",
                            dates=df["Date"].tolist(),
                            times=df["Time"].tolist(),
                            latitudes=df["Latitude"].tolist(),
                            longitudes=df["Longitude"].tolist(),
                            depths=df["Depth"].tolist(),
                            magnitudes=df["Magnitude"].tolist(),
                            locations=df["Location"].tolist(),
                            content=df.to_html())


if __name__ == "__main__":
    app.run()
