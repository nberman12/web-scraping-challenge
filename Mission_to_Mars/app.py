from flask import Flask, render_template, redirect
from flask_pymongo import pymongo
import scrape_mars

app = Flask(__name__)

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

mars_db=client.mars


@app.route("/")
def home():
    mars_data=mars_db.mars_data.find_one()
    

    return render_template("index.html", mars_data=mars_data)

@app.route("/scrape")
def scraper():

    mars_db.mars_data.drop()

    mars_data=scrape_mars.scrape()

    mars_db.mars_data.update({},mars_data,upsert=True)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)