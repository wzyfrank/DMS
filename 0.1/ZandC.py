import bus
import linecode
import numpy as np
import pandas as pd
import scipy.io as sio


###############################################################################
#FUNCTION: ZC_line

#INPUT: bus_dict busname -> index
#       Vbase base voltage
#       threePbus set of three phase bus
#       Zbus impedance matrix
#       Cbus admittance matrix

#OUTPUT: Zbus (added line data)
#        Cbus (added line data)
###############################################################################
def ZC_line(bus_dict, Vbase, threePbus, Zbus, Cbus):
    # call linecode module to get the line code
    (Zarray, Carray, Z_dict, C_dict, Phase_dict) = linecode.get_linecode()
    
    # convert phase components to sequence components
    a = -0.5 + 1j * np.sqrt(3) / 2
    As = (1 / np.sqrt(3)) * np.array([[1, 1, 1],[1, a*a, a],[1, a, a*a]])
    As_inv = (1 / np.sqrt(3)) * np.array([[1, 1, 1],[1, a, a*a],[1, a*a, a]])  
    
    ## load the line data
    load_data = pd.read_csv("data/line data.csv", header=None)
    N_lines= len(load_data.index)
    
    
    for i in range(N_lines):
        from_bus = load_data.iloc[i,0]
        to_bus = load_data.iloc[i,1]
        # length in mile
        length = load_data.iloc[i,2] / 5280
        # config 
        config = load_data.iloc[i,3]
    
        # the Z and B matrix of line segment
        Z = np.zeros((3, 3), dtype = complex)
        C = np.zeros((3, 3), dtype = complex)
        
        # get the line segment impenance and admittance
        
        # config equal or greater than 100 indicates this is a transformer
        if config >= 100:
            continue
        
        # config smaller than 100, indicates this is a line segment
        else:
            Z = Z_dict[config] * length
            C = C_dict[config] * length
            # 3-phase line segment, change to sequential components
            if Phase_dict[config] == 3:
                Z = np.dot(np.dot(As_inv, Z), As)
                C = np.dot(np.dot(As_inv, C), As) 
                             
            # add this line to Zbus and Cbus matrix
            for f in range(3):
                for t in range(3):
                    from_phase = str(from_bus) + '.' + str(f+1)
                    to_phase = str(to_bus) + '.' + str(t+1)
                    from_t = str(from_bus) + '.' + str(t+1)
                    to_f = str(to_bus) + '.' + str(f+1)
                    if from_phase in bus_dict and to_phase in bus_dict:
                        # bus_dict is 1 based, python is 0 based 
                        Zbus[bus_dict[from_phase]-1, bus_dict[to_phase]-1] += Z[f,t]
                        Cbus[bus_dict[from_phase]-1, bus_dict[from_t]-1] += C[f,t] / 2
                        if to_f in bus_dict:
                            Cbus[bus_dict[to_f]-1, bus_dict[to_phase]-1] += C[f,t] / 2
    
    return (Zbus, Cbus)


###############################################################################
#FUNCTION: ZC_transformer

#INPUT: bus_dict busname -> index
#       Vbase base voltage
#       threePbus set of three phase bus
#       Zbus impedance matrix
#       Cbus admittance matrix

#OUTPUT: Zbus (added transformer data)
#        Cbus (added transformer data)
###############################################################################
def ZC_transformer(bus_dict, Vbase, threePbus, Zbus, Cbus):
    # call linecode module to get the line code
    (Z_dict, C_dict) = linecode.get_linecode()
    
    # convert phase components to sequence components
    a = -0.5 + 1j * np.sqrt(3) / 2
    As = (1 / np.sqrt(3)) * np.array([[1, 1, 1],[1, a*a, a],[1, a, a*a]])
    As_inv = (1 / np.sqrt(3)) * np.array([[1, 1, 1],[1, a, a*a],[1, a*a, a]])  
    ## load the transformer data
    load_data = pd.read_csv("data/line data.csv", header=None)
    N_lines= len(load_data.index)
    

    for i in range(N_lines):
        from_bus = load_data.iloc[i,0]
        to_bus = load_data.iloc[i,1]
        # config 
        config = load_data.iloc[i,3]
    
        # the Z and B matrix of line segment
        Z = np.zeros((3, 3), dtype = complex)
        C = np.zeros((3, 3), dtype = complex)    
        
        # NOTE: no substation Xfmr
        if config == 1002:
            # distribution transformer S base is 500kVA
            # delta-delta connection
            Sbase = 150000
            Zbase = Vbase * Vbase / Sbase
            Z = Zbase * np.diagflat([0.0127 + 0.0272j, 0.0127 + 0.0272j, 0.0127 + 0.0272j]) 
            # change to sequential components
            Z = np.dot(np.dot(As_inv, Z), As)
            C = np.dot(np.dot(As_inv, C), As) 
        elif config == 1003:
            # voltage regulator, S base is 5000kVA
            # single phase
            Sbase = 5000000
            Zbase = Vbase * Vbase / Sbase
            Z = Zbase * np.diagflat([0.000001+0.0001j, 0.000001+0.0001j, 0.000001+0.0001j])
            # change to sequential components
            Z = np.dot(np.dot(As_inv, Z), As)
            C = np.dot(np.dot(As_inv, C), As) 
        elif config == 1004:
            # voltage regulator, S base is 2000kVA
            # single phase
            Sbase = 2000000
            Zbase = Vbase * Vbase / Sbase
            Z = Zbase * np.diagflat([0.000001+0.0001j, 0.000001+0.0001j, 0.000001+0.0001j])   
            # change to sequential components
            Z = np.dot(np.dot(As_inv, Z), As)
            C = np.dot(np.dot(As_inv, C), As) 
        elif config == 1005:
            # voltage regulator, S base is 2000kVA
            # single phase
            Sbase = 2000000
            Zbase = Vbase * Vbase / Sbase
            Z = Zbase * np.diagflat([0.000001+0.0001j, 0.0000+0.0000j, 0.000001+0.0001j])        
        elif config == 1006:
            # voltage regulator, S base is 2000kVA
            # single phase
            Sbase = 2000000
            Zbase = Vbase * Vbase / Sbase
            Z = Zbase * np.diagflat([0.000001+0.0001j, 0.0000+0.0000j, 0.0000+0.0000j])            
    
    # add this line to Zbus and Cbus matrix
    for f in range(3):
        for t in range(3):
            from_phase = str(from_bus) + '.' + str(f+1)
            to_phase = str(to_bus) + '.' + str(t+1)
            from_t = str(from_bus) + '.' + str(t+1)
            to_f = str(to_bus) + '.' + str(f+1)
            if from_phase in bus_dict and to_phase in bus_dict:
                # bus_dict is 1 based, python is 0 based 
                Zbus[bus_dict[from_phase]-1, bus_dict[to_phase]-1] += Z[f,t]
                Cbus[bus_dict[from_phase]-1, bus_dict[from_t]-1] += C[f,t] / 2
                if to_f in bus_dict:
                    Cbus[bus_dict[to_f]-1, bus_dict[to_phase]-1] += C[f,t] / 2      

    return (Zbus, Cbus)


