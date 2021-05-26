import simpy
import sys
import math
import numpy as np
import random
import matplotlib.pyplot as plt


# Hosts can only transmit at slot boundaries
# For a new packet, node attempts transmission in the next slot boundary
# If a slot has 2+ hosts ready to transmit, there will be collision so packet not received
# and must be re-transmitted

# Algorithm changes how retransmission happens
# 

packets = []

# First  define some global variables. You should change values
class G:
    RANDOM_SEED = 33
    SIM_TIME = 1000000   # This should be large
    SLOT_TIME = 1
    N = 30
    ARRIVAL_RATES = [0.001, 0.002, 0.003, 0.006, 0.008, 0.01, 0.015, 0.02, 0.024, 0.03]  # Check the submission guidelines
    RETRANMISSION_POLICIES = ["pp", "op", "beb", "lb"]
    LONG_SLEEP_TIMER = 1000000000

        

class Server_Process(object):
    def __init__(self, env, dictionary_of_nodes, retran_policy, slot_stat):
        self.env = env
        self.dictionary_of_nodes = dictionary_of_nodes 
        self.retran_policy = retran_policy 
        self.slot_stat = slot_stat
        self.current_slot = 0
        self.successful_slots = 0
        self.transmitting_nodes = []
        self.total_transmitting = 0   
        
        self.action = env.process(self.run())
       
    def run(self):
        print("Server process started")
        
        # Generator function- Will never terminate but will pass control back when yield is reached
        while True: 
            # sleep for slot time
            # total_time += 1
            yield self.env.timeout(G.SLOT_TIME)
            self.current_slot += 1
            temp = 0
            # Code to determine what happens to a slot and 
            # then update node variables accordingly based 
            # on the algorithm 
  
            # loop through node dict, if (len >= 1) then add to trnasmittin nodes
            for node in list(range(1,G.N+1)):
                if self.dictionary_of_nodes[node].len >= 1:
                    self.transmitting_nodes.append(self.dictionary_of_nodes[node].id)
                    self.total_transmitting += 1
                if node == G.N and self.total_transmitting == 1:
                    self.successful_slots += 1
                    self.dictionary_of_nodes[self.transmitting_nodes[0]].len -= 1 #subtract length of node in dict
                    self.transmitting_nodes.clear()
                    self.total_transmitting = 0
            if self.total_transmitting >= 2:
                for elem in self.transmitting_nodes:
                    if self.retran_policy == "pp":
                        if random.random() <= 0.5:
                            temp += 1
                            self.dictionary_of_nodes[elem].retransmit_slot = self.current_slot
                    elif self.retran_policy == "op":
                        if random.random() <= 1/G.N:
                            temp += 1
                            self.dictionary_of_nodes[elem].retransmit_slot = self.current_slot
                    elif self.retran_policy == "beb":
                        max = pow(2, self.dictionary_of_nodes[elem].k)
                        self.dictionary_of_nodes[elem].retransmit_slot = random.random() * max
                    else:
                        self.dictionary_of_nodes[elem].retransmit_slot = random.random() * self.dictionary_of_nodes[elem].k # should be elem.retrans_slot
                
                if self.retran_policy == "pp" or self.retran_policy == "op":
                    if temp == 1:
                        for elem in self.transmitting_nodes:
                            self.successful_slots += 1
                            cur_node = self.dictionary_of_nodes[elem]
                            if cur_node.retransmit_slot == self.current_slot:
                                cur_node.len -= 1
                                if cur_node.len == 0:
                                    self.transmitting_nodes.remove(elem)
                                    self.total_transmitting -= 1
                if self.retran_policy == "beb":
                    break    

            


                    
        
class Node_Process(object): 
    def __init__(self, env, id, arrival_rate):
        
        self.env = env
        # Number for identification
        self.id = id
        self.arrival_rate = arrival_rate
        self.len = 0
        self.retransmit_slot = 0
        self.k = 0
        # Other state variables
        
        self.action = env.process(self.run())
        
    # Automatically started when object instantiated
    def run(self):
        # packet arrivals 
        #print("Arrival Process Started:", self.id)
        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            self.len += 1
        # Code to generate the next packet and deal with it
        
        # create an array of packets, if any
    def get_id(self):
        return self.id 
        

class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time


class StatObject(object):    
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)
    
    def getLength(self):
        return len(self.dataset)




def main():
    #if sys.argv[2] not in G.RETRANMISSION_POLICIES:
    #    sys.exit("Invalid algorithm.")

    print("Simulation Analysis of Random Access Protocols")
    random.seed(G.RANDOM_SEED)

    for retran_policy in G.RETRANMISSION_POLICIES: 
        for arrival_rate in G.ARRIVAL_RATES:
            # Allows for the creation of new events
            env = simpy.Environment()
            slot_stat = StatObject()
            dictionary_of_nodes  = {} 
                                      
            
            for i in list(range(1,G.N+1)):
                node = Node_Process(env, i, arrival_rate)
                dictionary_of_nodes[i] = node
            server_process = Server_Process(env, dictionary_of_nodes,retran_policy,slot_stat)
            env.run(until=G.SIM_TIME)
            
            # code to determine throughput
            # total_slots = server_process.slot_stat.getLength()
            throughput = slot_count/G.SIM_TIME
        
        # code to plot 
        plt.plot(G.ARRIVAL_RATES * G.N, throughput)   
    
if __name__ == '__main__': main()

