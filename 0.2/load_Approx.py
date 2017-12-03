import pandas as pd
import numpy as np
import scipy.io as sio
import Bus

def loadApproximate():
    # Voltage base
    Vbase = 4160 / np.sqrt(3)
    
    # get bus dict
    (bus_dict, Nbus, threePbus) = Bus.Bus_gen()
    
    # init the constant Z loads
    Yloads = np.zeros((Nbus, Nbus), dtype = complex)
    
    # init the constant PQ loads
    PQloads = np.zeros((Nbus), dtype = complex)
    
    # read load data from file
    loads = pd.read_csv('data/loads data.csv')
    N_loads = len(loads.index)
    
    # delta to wye 
    alpha = np.cos(np.pi / 6) + 1j * np.sin(np.pi / 6)
    beta = np.cos(-np.pi / 6) + 1j * np.sin(-np.pi / 6)
    M = np.array([[beta, 0, alpha], [alpha, beta, 0], [0, alpha, beta]]) / np.sqrt(3)
    
    
    # iterate over loads
    for i in range(N_loads):
        bus = str(loads.iloc[i,0])
        load_type = str(loads.iloc[i,1])
        
        # three phase load in W (convert from kW)
        load_A = 1000 * (float(loads.iloc[i,2]) + 1j * float(loads.iloc[i,3]))
        load_B = 1000 * (float(loads.iloc[i,4]) + 1j * float(loads.iloc[i,5]))
        load_C = 1000 * (float(loads.iloc[i,6]) + 1j * float(loads.iloc[i,7]))
        
        # three phase node
        node_A = bus + '.1'
        node_B = bus + '.2'
        node_C = bus + '.3'
        
        # Wye connection
        # constant PQ
        if load_type == 'Y-PQ':
            if node_A in bus_dict:
                PQloads[bus_dict[node_A]-1] = load_A
            if node_B in bus_dict:
                PQloads[bus_dict[node_B]-1] = load_B
            if node_C in bus_dict:
                PQloads[bus_dict[node_C]-1] = load_C
            
        # constant I
        elif load_type == 'Y-I':
            # split half to PQ and other half to Z
            if node_A in bus_dict:
                PQloads[bus_dict[node_A]-1] = load_A / 2
            if node_B in bus_dict:
                PQloads[bus_dict[node_B]-1] = load_B / 2
            if node_C in bus_dict:
                PQloads[bus_dict[node_C]-1] = load_C / 2
                
            Y_A = load_A / (Vbase * Vbase * 2)
            Y_B = load_B / (Vbase * Vbase * 2)
            Y_C = load_C / (Vbase * Vbase * 2)
            if node_A in bus_dict:
                Yloads[bus_dict[node_A]-1, bus_dict[node_A]-1] = Y_A
            if node_B in bus_dict:
                Yloads[bus_dict[node_B]-1, bus_dict[node_B]-1] = Y_B
            if node_C in bus_dict:
                Yloads[bus_dict[node_C]-1, bus_dict[node_C]-1] = Y_C        
                
        # constant Z
        elif load_type == 'Y-Z': 
            Y_A = load_A / (Vbase * Vbase)
            Y_B = load_B / (Vbase * Vbase)
            Y_C = load_C / (Vbase * Vbase)
            if node_A in bus_dict:
                Yloads[bus_dict[node_A]-1, bus_dict[node_A]-1] = Y_A
            if node_B in bus_dict:
                Yloads[bus_dict[node_B]-1, bus_dict[node_B]-1] = Y_B
            if node_C in bus_dict:
                Yloads[bus_dict[node_C]-1, bus_dict[node_C]-1] = Y_C
        
        # Delta connection
        else:
            delta_load = np.array([load_A, load_B, load_C])
            delta_load = np.dot(M, delta_load)
            
            # constant PQ
            if load_type == 'D-PQ':
                if node_A in bus_dict:
                    PQloads[bus_dict[node_A]-1] = delta_load[0]
                if node_B in bus_dict:
                    PQloads[bus_dict[node_B]-1] = delta_load[1]
                if node_C in bus_dict:
                    PQloads[bus_dict[node_C]-1] = delta_load[2]   
            
            # constant Z
            elif load_type == 'D-Z': 
                Y_A = delta_load[0] / (Vbase * Vbase)
                Y_B = delta_load[1] / (Vbase * Vbase)
                Y_C = delta_load[2] / (Vbase * Vbase)
                if node_A in bus_dict:
                    Yloads[bus_dict[node_A]-1, bus_dict[node_A]-1] = Y_A
                if node_B in bus_dict:
                    Yloads[bus_dict[node_B]-1, bus_dict[node_B]-1] = Y_B
                if node_C in bus_dict:
                    Yloads[bus_dict[node_C]-1, bus_dict[node_C]-1] = Y_C 
            
            # constant I
            elif load_type == 'D-I':
                # split half to PQ and other half to Z
                if node_A in bus_dict:
                    PQloads[bus_dict[node_A]-1] = delta_load[0] / 2
                if node_B in bus_dict:
                    PQloads[bus_dict[node_B]-1] = delta_load[1] / 2
                if node_C in bus_dict:
                    PQloads[bus_dict[node_C]-1] = delta_load[2] / 2
                    
                Y_A = delta_load[0] / (Vbase * Vbase * 2)
                Y_B = delta_load[1] / (Vbase * Vbase * 2)
                Y_C = delta_load[2] / (Vbase * Vbase * 2)
                if node_A in bus_dict:
                    Yloads[bus_dict[node_A]-1, bus_dict[node_A]-1] = Y_A
                if node_B in bus_dict:
                    Yloads[bus_dict[node_B]-1, bus_dict[node_B]-1] = Y_B
                if node_C in bus_dict:
                    Yloads[bus_dict[node_C]-1, bus_dict[node_C]-1] = Y_C 
                    
    sio.savemat('data/Yloads.mat', {"Yloads":Yloads})  
    sio.savemat('data/PQloads.mat', {"PQloads":PQloads})


if __name__ == "__main__": 
    loadApproximate()