###############################################################################
#FUNCTION: ZC_capacitor

#INPUT: bus_dict busname -> index
#       Vbase base voltage
#       threePbus set of three phase bus
#       Zbus impedance matrix
#       Cbus admittance matrix

#OUTPUT: Zbus (added line data)
#        Cbus (added line data)
###############################################################################
def ZC_capacitor(bus_dict, Vbase, threePbus, Zbus, Cbus):
    # convert to sequence components
    a = -0.5 + 1j * np.sqrt(3) / 2
    As = (1 / np.sqrt(3)) * np.array([[1, 1, 1],[1, a*a, a],[1, a, a*a]])
    As_inv = (1 / np.sqrt(3)) * np.array([[1, 1, 1],[1, a, a*a],[1, a*a, a]])  
    
    ## Cbus matrix, primarily for capacitors
    cap_data = pd.read_csv("data/cap data.csv", sep = ',', header=None)
    N_caps= len(cap_data.index)
    for i in range(N_caps):
        cap_bus = str(cap_data.iloc[i,0])
        # three phase bus
        if cap_bus in threePbus:
            cap_C = np.zeros((3, 3), dtype = complex)
            for ph in range(3):
                cap_C[ph, ph] = 1j * (cap_data.iloc[i,ph+1] * 1000) / (Vbase * Vbase / 3)
        
            # change to sequential components
            cap_C = np.dot(np.dot(As_inv, cap_C), As) 
            for ph in range(3):
                cap_phase = str(cap_bus) + '.' + str(ph+1)
                if cap_phase in bus_dict:
                    # rating is in kVar, Vbase is LL voltage, change to imag
                    Cbus[bus_dict[cap_phase]-1, bus_dict[cap_phase]-1] += cap_C[ph, ph]
        
        #single and two phase bus
        else:
            for ph in range(3):
                cap_phase = str(cap_bus) + '.' + str(ph+1)
                if cap_phase in bus_dict:
                    # rating is in kVar, Vbase is LL voltage, change to imag
                    Cbus[bus_dict[cap_phase]-1, bus_dict[cap_phase]-1] += 1j * (cap_data.iloc[i,ph+1] * 1000) / (Vbase * Vbase / 3)    
    
    return (Zbus, Cbus)


###############################################################################
#FUNCTION: gen_ZC

#INPUT: Vbase base voltage


#OUTPUT: Zbus (added line data)
#        Cbus (added line data)
###############################################################################    
def gen_ZC(Vbase):
    # call bus_gen function
    # get the bus dict , N_bus and 3-phase bus
    (bus_dict, N_bus, threePbus) = bus.Bus_gen()
    
    ## init the Zbus and Cbus matrix
    Zbus = np.zeros((N_bus, N_bus), dtype = complex)
    Cbus = np.zeros((N_bus, N_bus), dtype = complex)
    
    # add line data to Zbus and Cbus
    (Zbus, Cbus) = ZC_line(bus_dict, Vbase, threePbus, Zbus, Cbus)
    # add transformer data to Zbus and Cbus
    (Zbus, Cbus) = ZC_transformer(bus_dict, Vbase, threePbus, Zbus, Cbus)
    # add capacitor data to Zbus and Cbus    
    (Zbus, Cbus) = ZC_capacitor(bus_dict, Vbase, threePbus, Zbus, Cbus)

    
    sio.savemat('data/Zbus.mat', {"Zbus":Zbus})  
    sio.savemat('data/Cbus.mat', {"Cbus":Cbus})
    return(Zbus, Cbus)


if __name__ == "__main__":
    # The Voltage base
    Vbase = 4160 # V
    gen_ZC(Vbase)
    
