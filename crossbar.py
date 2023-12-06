import os
import regex as re
import pandas as pd
import numpy as np

# A virtual memristive crossbar with precision, memristor programming based on experimental data, and multiplication
# precision sets the number of bits the DAC would have
# shape is the shape of the crossbar
# max_attempts is the number of programming attemts
    # this is required because when a cell is programmed, a random sample from experimental data is chosen
    # this sample is chosen from a list of resistances collected from a specific voltage at the gate of a 1t1r
    # for more information see characterize_analog.ipynb
# threshold is the percentage from the median resistance a programming 
    # attempt must be within to return before max_attempts is reached
class Crossbar:
    def __init__(self, precision, shape, max_attempts, threshold):
        self.__precision = precision
        self.__shape = shape
        self.__n = shape[0]
        self.__m = shape[1]
        self.__max_attempts = max_attempts
        self.__threshold = threshold
        # integer value representation of the matrix (not used in multiplication)
        self.__values = np.random.randint(0, 2**self.__precision, self.__shape)
        self.__r_b_v = self.__make_r_b_v()
        self.__medians = np.median(self.__r_b_v, axis=1)
        self.__resistances, self.__errors = self.__program_array(self.__values, self.__precision, self.__max_attempts, self.__threshold)
        print(f'resistances:\n {self.__resistances}')
        print(f'values:\n {self.__values}')
        print(f'errors:\n {self.__errors}')
        print(f'average error:\n {np.mean(self.__errors)}')

    def __make_r_b_v(self):
        temps = []
        prog_data = []
        filenames = []
        for top, _, files in os.walk('.'):
            for f in files:
                res = re.findall(f'Prog' + r'.*_(\d+k)_', f)

                # we found a file starting with 'type'
                if len(res) > 0 and f[-4:] == '.xls':
                    temp = res[0][:-1]
                    temps.append(int(temp))

                    df = pd.read_excel(os.path.join(top, f), 'Sheet 1')
                    filenames.append(f)
                    d = {} 
                    for d_i, l in enumerate(list(df.columns)):
                        d[l] = df.to_numpy()[:,d_i]

                    prog_data.append(d)

        
        r_b_v = self.__get_y_by_voltage(prog_data[0],'LRS')
        for d in prog_data[1:]:
            r_b_v = np.append(r_b_v, self.__get_y_by_voltage(d, 'LRS'), axis=1)

        return r_b_v

    def __get_y_by_voltage(self, device, y): 
        y_by_voltage = []

        # for each voltage value
        for v_i in range(200):
            y_by_voltage.append([])

            # grab the LRS from each group
            for group_j in range(10):
                y_by_voltage[-1].append(device[y][v_i + group_j*200])
        
        return np.asarray(y_by_voltage)
    
    def __program_array(self, values, precision, max_attempts, threshold):
        resistances = np.zeros(self.__shape)
        errors = np.zeros(self.__shape)
        for (n_i, m_i), v in np.ndenumerate(values):
                v_idx = int(200 * (v / (2**precision)))
                resistances[n_i, m_i], errors[n_i, m_i] = self.__program_cell(v_idx, max_attempts, threshold)

        return resistances, errors
    
    def __program_cell(self, v_idx, max_attempts, threshold):
        resistance = 0
        error = 0
        attempt = 0
        while attempt < max_attempts:
            resistance = self.get_resistance(v_idx)
            max_target = self.__medians[v_idx] + self.__medians[v_idx] * threshold
            min_target = self.__medians[v_idx] - self.__medians[v_idx] * threshold
            error = 1 - np.abs(resistance/self.__medians[v_idx])
            if resistance < max_target and resistance > min_target:
                break

        return resistance, error

    def set_values(self, values):
        if np.max(values) > 2**self.__precision:
            print('Requested value to program exceeds maximum based on precision')
        else:
            self.__values = values
            self.__resistances, self.__errors = self.__program_array(self.__values, self.__precision)

    def set_value(self, value, n_i, m_i):
        if value > 2**self.__precision:
            print('Requested value to program exceeds maximum based on precision')
        else:
            v_idx = int(200 * (value / (2**self.__precision)))
            self.__resistances[n_i, m_i] = self.__program_cell(v_idx, self.__max_attempts, self.__threshold)

    def get_resistance(self, voltage_idx):
        return self.__r_b_v[voltage_idx][np.random.choice(len(self.__r_b_v[voltage_idx]))]
    
    def multiply(self, voltages):
        currents = []
        for col in range(self.__m):
            currents.append(np.sum(voltages/self.__resistances[:, col]))

        return currents

