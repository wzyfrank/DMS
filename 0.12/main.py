import pandas as pd
import queue
import Bus
import ZandC
import DER

# forget about the per unit system 
# use real value
class OPF:
    ###########################################################################
    #FUNCTION: init, the constructor
    # Vbase base voltage level
    # SourceBus the slack bus
    #INPUT: None

    #OUTPUT: None
    ###########################################################################
    def __init__(self, Vbase, SourceBus, reg_bus, reg_phase):
        # The Voltage base
        self.Vbase = Vbase # V
        self.SourceBus = SourceBus
        # Voltage regulator nodes
        self.reg_bus = reg_bus
        self.reg_Phase = reg_phase 
        
        # (1) get the bus dict 
        (self.bus_dict, self.N_bus, self.threePbus) = Bus.Bus_gen()
        
        # (2) get the Z and C bus
        (self.Zbus, self.Cbus) = ZandC.gen_ZC(self.Vbase)
    
        # (3) the bus -> phase dict
        self.bus_phase_dict = dict()
        self.bus_phase_dict[SourceBus] = [1,2,3]
        
        # (4) the bus -> downstream bus dictionary
        self.downstream_dict = dict()
        
        # (5) transistion bus, having both abc and 012 variables
        self.transistion_bus = set()
    
        # (6) line data, read from file
        self.line_data = pd.read_csv("data/line data.csv", header=None)
        self.N_lines = len(self.line_data.index)
    
    
        # open the file
        self.fd = open('ieee123.m', 'w')
        # first line, MATLAB function declare
        self.fd.write('clear;\n')
        self.fd.write('clc;\n')
        self.fd.write('close all;\n')
        self.fd.write('\n')
        
        
    ###########################################################################
    #FUNCTION: load data
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################
    def loadData(self):
        self.fd.write("Zbus = load('Zbus.mat');\n")
        self.fd.write("Zbus = Zbus.Zbus;\n")
        self.fd.write("Cbus = load('Cbus.mat');\n")
        self.fd.write("Cbus = Cbus.Cbus;\n")
        self.fd.write("loads = load('PQloads.mat');\n")
        self.fd.write("loads = loads.PQloads;\n")
        self.fd.write("Yloads = load('Yloads.mat');\n")
        self.fd.write("Yloads = Yloads.Yloads;\n")        
        self.fd.write('\n')
        
        
    ###########################################################################
    #FUNCTION: VoltageRegulatorTaps, set the voltage regulator taps
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################    
    def VoltageRegulatorTaps(self):
        self.fd.write('\n')
        self.fd.write('% voltage regulator taps \n')
        ## voltage regulator parameters
        for i in range(len(self.reg_bus)):
            reg = self.reg_bus[i]
            ph = self.reg_Phase[i]
            # ABC
            if ph == 'ABC':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapB' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapC' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = [tapA' + reg + '; tapB' + reg + '; tapC' + reg + '];\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")
            # AB
            elif ph == 'AB':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapB' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = [tapA' + reg + '; tapB' + reg + '];\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")
            # AC
            elif ph == 'BC':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapB' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapC' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = [tapB' + reg + '; tapC' + reg + '];\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")
            # AC
            elif ph == 'AC':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapC' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = [tapA' + reg + '; tapC' + reg + '];\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")            
            # A
            elif ph == 'A':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = tapA' + reg + ';\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")  
            # B
            elif ph == 'B':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapB' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = tapB' + reg + ';\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")  
            # C
            elif ph == 'C':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapC' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = tapC' + reg + ';\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")  
        self.fd.write('\n')
    

    ###########################################################################
    #FUNCTION: Zimpedances, extract line segment Z matrix from Zbus 
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################    
    def Zimpedances(self):
        self.fd.write('\n')
        self.fd.write('% Z impedances \n')

        # iterate over lines
        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])
            if from_bus in self.downstream_dict:
                self.downstream_dict[from_bus].append(to_bus)
            else:
                self.downstream_dict[from_bus] = [to_bus]
            
            to_PhaseA = str(to_bus) + '.1'
            to_PhaseB = str(to_bus) + '.2'
            to_PhaseC = str(to_bus) + '.3'
            from_PhaseA = str(from_bus) + '.1'
            from_PhaseB = str(from_bus) + '.2'
            from_PhaseC = str(from_bus) + '.3'
            to_idx = []
            from_idx = []
            
            # init the no. of phases
            phase = []
            
            if to_PhaseA in self.bus_dict:
                to_idx.append(self.bus_dict[to_PhaseA])
                from_idx.append(self.bus_dict[from_PhaseA])
                phase.append(1)
            if to_PhaseB in self.bus_dict:
                to_idx.append(self.bus_dict[to_PhaseB])
                from_idx.append(self.bus_dict[from_PhaseB])
                phase.append(2)
            if to_PhaseC in self.bus_dict:
                to_idx.append(self.bus_dict[to_PhaseC])
                from_idx.append(self.bus_dict[from_PhaseC])
                phase.append(3)
            
            self.bus_phase_dict[to_bus] = phase
                          
            # write the Z impedance to file
            self.fd.write('Z' + str(from_bus) + str(to_bus) + ' = Zbus(' + str(from_idx) + ',' + str(to_idx) + ');\n')
    

    ###########################################################################
    # FUNCTION: basicParameters, basic parameters for the model
    # Voltage profile, sequential component parameters
    
    #INPUT: Vsub voltage at substation
    #       Vlb : voltage lower bound
    #       Vub : voltage upper bound
    #OUTPUT: None
    ########################################################################### 
    def basicParameters(self, Vsub, Vlb, Vub):
        self.fd.write('\n')
        self.fd.write('\n')
        # slack bus voltage
        self.fd.write('% three phase voltage at slack bus\n')
        self.fd.write('Vbase = ' + str(self.Vbase) + ' / sqrt(3);\n')
        self.fd.write("v0 =" + str(Vsub) + " * Vbase * [1; cosd(-120) + 1j * sind(-120); cosd(120) + 1j * sind(120)];\n")
        # voltage lower and upper bounds
        self.fd.write('% voltage upper and lower bounds\n')
        self.fd.write('V_lb = ' + str(Vlb) + ' * Vbase;\n')
        self.fd.write('V_ub = ' + str(Vub) + ' * Vbase;\n')
        self.fd.write('v_lb = V_lb * V_lb;\n')
        self.fd.write('v_ub = V_ub * V_ub;\n')
        self.fd.write('\n')
        

    ###########################################################################
    #FUNCTION: createVariables, create CVX variables (V, I, S), DER variables
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################        
    def createVariables(self, der_list):
        self.fd.write('\n')
        self.fd.write('\n')
        self.fd.write('cvx_begin sdp quiet\n')
        self.fd.write('% the solver: \n')
        self.fd.write('cvx_solver SeDuMi;\n')
        
        # (1) voltage square variables
        self.fd.write('\n')
        self.fd.write('% voltage square variables\n')
        

        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])
            ph = len(self.bus_phase_dict[to_bus])
            self.fd.write('variable v' + to_bus + '(' + str(ph) + ',' + str(ph) + ') hermitian\n')
            
        # slack bus variable        
        self.fd.write('variable v150(3,3) hermitian\n')    
        
        # (2) complex power variables
        self.fd.write('\n')
        self.fd.write('% complex power variables\n')
        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])
            ph = len(self.bus_phase_dict[to_bus])
            self.fd.write('variable S' + str(from_bus) + str(to_bus) + '(' + str(ph) + ',' + str(ph) + ') complex\n')
        
        # (3) current square variables
        self.fd.write('\n')
        self.fd.write('% current square variables\n')   
        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])
            ph = len(self.bus_phase_dict[to_bus])
            self.fd.write('variable l' + str(from_bus) + str(to_bus) + '(' + str(ph) + ',' + str(ph) + ') hermitian\n')
             
        # (4) DER variables
        self.fd.write('\n')
        self.fd.write('% DER variables\n')
        for der in der_list:
            self.fd.write('variable DER' + der.bus + '(3, 1) complex\n')
            
        
    ###########################################################################
    #FUNCTION: ObjectiveFunction, create the objective function
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################    
    def ObjectiveFunction(self, der_list):
        self.fd.write('\n')   
        self.fd.write('\n')   
        
        '''
        # minimize losses
        self.fd.write('minimize(')
        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])        
            Z_cur = 'Z' + from_bus + to_bus
            l_cur = 'l' + from_bus + to_bus

            self.fd.write('trace(real('+ Z_cur + '*' + l_cur + ')) + ')

        self.fd.write('0)\n')
        '''
        
        # minimize production cost
        self.fd.write('minimize(')
        self.fd.write('trace(real(S150R149)) +')
        for der in der_list:
            self.fd.write(str(der.cost) + ' * sum(real(DER' + der.bus + ')) + ')
            
        self.fd.write('0)\n')
        self.fd.write('subject to\n')  
    

    ###########################################################################
    #FUNCTION: Constraints, create model constraints
    # (1) voltage upper and lower bounds
    # (2) voltage across a line 
    # (3) semidefinite contraints
    # (4) power flow balance
    # (5) DER power constriants
    #INPUT: list of DERs

    #OUTPUT: None
    ###########################################################################    
    def Constraints(self, der_list):
        # build a dict of DER BUS -> DER
        der_dict = dict()
        for der in der_list:
            der_dict[der.bus] = der
        
        
        # (1) voltage upper and lower bounds
        self.fd.write('\n')
        self.fd.write('\n')
        self.fd.write('% constraints: \n')
        self.fd.write('% (1): voltage lower and upper bounds \n')
        for l in range(self.N_lines):
            to_bus = str(self.line_data.iloc[l, 1])
            self.fd.write('v_lb <= diag(v' + to_bus + ') <= v_ub;\n')
                
        self.fd.write('v150 == v0 * ctranspose(v0);\n' )  
        
        # (2) voltage across a line 
        # (3) semidefinite contraints
        # (4) power flow balance
        self.fd.write('\n')
        self.fd.write('% (1): voltage across a line \n')
        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])
            
            # power transfer along a line
            S_cur = 'S' + from_bus + to_bus
            # line impedance
            Z_cur = 'Z' + from_bus + to_bus
            # square of current
            l_cur = 'l' + from_bus + to_bus
            
            # the line is a voltage regulator
            if to_bus in self.reg_bus:
                # voltage regulator case 
                phase_from = self.bus_phase_dict[from_bus]
                phase_to = self.bus_phase_dict[to_bus]
                idx_list = [idx+1 for idx, val in enumerate(phase_from) if val in phase_to]

                # (2) voltage across a line
                self.fd.write('v' + to_bus + ' == (v' + from_bus + '(' + str(idx_list) + ',' + str(idx_list) + ') - ' + S_cur + '*ctranspose(' + Z_cur + ') - ' + Z_cur + '*ctranspose(' + S_cur + ') + ' + Z_cur + '*' + l_cur + '*ctranspose(' + Z_cur + ')) .* alphaM' + to_bus + ';\n') 
            
                # (3) semidefinite constraint
                self.fd.write('[v' + from_bus + '(' + str(idx_list) + ',' + str(idx_list) + '), ' + S_cur + '; ctranspose(' + S_cur + '), ' + l_cur + '] >= 0;\n')
                       
            # from bus phase = to bus phase
            elif len(self.bus_phase_dict[from_bus]) == len(self.bus_phase_dict[to_bus]):
                # voltage across a line
                self.fd.write('v' + to_bus + ' == v' + from_bus + ' - ' + S_cur + '*ctranspose(' + Z_cur + ') - ' + Z_cur + '*ctranspose(' + S_cur + ') + ' + Z_cur + '*' + l_cur + '*ctranspose(' + Z_cur + ');\n')
                # semidefinite constraint
                self.fd.write('[v' + from_bus + ', ' + S_cur + '; ctranspose(' + S_cur + '), ' + l_cur + '] >= 0;\n')        
            
            # from bus phase != to bus phase
            else:
                phase_from = self.bus_phase_dict[from_bus]
                phase_to = self.bus_phase_dict[to_bus]
                idx_list = [idx+1 for idx, val in enumerate(phase_from) if val in phase_to]

                # voltage across a line
                self.fd.write('v' + to_bus + ' == v' + from_bus + '(' + str(idx_list) + ',' + str(idx_list) + ') - ' + S_cur + '*ctranspose(' + Z_cur + ') - ' + Z_cur + '*ctranspose(' + S_cur + ') + ' + Z_cur + '*' + l_cur + '*ctranspose(' + Z_cur + ');\n')
                # semidefinite constraint
                self.fd.write('[v' + from_bus + '(' + str(idx_list) + ',' + str(idx_list) + '), ' + S_cur + '; ctranspose(' + S_cur + '), ' + l_cur + '] >= 0;\n')
     
            # (4) power flow balance
            to_PhaseA = str(to_bus) + '.1'
            to_PhaseB = str(to_bus) + '.2'
            to_PhaseC = str(to_bus) + '.3'
            
            # the load at node
            load_idx = []
            if to_PhaseA in self.bus_dict:
                load_idx.append(self.bus_dict[to_PhaseA])
            if to_PhaseB in self.bus_dict:
                load_idx.append(self.bus_dict[to_PhaseB])
            if to_PhaseC in self.bus_dict:
                load_idx.append(self.bus_dict[to_PhaseC])
            
            # a. upstream line
            self.fd.write('diag(' + S_cur + '-' + Z_cur + '*' + l_cur + ')') 
            
            # b. load 
            # constant PQ load
            self.fd.write('- loads(' + str(load_idx) + ')')
            # constant Z load
            self.fd.write(' - diag(v' + to_bus + ' * Yloads(' + str(load_idx) + ',' + str(load_idx) + ')) ') 
            
            # c. DER, check if this bus has DER
            if to_bus in der_dict.keys():
                # get current der
                der = der_dict[to_bus]
                
                # check phasing 
                der_phase_idx = []
                if to_PhaseA in der.phase_list:
                    der_phase_idx.append(1)
                if to_PhaseB in der.phase_list:
                    der_phase_idx.append(2)
                if to_PhaseC in der.phase_list:
                    der_phase_idx.append(3)
                
                # write DER
                self.fd.write('+ DER' + der.bus + '('+ str(der_phase_idx) + ')')
                
            # d. shunt capacitance
            self.fd.write(' + diag(v' + to_bus + ' * Cbus(' + str(load_idx) + ',' + str(load_idx) + ')) == ') 
                
            # e. downstream flows
            if to_bus in self.downstream_dict:
                for d_bus in self.downstream_dict[to_bus]:
                    # equal phase config
                    if len(self.bus_phase_dict[to_bus]) == len(self.bus_phase_dict[d_bus]):
                        self.fd.write('diag(S' + to_bus + d_bus + ') + ')  
                    else:
                        # to_bus ABC
                        if self.bus_phase_dict[to_bus] == [1,2,3]:
                            if self.bus_phase_dict[d_bus] == [1,2]:
                                self.fd.write('[diag(S' + to_bus + d_bus + '); 0] + ')
                            elif self.bus_phase_dict[d_bus] == [2,3]:
                                self.fd.write('[0; diag(S' + to_bus + d_bus + ')] + ')
                            elif self.bus_phase_dict[d_bus] == [1,3]:
                                self.fd.write('[S' + to_bus + d_bus + '(1,1); 0; S' + to_bus + d_bus + '(2,2) ] + ')
                            elif self.bus_phase_dict[d_bus] == [1]:
                                self.fd.write('[diag(S' + to_bus + d_bus + '); 0; 0] + ')
                            elif self.bus_phase_dict[d_bus] == [2]:
                                self.fd.write('[0; diag(S' + to_bus + d_bus + '); 0] + ')
                            elif self.bus_phase_dict[d_bus] == [3]:    
                                self.fd.write('[0; 0; diag(S' + to_bus + d_bus + ')] + ')
                        # to_bus AB
                        elif self.bus_phase_dict[to_bus] == [1,2]:   
                            if self.bus_phase_dict[d_bus] == [1]:
                                self.fd.write('[diag(S' + to_bus + d_bus + '); 0] + ')
                            else:
                                self.fd.write('[0; diag(S' + to_bus + d_bus + ')] + ')
                        # to_bus BC        
                        elif self.bus_phase_dict[to_bus] == [2,3]:
                            if self.bus_phase_dict[d_bus] == [2]:
                                self.fd.write('[diag(S' + to_bus + d_bus + '); 0] + ')
                            else:
                                self.fd.write('[0; diag(S' + to_bus + d_bus + ')] + ')                        
                        # to_bus AC
                        elif self.bus_phase_dict[to_bus] == [1,3]:    
                            if self.bus_phase_dict[d_bus] == [1]:
                                self.fd.write('[diag(S' + to_bus + d_bus + '); 0] + ')
                            else:
                                self.fd.write('[0; diag(S' + to_bus + d_bus + ')] + ')
                                
            # the last zero may seem redundant
            self.fd.write('0;\n')
            self.fd.write('\n')
        
        # (5) DER power constriants
        # convert rating from kW to W
        self.fd.write('\n')
        self.fd.write('% (5): DER power constriants \n')
        for der in der_list:
            self.fd.write('0 <= real(DER' + der.bus + '(1)) <= ' + str(der.PmaxA * 1000) + ';\n')
            self.fd.write('0 <= real(DER' + der.bus + '(2)) <= ' + str(der.PmaxB * 1000) + ';\n')
            self.fd.write('0 <= real(DER' + der.bus + '(3)) <= ' + str(der.PmaxC * 1000) + ';\n')
            self.fd.write('imag(DER' + der.bus + '(1)) == real(DER' + der.bus + '(1)) * ' + str(der.QP_ratio) + ';\n')
            self.fd.write('imag(DER' + der.bus + '(2)) == real(DER' + der.bus + '(2)) * ' + str(der.QP_ratio) + ';\n')
            self.fd.write('imag(DER' + der.bus + '(3)) == real(DER' + der.bus + '(3)) * ' + str(der.QP_ratio) + ';\n')       
            self.fd.write('\n')
            
            
        # close the cvx
        self.fd.write('\n')
        self.fd.write('\n')
        self.fd.write('cvx_end\n')
        self.fd.write('\n')
        self.fd.write('\n')        
        

    ###########################################################################
    #FUNCTION: recoverVI, recover voltage and current phasors from SDP variables
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################
    def recoverVI(self):
        self.fd.write('V' + str(self.SourceBus) + '= v0;\n')
        bus_queue = queue.Queue()
        bus_queue.put(self.SourceBus)
        while not bus_queue.empty():
            cur_bus = bus_queue.get()
            if cur_bus in self.downstream_dict:
                for d_bus in self.downstream_dict[cur_bus]:
                    # find the corresponding phase index
                    phase_cur = self.bus_phase_dict[cur_bus]
                    phase_d = self.bus_phase_dict[d_bus]
                    idx_list = [idx+1 for idx, val in enumerate(phase_cur) if val in phase_d]
                                       

                    self.fd.write('I' + cur_bus + d_bus + ' = 1/trace(v' + cur_bus + '(' + str(idx_list) + ',' + str(idx_list) + '))*ctranspose(S' + cur_bus + d_bus + ')*V' + cur_bus + '(' + str(idx_list) + ');\n')
                    if d_bus not in self.reg_bus:
                        self.fd.write('V' + d_bus + ' = V' + cur_bus + '(' + str(idx_list) + ') - Z' + cur_bus + d_bus + '*I' + cur_bus + d_bus + ';\n')
                    else:
                        self.fd.write('V' + d_bus + ' = (V' + cur_bus + '(' + str(idx_list) + ') - Z' + cur_bus + d_bus + '*I' + cur_bus + d_bus + ') .* alpha' + d_bus + ';\n')
                           
                    bus_queue.put(d_bus)        
                    

    ###########################################################################
    #FUNCTION: changeToPerUnit, change real value to per unit
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################
    def changeToPerUnit(self):
        self.fd.write('\n')
        self.fd.write('\n')
        self.fd.write('phasors=[];\n')
        
        bus_queue = queue.Queue()
        bus_queue.put(self.SourceBus)
        while not bus_queue.empty():
            cur_bus = bus_queue.get()
            print(cur_bus)
            phase_list = self.bus_phase_dict[cur_bus]
            sum = 0
            for a in phase_list:
                sum = sum * 10 + a
            self.fd.write('phasors=[phasors;recover_voltage(V' + cur_bus + ', ' + str(sum) + ')];\n')
            if cur_bus in self.downstream_dict:
                for d_bus in self.downstream_dict[cur_bus]:
                    bus_queue.put(d_bus)
        
        # change to per unit
        self.fd.write('\n')
        self.fd.write('% change to per unit\n')
        self.fd.write('phasors(:, 1) = phasors(:, 1) / Vbase;\n')
        self.fd.write('phasors(:, 3) = phasors(:, 3) / Vbase;\n')
        self.fd.write('phasors(:, 5) = phasors(:, 5) / Vbase;\n')
        self.fd.write('\n')
        ## output the three phase power
    
        self.fd.write('\n')        
           

    ###########################################################################
    #FUNCTION: MATLABoutput
    
    #INPUT: None

    #OUTPUT: None
    ########################################################################### 
    def MATLABoutput(self):
        self.fd.write('\n')
        self.fd.write('\n')
        self.fd.write('Voltage_output=[];\n')
        
        load_nodes = pd.read_csv("data/loads data.csv", sep = ',', header=None)
        N_load= len(load_nodes.index)
        for i in range(N_load):
            node = str(load_nodes.iloc[i,0])
            phase_list = self.bus_phase_dict[node]
            sum = 0
            for a in phase_list:
                sum = sum * 10 + a
            self.fd.write('Voltage_output = [Voltage_output; recover_voltage(V' + node + ', ' + str(sum) + ')];\n')
        
        # change to per unit
        self.fd.write('\n')
        self.fd.write('% change to per unit\n')
        self.fd.write('Voltage_output(:, 1) = Voltage_output(:, 1) / Vbase;\n')
        self.fd.write('Voltage_output(:, 3) = Voltage_output(:, 3) / Vbase;\n')
        self.fd.write('Voltage_output(:, 5) = Voltage_output(:, 5) / Vbase;\n')
        self.fd.write('\n')
    
        # output the voltage profile
        self.fd.write('\n')
        self.fd.write('disp(diag(S150R149) / 1000)')
           
    
    
    ###########################################################################
    #FUNCTION: close
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################         
    def close(self):
        self.fd.close()
        

        
        
if __name__ == "__main__": 
    # regulator bus
    reg_bus = ['150R', '9R', '25R', '160R']
    reg_phase = ['ABC', 'A', 'AC', 'ABC']
    
    # DER
    der_list = []
    
    opf = OPF(4160, '150', reg_bus, reg_phase)
    opf.loadData()
    opf.VoltageRegulatorTaps()
    opf.Zimpedances()
    opf.basicParameters(1.00, 0.9, 1.1) # Voltage at substation
    opf.createVariables(der_list)
    opf.ObjectiveFunction(der_list)
    opf.Constraints(der_list)
    opf.recoverVI()
    opf.changeToPerUnit()
    opf.MATLABoutput()
    opf.close()
    del opf
