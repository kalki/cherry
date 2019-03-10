import json
import os
import pandas as pd
import numpy as np
import conf
import bloom_date_file as bdf

def get_site_full_header():
    existing_dates = []
    available_dates = bdf.get_dates()
    for date_item in available_dates:
        file_path = bdf.get_date_path(date_item)
        if os.path.exists(file_path):
            existing_dates.insert(0,date_item)

    coldef = pd.read_csv(conf.DEF_COLUMNS)
    coldef = coldef[coldef.used_in_full]
    coldef = coldef.loc[:,["name","title", "visible", "searchable", "orderable"]]
    
    datedef = pd.DataFrame(existing_dates, columns=["name"])
    datedef["title"] = datedef["name"].apply(lambda x:x[6:])
    datedef["visible"] = True
    datedef["searchable"] = False
    datedef["orderable"] = False

    coldef = pd.concat([coldef, datedef])

    return coldef.to_dict(orient="records")

def get_site_full_banned():
    coldef = pd.read_csv(conf.DEF_COLUMNS)
    coldef = coldef[~coldef.used_in_full]
    return coldef["name"].values.tolist()

