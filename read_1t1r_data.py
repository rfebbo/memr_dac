import os
import regex as re
import pandas as pd

def read_1t1r_data(dir, type):
    temps = []
    data = []
    for top, _, files in os.walk(dir):
        for f in files:
            res = re.findall(f'{type}' + r'.*_(\d+k)_', f)

            # we found a file starting with 'type'
            if len(res) > 0 and f[-4:] == '.xls':
                temp = res[0][:-1]
                temps.append(int(temp))

                df = pd.read_excel(os.path.join(top, f), 'Sheet 1')

                d = {} 
                for d_i, l in enumerate(list(df.columns)):
                    d[l] = df.to_numpy()[:,d_i]

                data.append(d)

    return temps, data 
