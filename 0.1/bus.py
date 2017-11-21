import pandas as pd


###############################################################################
#FUNCTION: Bus_gen

#INPUT: a .csv file with a list of nodes

#OUTPUT: a dict of nodename -> index, number of nodes and a set of 3-phase bus

###############################################################################
def Bus_gen():
    data = pd.read_csv("data/ieee123_EXP_Y.csv", header=None)    
    # parse the data
    N_rows = len(data.index)
    
    # list of buses
    bus_dict = dict()
    busnames = set()
    idx = 1
    
    for i in range(N_rows):
        # add the current bus, execlue the slack bus
        bus_dict[data.iloc[i,0]] = idx
        idx += 1
        
        busnames.add(data.iloc[i,0][:-2])
    
    threePbus = set()
    for bus in busnames:
        phaseA = bus + '.' + str(1)
        phaseB = bus + '.' + str(2)  
        phaseC = bus + '.' + str(3)
        if phaseA in bus_dict and phaseB in bus_dict and phaseC in bus_dict:
            threePbus.add(bus)
    
    return (bus_dict, idx-1, threePbus)



