import time
import os
import pandas as pd
import conf


def get_dates(periods=14):
    pattern="%Y-%m-%d"
    current_date = time.strftime(pattern)
    rng = pd.date_range(end=current_date, periods=periods, freq="D", normalize=True)
    index = 0
    for date_item in rng:
        file_path = get_date_path(date_item.strftime(pattern))
        if os.path.exists(file_path):
            break
        index = index + 1
    rng = rng[index:]
    return rng.to_series().apply(lambda x: x.strftime(pattern)).tolist()


def get_date_path(file_date):
    file_name = file_date + conf.DATA_SUFFIX
    return os.path.join(conf.DATA_PATH, file_name)

