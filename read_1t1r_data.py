import os
import regex as re
import pandas as pd

def read_1t1r_data(dir, type):
    temps = []
    data = []
    labels = []
    for top, _, files in os.walk(dir):
        for f in files:
            res = re.findall(f'{type}' + r'.*_(\d+k)_', f)

               # we found a file starting with 'type'
            if len(res) > 0 and f[-4:] == '.xls':
                data.append({})
                
                labels.append([])
                # print(vg)
                temp = res[0][:-1]
                temps.append(int(temp))
                try:
                    df = pd.read_excel(os.path.join(top, f), 'Sheet 1')

                    labels[-1] = df.columns
                    data[-1] = df.to_numpy()
                except:
                    print(f'Unable to read file: {os.path.join(top, f)}')
    return temps, data, labels 
