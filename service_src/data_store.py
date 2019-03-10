import os
import pandas as pd
import bloom_date_file as bdf
import column_definition as cd
import conf

def get_site_full():
    available_dates = bdf.get_dates()
    available_dates.reverse()

    sites = pd.read_csv(os.path.join(conf.DATA_PATH, "sites.csv"))
    sites.set_index("site_url", drop=False, inplace=True)

    transit = pd.read_csv(os.path.join(conf.DATA_PATH, "transit.csv"))
    transit.set_index("site_url", inplace=True)
    sites = sites.merge(transit, left_index=True, right_index=True)

    for date_item in available_dates:
        file_path = bdf.get_date_path(date_item)
        if os.path.exists(file_path):
            status_data = pd.read_csv(bdf.get_date_path(date_item))
            status_data.set_index("site_url", inplace=True)
            status_data.rename(columns={"status": date_item}, inplace=True)
            sites = sites.merge(status_data, left_index=True, right_index=True)

    sites.drop(columns=cd.get_site_full_banned(), inplace=True)
    sites.sort_index(inplace=True)
    sites.fillna("", inplace=True)

    return sites.values.tolist()

