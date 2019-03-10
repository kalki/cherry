import csv
import json
from flask import Flask
from flask import jsonify
import data_store as ds
import column_definition as cd

app = Flask(__name__)

@app.route("/", methods=["GET"])
def hello():
    return "Cherry Service OK"

@app.route("/data/sites/full", methods=["GET"])
def get_sites_full():
    data = {"data": ds.get_site_full()}
    return jsonify(data)

@app.route("/header/sites/full", methods=["GET"])
def get_sites_full_header():
    col_dict_list = cd.get_site_full_header()

    return jsonify(col_dict_list)

if __name__ == "__main__":
    app.run()
