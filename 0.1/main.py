import pandas as pd
import queue
import Bus
import ZandC

# forget about the per unit system 
# use real value
class OPF:
    ###########################################################################
    #FUNCTION: init, the constructor
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################
    def __init__(self):
        # The Voltage base
        self.Vbase = 4160 # V
        
        # Voltage regulator nodes
        self.reg_bus = ['150R', '9R', '25R', '160R']
        
        # (1) get the bus dict 
        (self.bus_dict, self.N_bus, self.threePbus) = Bus.Bus_gen()
        
        # (2) get the Z and C bus
        (self.Zbus, self.Cbus) = ZandC.gen_ZC(self.Vbase)
    
        # (3) the bus -> phase dict
        self.bus_phase_dict = dict()
        self.bus_phase_dict['150'] = [1,2,3]
        
        # (4) the bus -> downstream bus dictionary
        self.downstream_dict = dict()
        
        # (5) transistion bus, having both abc and 012 variables
        self.transistion_bus = set()
    
        # (6) line data, read from file
        self.line_data = pd.read_csv("data/line data.csv", header=None)
        self.N_lines = len(self.line_data.index)
    
    
        # open the file
        self.fd = open('ieee123_iter.m', 'w')
        # first line, MATLAB function declare
        self.fd.write('function [Voltage_output, phasors] = ieee123_iter(loads, Zbus, Cbus)\n')
        
        
    ###########################################################################
    #FUNCTION: VoltageRegulatorTaps, set the voltage regulator taps
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################    
    def VoltageRegulatorTaps(self):
        self.fd.write('\n')
        self.fd.write('% voltage regulator taps \n')
        ## voltage regulator parameters
        for reg in self.reg_bus:
            if reg == '150R' or reg == '160R':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapB' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapC' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = [tapA' + reg + '; tapB' + reg + '; tapC' + reg + '];\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")
            elif reg == '25R':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('tapC' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = [tapA' + reg + '; tapC' + reg + '];\n')
                self.fd.write('alphaM' + reg + ' = alpha' + reg + ' * alpha' + reg + "';\n")            
            elif reg == '9R':
                self.fd.write('\n')
                self.fd.write('% voltage regulator: ' + reg + '\n')
                self.fd.write('tapA' + reg + ' = 1.0 + 0.00625 * 0;\n')
                self.fd.write('alpha' + reg + ' = tapA' + reg + ';\n')
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
    #FUNCTION: basicParameters, basic parameters for the model
    # Voltage profile, sequential component parameters
    #INPUT: None

    #OUTPUT: None
    ########################################################################### 
    def basicParameters(self):
        self.fd.write('\n')
        self.fd.write('\n')
        # slack bus voltage
        self.fd.write('% three phase voltage at slack bus\n')
        self.fd.write('Vbase = ' + str(self.Vbase) + ' / sqrt(3);\n')
        self.fd.write("v0=1.02 * Vbase * [0,sqrt(3),0]';\n")
        # voltage lower and upper bounds
        self.fd.write('% voltage upper and lower bounds\n')
        self.fd.write('V_lb = 0.90 * Vbase;\n')
        self.fd.write('V_ub = 1.055 * Vbase;\n')
        self.fd.write('v_lb = V_lb * V_lb;\n')
        self.fd.write('v_ub = V_ub * V_ub;\n')
        self.fd.write('\n')
        # sequential component parameters (matrices)
        self.fd.write('% sequential component parameters\n')
        self.fd.write('a = -0.5 + 0.5 * i * sqrt(3);\n')
        self.fd.write('A = 1/sqrt(3) * [1,1,1; 1, a*a, a; 1, a, a*a];\n')
        self.fd.write('AH = 1/sqrt(3) * [1,1,1; 1, a, a*a; 1, a*a, a];\n')
        self.fd.write('\n')  
        

    ###########################################################################
    #FUNCTION: createVariables, create CVX variables (V, I, S)
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################        
    def createVariables(self):
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
            
            # the three phase -> single or two phase bus
            if from_bus in self.threePbus and to_bus not in self.threePbus and from_bus not in self.transistion_bus:
                self.fd.write('variable v' + from_bus + '_abc(3,3) hermitian\n')
                self.transistion_bus.add(from_bus)
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
             

    ###########################################################################
    #FUNCTION: ObjectiveFunction, create the objective function
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################    
    def ObjectiveFunction(self):
        self.fd.write('\n')   
        self.fd.write('\n')   
    
        # minimize losses
        self.fd.write('minimize(')
        for l in range(self.N_lines):
            from_bus = str(self.line_data.iloc[l, 0])
            to_bus = str(self.line_data.iloc[l, 1])        
            Z_cur = 'Z' + from_bus + to_bus
            l_cur = 'l' + from_bus + to_bus
            if to_bus not in self.threePbus:
                self.fd.write('trace(real('+ Z_cur + '*' + l_cur + ')) + ')
            else:
                self.fd.write('trace(real(A * '+ Z_cur + '*' + l_cur + ' * AH)) + ')
            #self.fd.write('trace(imag('+ Z_cur + '*' + l_cur + ')) + ')
        self.fd.write('0)\n')
        
        self.fd.write('subject to\n')  
    

    ###########################################################################
    #FUNCTION: Constraints, create model constraints
    # (1) voltage upper and lower bounds
    # (2) voltage across a line 
    # (3) semidefinite contraints
    # (4) power flow balance
    #INPUT: None

    #OUTPUT: None
    ###########################################################################    
    def Constraints(self):
        # (1) voltage upper and lower bounds
        self.fd.write('\n')
        self.fd.write('\n')
        self.fd.write('% constraints: \n')
        self.fd.write('% (1): voltage lower and upper bounds \n')
        for l in range(self.N_lines):
            to_bus = str(self.line_data.iloc[l, 1])
            # three phase bus, use Seq. values
            if to_bus in self.threePbus:
                self.fd.write('v_lb <= diag(A * v' + to_bus + ' * ctranspose(A)) <= v_ub;\n')
            # non-three phase bus, use abc values
            else:
                self.fd.write('v_lb <= diag(v' + to_bus + ') <= v_ub;\n')
                
        self.fd.write('v150 == v0 * ctranspose(v0);\n' )  
        
        # (2) voltage across a line 
        # (3) semidefinite contraints
        # (4) power flow balance
        # (5) bridge between the transistion bus
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
                if to_bus in self.threePbus:
                    # (2) voltage across a line, both side three phase bus
                    self.fd.write('A * v' + to_bus + ' * AH == (A * (v' + from_bus + '(' + str(idx_list) + ',' + str(idx_list) + ') -'  + S_cur + '*ctranspose(' + Z_cur + ') - ' + Z_cur + '*ctranspose(' + S_cur + ') + ' + Z_cur + '*' + l_cur + '*ctranspose(' + Z_cur + ')) * AH) .* alphaM' + to_bus + ';\n') 
                elif from_bus in self.threePbus:
                    # (2) voltage across a line, from side three phase bus 
                    self.fd.write('v' + to_bus + ' == (v' + from_bus + '_abc(' + str(idx_list) + ',' + str(idx_list) + ') - ' + S_cur + '*ctranspose(' + Z_cur + ') - ' + Z_cur + '*ctranspose(' + S_cur + ') + ' + Z_cur + '*' + l_cur + '*ctranspose(' + Z_cur + ')) .* alphaM' + to_bus + ';\n') 
                else:
                    # (2) voltage across a line, both side non-three phase bus
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
                # from phase bus is a three phase bus
                if from_bus in self.threePbus:
                    # voltage across a line
                    self.fd.write('v' + to_bus + ' == v' + from_bus + '_abc(' + str(idx_list) + ',' + str(idx_list) + ') - ' + S_cur + '*ctranspose(' + Z_cur + ') - ' + Z_cur + '*ctranspose(' + S_cur + ') + ' + Z_cur + '*' + l_cur + '*ctranspose(' + Z_cur + ');\n')
                    # semidefinite constraint
                    self.fd.write('[v' + from_bus + '_abc(' + str(idx_list) + ',' + str(idx_list) + '), ' + S_cur + '; ctranspose(' + S_cur + '), ' + l_cur + '] >= 0;\n')
                else:
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
            
            # upstream line
            if from_bus in self.threePbus and to_bus in self.threePbus:
                self.fd.write('diag(A *(' + S_cur + '-' + Z_cur + '*' + l_cur + ') * AH)') 
            else:
                self.fd.write('diag(' + S_cur + '-' + Z_cur + '*' + l_cur + ')') 
            
            # load 
            self.fd.write('- loads(' + str(load_idx) + ')')
            
            # shunt capacitance
            if to_bus in self.threePbus:
                # add the capacitance data
                self.fd.write(' + diag(A * v' + to_bus + ' * Cbus(' + str(load_idx) + ',' + str(load_idx) + ') * AH) == ')
            else:
                # add the capacitance data
                self.fd.write(' + diag(v' + to_bus + ' * Cbus(' + str(load_idx) + ',' + str(load_idx) + ')) == ') 
                
            # downstream flows
            if to_bus in self.downstream_dict:
                for d_bus in self.downstream_dict[to_bus]:
                    # equal phase config
                    if len(self.bus_phase_dict[to_bus]) == len(self.bus_phase_dict[d_bus]):
                        if to_bus in self.threePbus:
                            self.fd.write('diag(A * S' + to_bus + d_bus + ' * AH) + ')  
                        else:
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
        
        # (5) bridge between the transistion bus
        for bus in self.transistion_bus:
            self.fd.write('v' + bus + '_abc == A * v' + bus + ' * AH;\n')
            
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
        self.fd.write('V150 = A * v0;\n')
        bus_queue = queue.Queue()
        bus_queue.put('150')
        while not bus_queue.empty():
            cur_bus = bus_queue.get()
            if cur_bus in self.downstream_dict:
                for d_bus in self.downstream_dict[cur_bus]:
                    # find the corresponding phase index
                    phase_cur = self.bus_phase_dict[cur_bus]
                    phase_d = self.bus_phase_dict[d_bus]
                    idx_list = [idx+1 for idx, val in enumerate(phase_cur) if val in phase_d]
                    
                    # both from and to buses are three phase buses
                    if cur_bus in self.threePbus and d_bus in self.threePbus:
                        self.fd.write('I' + cur_bus + d_bus + ' = 1/trace(A * v' + cur_bus + '(' + str(idx_list) + ',' + str(idx_list) + ') * AH) * ctranspose(A * S' + cur_bus + d_bus + ' * AH)*V' + cur_bus + '(' + str(idx_list) + ');\n')
                        if d_bus not in self.reg_bus:
                            self.fd.write('V' + d_bus + ' = V' + cur_bus + '(' + str(idx_list) + ') - A * Z' + cur_bus + d_bus + '* AH *I' + cur_bus + d_bus + ';\n')
                        else:
                            self.fd.write('V' + d_bus + ' = (V' + cur_bus + '(' + str(idx_list) + ') - A * Z' + cur_bus + d_bus + '* AH *I' + cur_bus + d_bus + ').* alpha' + d_bus + ';\n')
                    
                    # just the from bus is three phase bus
                    elif cur_bus in self.threePbus:
                        self.fd.write('I' + cur_bus + d_bus + ' = 1/trace(v' + cur_bus + '_abc(' + str(idx_list) + ',' + str(idx_list) + ') ) * ctranspose(S' + cur_bus + d_bus + ')*V' + cur_bus + '(' + str(idx_list) + ');\n')
                        if d_bus not in self.reg_bus:
                            self.fd.write('V' + d_bus + ' = V' + cur_bus + '(' + str(idx_list) + ') - Z' + cur_bus + d_bus + '*I' + cur_bus + d_bus + ';\n')
                        else:
                            self.fd.write('V' + d_bus + ' = (V' + cur_bus + '(' + str(idx_list) + ') - Z' + cur_bus + d_bus + '*I' + cur_bus + d_bus + ') .* alpha' + d_bus + ';\n')
                    
                    # both buses are non-three phase buses
                    else: 
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
        bus_queue.put('150')
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
        self.fd.write('disp(diag(A * S150R149 * AH) / 1000)')
        self.fd.close()     
    
    
    ###########################################################################
    #FUNCTION: close
    
    #INPUT: None

    #OUTPUT: None
    ###########################################################################         
    def close(self):
        self.fd.close()
        

        
if __name__ == "__main__": 
    opf = OPF()
    opf.VoltageRegulatorTaps()
    opf.Zimpedances()
    opf.basicParameters()
    opf.createVariables()
    opf.ObjectiveFunction()
    opf.Constraints()
    opf.recoverVI()
    opf.changeToPerUnit()
    opf.MATLABoutput()
    opf.close()
    
