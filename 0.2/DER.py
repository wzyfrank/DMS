import pandas as pd
import numpy as np

def readDER():
    DER_list = [] # a list of DER objects
    
    # column 1: Bus
    # column 2: production cost $/kWh
    # column 3: Phase
    # column 4: Phase A apparent power rating
    # column 5: Phase B apparent power rating
    # column 6: Phase C apparent power rating
    # column 7: power factor
    DER_data = pd.read_csv("data/DER data.csv", header=None)
    
    # iterate over table, extract DER attributes
    N_DER = len(DER_data.index)
    for i in range(N_DER):
        bus = str(DER_data.iloc[i,0])
        cost = float(DER_data.iloc[i,1])
        phase = str(DER_data.iloc[i,2])
        SA = float(DER_data.iloc[i,3])
        SB = float(DER_data.iloc[i,4])
        SC = float(DER_data.iloc[i,5])
        pf = float(DER_data.iloc[i,6])
        
        der = DER(bus, cost, phase, SA, SB, SC, pf) # create DER objects
        DER_list.append(der) # append DER object to the list
    return DER_list  


class DER:
    def __init__(self, bus, cost, phase, SA, SB, SC, pf):
        self.bus = bus
        self.cost = cost
        self.phase = phase
        
        self.PmaxA = SA * pf
        self.PmaxB = SB * pf
        self.PmaxC = SC * pf
        self.pf = pf
        self.QP_ratio = np.sqrt(1 - pf * pf) / pf

        # phase list 
        self.phase_list = []
        if 'A' in phase:
            self.phase_list.append(bus + '.1')
        if 'B' in phase:
            self.phase_list.append(bus + '.2')
        if 'C' in phase:
            self.phase_list.append(bus + '.3')
        
        
if __name__ == "__main__": 
    DER_list = readDER()
    for der in DER_list:
        print(der.phase)
        print(der.phase_list)