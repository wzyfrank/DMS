import pandas as pd
import Bus
import queue

def bus_trace(SourceBus):
    # to_bus -> downstream bus dict
    downstream_dict = dict()
        
    # iterate over lines
    line_data = pd.read_csv("data/line data.csv", header=None)
    N_lines = len(line_data.index)
    for l in range(N_lines):
        from_bus = str(line_data.iloc[l, 0])
        to_bus = str(line_data.iloc[l, 1])
        if from_bus in downstream_dict:
            downstream_dict[from_bus].append(to_bus)
        else:
            downstream_dict[from_bus] = [to_bus]
    
    
    # bus -> upstream buses dict
    upstream_dict = dict()
    upstream_dict[SourceBus] = []
    
    # trace down
    bus_queue = queue.Queue()
    bus_queue.put(SourceBus)    
    while not bus_queue.empty():
        cur_bus = bus_queue.get()
        up_list = upstream_dict[cur_bus][:]
        up_list.append(cur_bus)
        
        
        if cur_bus in downstream_dict:
            for d_bus in downstream_dict[cur_bus]:
                upstream_dict[d_bus] = up_list
                bus_queue.put(d_bus)
                
                
    return (downstream_dict, upstream_dict)


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


def v_DER_sensivity(der_list, f):
    # downstream and upstream dict
    (downstream_dict, upstream_dict) = bus_trace(SourceBus)
   
    # get bus_dict
    busnames = Bus.getBus()
    
    # impedance between bus and DER
    for bus in busnames:
        # check if any DER is downstream of the bus
        hasDER = False
        for der in der_list:
            if bus in upstream_dict[der]:
                hasDER = True
        
        # hasDER is true, the bus has downstream DER
        if hasDER:
            for der in der_list:
                if bus in upstream_dict[der]:
                    f.write('Z' + bus + der + ' = ')
                    length = len(upstream_dict[der])
                    for i in range(length-1):
                        bus_f = upstream_dict[der][i]
                        bus_t = upstream_dict[der][i+1]
                        f.write('Z' + bus_f + bus_t + ' + ')
                    f.write('0;\n')
    
    
if __name__ == "__main__": 
    SourceBus = '150'
    (downstream_dict, upstream_dict) = bus_trace(SourceBus)
    
    f = open('v_DER.m', 'w')
    der_list = ['83']
    v_DER_sensivity(der_list, f)
    f.close()