# DMS
distribution management system

0.1: basic version, no DER is installed, the OPF problem reduced to a PF problem. This version is used to test the accuracy of BFM-SDP method

0.12: basic version. Approximations are made on ZIP load models and Wye Delta connections. The goal is to solve OPF in just 1 iteration with approximate loads.
Tested on IEEE 123 node test feeder, the approximate makes it possible to solve the OPF in just one iteration at the costs of less accuracy.

0.2: DER is introduced, voltage regulation constraint added.
