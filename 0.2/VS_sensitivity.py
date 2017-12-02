import pandas as pd
import Bus


def bus_trace():
    # bus -> downstream bus dict
    bus_trace_dict = dict()
    
    # iterate over lines
    line_data = pd.read_csv("data/line data.csv", header=None)
    N_lines = len(line_data.index)
    for l in range(N_lines):
        from_bus = str(line_data.iloc[l, 0])
        to_bus = str(line_data.iloc[l, 1])
        bus_trace_dict[to_bus] = from_bus
    
    return bus_trace_dict


def bus_phase(SourceBus):
    # get bus_dict from external 
    (bus_dict, N_bus, threePbus) = Bus.Bus_gen()
    
    bus_phase_dict = dict()
    bus_phase_dict[SourceBus] = [1,2,3]
    
    # iterate over lines
    line_data = pd.read_csv("data/line data.csv", header=None)
    N_lines = len(line_data.index)  
    
    for l in range(N_lines):
        to_bus = str(line_data.iloc[l, 1])
        phase = []
    
        to_PhaseA = str(to_bus) + '.1'
        to_PhaseB = str(to_bus) + '.2'
        to_PhaseC = str(to_bus) + '.3'
        
        # init the no. of phases
        phase = []
        
        if to_PhaseA in bus_dict:
            phase.append(1)
        if to_PhaseB in bus_dict:
            phase.append(2)
        if to_PhaseC in bus_dict:
            phase.append(3)
        
        bus_phase_dict[to_bus] = phase
    
    return bus_phase_dict

'''
def v_DER_sensivity(der_bus, f):
''' 
    
    
if __name__ == "__main__": 
    SourceBus = '150'
    bus_phase_dict = bus_phase(SourceBus)
    
    fd = open('v_DER.m', 'w')
    der_bus = '83'
    