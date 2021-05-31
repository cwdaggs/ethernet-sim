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
    SIM_TIME = 100000   # This should be large
    SLOT_TIME = 1
    N = 30
    ARRIVAL_RATES = [0.001, 0.002, 0.003, 0.006, 0.008, 0.01, 0.015, 0.02, 0.024, 0.03]  # Check the submission guidelines [0.003] #
    RETRANMISSION_POLICIES = ["pp", "op", "beb", "lb"]#, "beb", "lb"]["pp"]
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
        self.transmitting_node_index = 0
        self.action = env.process(self.run())
       
    def run(self):
        print("Server process started", self.retran_policy)
        
        # Generator function- Will never terminate but will pass control back when yield is reached
        while True: 
            yield self.env.timeout(G.SLOT_TIME)
            self.current_slot += 1
            temp = 0
  
            # loop through node dict, if (len >= 1) then add to transmitting nodes (list of indexes)
            for node in list(range(1,G.N+1)):
                if self.dictionary_of_nodes[node].len >= 1:
                    # Add node ID to transmitting nodes
                    self.transmitting_nodes.append(self.dictionary_of_nodes[node].id)
                    self.total_transmitting += 1
                # if on last item in list and only one node transmitting
            if self.total_transmitting == 1:
                self.successful_slots += 1
                self.dictionary_of_nodes[self.transmitting_nodes[0]].len -= 1 #subtract length of node in dict

            if self.total_transmitting >= 2:
            
                if self.retran_policy == "pp":
                    for elem in self.transmitting_nodes:
                        if random.random() <= 0.5:
                            temp += 1
                            if temp == 2:
                                break
                            self.dictionary_of_nodes[elem].retransmit_slot = self.current_slot
                elif self.retran_policy == "op":
                    for elem in self.transmitting_nodes:
                        if random.random() <= 1/G.N:
                            temp += 1
                            if temp == 2:
                                break
                            self.dictionary_of_nodes[elem].retransmit_slot = self.current_slot
                elif self.retran_policy == "beb" or self.retran_policy == "lb":
                    for elem in self.transmitting_nodes:
                        cur_node = self.dictionary_of_nodes[elem]
                        # Nodes trying to transmit in this slot
                        if cur_node.retransmit_slot == self.current_slot:
                            print("got here")
                            temp += 1
                            # Collision occurred
                            if temp == 2:
                                break
                            self.transmitting_node_index = elem
                    # No collision
                    if temp == 1:
                        self.dictionary_of_nodes[self.transmitting_node_index].len -= 1
                        # need a conditional on this?
                        self.dictionary_of_nodes[self.transmitting_node_index].n = 0
                        # need a conditional on this?
                        self.dictionary_of_nodes[self.transmitting_node_index].retransmit_slot = 0
                        self.successful_slots += 1
                    elif temp == 2:
                        for elem in self.transmitting_nodes:
                            if self.retran_policy == "beb":
                                max = random.randint(0, pow(2, min(self.dictionary_of_nodes[elem].n, 10)))
                            else:
                                max = random.randint(0, min(self.dictionary_of_nodes[elem].n, 1024))
                            # fix this
                            if self.dictionary_of_nodes[elem].retransmit_slot == 0:
                                self.dictionary_of_nodes[elem].retransmit_slot = self.current_slot + max
                            else: 
                                self.dictionary_of_nodes[elem].retransmit_slot += max
                            self.dictionary_of_nodes[elem].n += 1
           
                
                if self.retran_policy == "pp" or self.retran_policy == "op":
                    # If no collisions and not empty
                    if temp == 1:
                        # Find correct node
                        for elem in self.transmitting_nodes:
                            cur_node = self.dictionary_of_nodes[elem]
                            if cur_node.retransmit_slot == self.current_slot:
                                cur_node.len -= 1
                                self.successful_slots += 1

                # if self.retran_policy == "beb":
                #     for elem in self.transmitting_nodes:
                #         cur_node = self.dictionary_of_nodes[elem]
                #         if cur_node.retransmit_slot == self.current_slot:
                #             temp += 1
                #             if temp == 2:
                #                 break
                #             self.transmitting_node_index = elem
                #     if temp == 1:
                #         self.dictionary_of_nodes[self.transmitting_node_index].len -= 1
                #         self.dictionary_of_nodes[self.transmitting_node_index].n = 0
                #         self.dictionary_of_nodes[self.transmitting_node_index].retransmit_slot = 0
                #         self.successful_slots += 1
                #     else:
                #         for elem in self.transmitting_nodes:
                #             max = random.randint(0, pow(2, min(self.dictionary_of_nodes[elem].n, 10)))
                #             self.dictionary_of_nodes[elem].retransmit_slot = self.current_slot + max
                #             self.dictionary_of_nodes[elem].n += 1

            temp = 0
            self.transmitting_nodes.clear()
            self.total_transmitting = 0
            self.transmitting_node_index = 0

            


                    
        
class Node_Process(object): 
    def __init__(self, env, id, arrival_rate):
        
        self.env = env
        # Number for identification
        self.id = id
        self.arrival_rate = arrival_rate
        self.len = 0
        self.retransmit_slot = 0
        self.n = 0
        # Other state variables
        
        self.action = env.process(self.run())
        
    # Automatically started when object instantiated
    def run(self):
        # print("Arrival Process Started:", self.id)
        while True:
            yield self.env.timeout(random.expovariate(self.arrival_rate))
            self.len += 1



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
    throughputs = []
    lambda_n = []
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
            # print(server_process.successful_slots)
            # throughput = server_process.successful_slots/G.SIM_TIME
            throughputs.append(server_process.successful_slots/G.SIM_TIME)
            # print(throughput)
        
        # code to plot 
    for arrival_rate in G.ARRIVAL_RATES:
        lambda_n.append(arrival_rate * G.N)

    plt.plot(lambda_n, throughputs[0:10], label="pp")
    plt.plot(lambda_n, throughputs[10:20], label="op")
    plt.plot(lambda_n, throughputs[20:30], label="beb")
    plt.plot(lambda_n, throughputs[30:40], label="lb")
    plt.axis([-0.05, 1.2, -0.05, 0.9])
    plt.legend()
    plt.xlabel("Offered Load (Lambda * N)")
    plt.ylabel("Achieved Throughput")
    plt.grid(True)
    plt.savefig('name2.png')   
    plt.show()
    
if __name__ == '__main__': main()

