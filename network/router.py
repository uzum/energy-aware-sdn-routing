import sys
import random
import json
import numpy as np
import random
from config import *

class Router():
    def __init__(self, topology, api):
        self.topology = topology
        self.api = api

    def collectStatistics(self):
        cumulativeStats = {}
        for switch, stats in self.api.collectPorts().iteritems():
            switchObject = self.topology.get('s' + switch[len(switch) - 1])
            portStats = stats['port_reply'][0]['port']
            cumulativeStats[switchObject.name] = {}
            for port in portStats:
                if (port['port_number'] != 'local'):
                    if (int(port['port_number']) in switchObject.portMap):
                        neighbor = switchObject.portMap[int(port['port_number'])]
                        cumulativeStats[switchObject.name][neighbor.name] = port

        for portStats in self.api.collectBandwidth():
            switchId = portStats['dpid']
            if (portStats['port'] != 'local'):
                switchObject = self.topology.get('s' + switchId[len(switchId) - 1])
                if (int(portStats['port']) in switchObject.portMap):
                    neighbor = switchObject.portMap[int(portStats['port'])]
                    cumulativeStats[switchObject.name][neighbor.name]['link-speed-bits-per-second'] = portStats['link-speed-bits-per-second']
                    cumulativeStats[switchObject.name][neighbor.name]['bits-per-second-rx'] = portStats['bits-per-second-rx']
                    cumulativeStats[switchObject.name][neighbor.name]['bits-per-second-tx'] = portStats['bits-per-second-tx']

        return cumulativeStats

    def calculateRandomRoute(self, host, locations):
        routes = {}
        probable_paths = []
        #initially look at the cache of the requesting host itself        
        inlocalcache = 0   
        innghhost = 0
        for i in np.arange(len(locations['base'])):
            if(locations['base'][i] == host):
                #if found in its cache then set destination to host and path to empty
                probable_paths.append({'host': host, 'destination': host,  '_path': []})  
                inlocalcache = 1
                
            
            
        #if not found in the cache itself look at the switch that the host is connected to
        if(inlocalcache == 0):
            hostObject = self.topology.get(host)
            hostAttachmentSwitch = hostObject.switch
            for i in np.arange(len(hostAttachmentSwitch.hosts)):
                for j in np.arange(len(locations['base'])):
                    if(hostAttachmentSwitch.hosts[i].name == locations['base'][j]):
                            #if found then assign the route
                            # return 2 routes for the base layer 
                            probable_paths.append({'host': host,
                                               'destination':hostAttachmentSwitch.hosts[i].name ,
                                               '_path': [hostAttachmentSwitch.name]})
                            innghhost = 1
    
            if(innghhost == 0):
                hostAttachmentSwitch = self.topology.switches[0]
                sink_tree_root = hostAttachmentSwitch.name
                #print sink_tree_root
                sink_tree = []
                not_traversed = 0
                L = []
                L.append([sink_tree_root])
                #print L

                l1s = hostAttachmentSwitch.switches
                #print l1s
                X = []
                for i in np.arange(len(l1s)):
                    X.append(l1s[i].name)
                    #print l1s[i].name
                L.append(X)
                #print L[1][1]
                
                Y = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        if cur_l2s[j].name not in L[0] and cur_l2s[j].name not in L[1] and cur_l2s[j].name not in Y:
                            Y.append(cur_l2s[j].name)
                
                L.append(Y)  
                #print L

                Z = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        cur_l3s = cur_l2s[j].switches
                        for k in np.arange(len(cur_l3s)):
                            if cur_l3s[k].name not in L[0] and cur_l3s[k].name not in L[1] and cur_l3s[k].name not in L[2]and cur_l3s[k].name not in Z:
                                Z.append(cur_l3s[k].name)

                L.append(Z)  
                
                routes = {}
                #for each of the base storing host look at the switch
                for i in np.arange(len(locations['base'])):
                    #hj
                    cur_host = self.topology.get(locations['base'][i])
                    #print cur_host.name + ' ' +cur_host.switch.name
                    #if cur_host.switch is in level 1 of L
                    for a in np.arange(len(L[1])):        
                        if(cur_host.switch.name == L[1][a]):
                            if(L[0][0] == hostAttachmentSwitch.name):
                                #print L[1][a]
                                probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, cur_host.switch.name]})
                    #else if cur_host.switch is in level 2 of L
                    for a in np.arange(len(L[2])):    
                        if(cur_host.switch.name == L[2][a]):
                            for j in np.arange(len(L[1])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[1][j]):
                                        #print L[2][a] + ' ' + L[1][j]
                                        probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][j], cur_host.switch.name]})
                    #else if cur_host.switch is in level 3 of L
                    for a in np.arange(len(L[3])):     
                        if(cur_host.switch.name == L[3][a]):
                            #print L[3]
                            for j in np.arange(len(L[2])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[2][j]):
                                        for b in np.arange(len(L[1])):
                                            for c in np.arange(len(cur_host.switch.switches[k].switches)):
                                                if(cur_host.switch.switches[k].switches[c].name == L[1][b]):
                                                    #print L[3][a] + ' ' + L[2][j] + ' ' + L[1][b]
                                                    probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][b], L[2][j], cur_host.switch.name]})

                #print probable_paths
                if(len(probable_paths) > 0):
                    x = random.randint(0,len(probable_paths)-1)
                    cur_path_x = probable_paths[x]
                
                    y = random.randint(0,len(probable_paths)-1)
                    cur_path_y = probable_paths[y]
                    routes['base'] = [cur_path_x,cur_path_y] 
                else:
                    routes['base'] = [] 
                
        #print routes['base']
        probable_paths = []        
        #initially look at the cache of the requesting host itself        
        inlocalcache = 0   
        innghhost = 0
        for i in np.arange(len(locations['enhancement'])):
            if(locations['enhancement'][i] == host):
                #if found in its cache then set destination to host and path to empty
                probable_paths.append({'host': host, 'destination': host,  '_path': []})  
                inlocalcache = 1
                
            
            
        #if not found in the cache itself look at the switch that the host is connected to
        if(inlocalcache == 0):
            hostObject = self.topology.get(host)
            hostAttachmentSwitch = hostObject.switch
            for i in np.arange(len(hostAttachmentSwitch.hosts)):
                for j in np.arange(len(locations['enhancement'])):
                    if(hostAttachmentSwitch.hosts[i].name == locations['enhancement'][j]):
                            #if found then assign the route
                            # return 2 routes for the base layer 
                            probable_paths.append({'host': host,
                                               'destination':hostAttachmentSwitch.hosts[i].name ,
                                               '_path': [hostAttachmentSwitch.name]})
                            innghhost = 1
    
            if(innghhost == 0):
                hostAttachmentSwitch = self.topology.switches[0]
                sink_tree_root = hostAttachmentSwitch.name
                #print sink_tree_root
                sink_tree = []
                not_traversed = 0
                L = []
                L.append([sink_tree_root])
                #print L

                l1s = hostAttachmentSwitch.switches
                #print l1s
                X = []
                for i in np.arange(len(l1s)):
                    X.append(l1s[i].name)
                    #print l1s[i].name
                L.append(X)
                #print L[1][1]
                
                Y = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        if cur_l2s[j].name not in L[0] and cur_l2s[j].name not in L[1] and cur_l2s[j].name not in Y:
                            Y.append(cur_l2s[j].name)
                
                L.append(Y)  
                #print L

                Z = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        cur_l3s = cur_l2s[j].switches
                        for k in np.arange(len(cur_l3s)):
                            if cur_l3s[k].name not in L[0] and cur_l3s[k].name not in L[1] and cur_l3s[k].name not in L[2]and cur_l3s[k].name not in Z:
                                Z.append(cur_l3s[k].name)

                L.append(Z)  
                
                #routes = {}
                #for each of the base storing host look at the switch
                for i in np.arange(len(locations['enhancement'])):
                    #hj
                    cur_host = self.topology.get(locations['enhancement'][i])
                    #print cur_host.name + ' ' +cur_host.switch.name
                    #if cur_host.switch is in level 1 of L
                    for a in np.arange(len(L[1])):        
                        if(cur_host.switch.name == L[1][a]):
                            if(L[0][0] == hostAttachmentSwitch.name):
                                #print L[1][a]
                                probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, cur_host.switch.name]})
                    #else if cur_host.switch is in level 2 of L
                    for a in np.arange(len(L[2])):    
                        if(cur_host.switch.name == L[2][a]):
                            for j in np.arange(len(L[1])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[1][j]):
                                        #print L[2][a] + ' ' + L[1][j]
                                        probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][j], cur_host.switch.name]})
                    #else if cur_host.switch is in level 3 of L
                    for a in np.arange(len(L[3])):     
                        if(cur_host.switch.name == L[3][a]):
                            #print L[3]
                            for j in np.arange(len(L[2])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[2][j]):
                                        for b in np.arange(len(L[1])):
                                            for c in np.arange(len(cur_host.switch.switches[k].switches)):
                                                if(cur_host.switch.switches[k].switches[c].name == L[1][b]):
                                                    #print L[3][a] + ' ' + L[2][j] + ' ' + L[1][b]
                                                    probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][b], L[2][j], cur_host.switch.name]})

          
               
                #print probable_paths
                if(len(probable_paths) > 0):
                    x = random.randint(0,len(probable_paths)-1)
                    cur_path_x = probable_paths[x]
                    routes['enhancement'] = [cur_path_x]
                else:
                    routes['enhancement'] = []
         
        #print routes
        return routes

    def calculateLatencyOptimalRoute(self, host, locations):
        return self.calculateRandomRoute(host, locations)

    def calculate(self, strategy, host, locations):
        if (strategy == 'random'):
            return self.calculateRandomRoute(host, locations)
        elif (strategy == 'energy'):
            return self.calculateEnergyOptimalRoute(host, locations)
        elif (strategy == 'flow-test'):
            return {
                'base': [{
                    'host': 'h1',
                    'destination': 'h4',
                    '_path': ['s1', 's5', 's6', 's4', 's7', 's3']
                }],
                'enhancement': [{
                    'host': 'h1',
                    'destination': 'h7',
                    '_path': ['s1', 's5']
                }]
            }
        else:
            return self.calculateLatencyOptimalRoute(host, locations)
        
    def calculateEnergyOptimalRoute(self, host, locations):       
        routes = {}
        #initially look at the cache of the requesting host itself        
        inlocalcache = 0   
        innghhost = 0
        for i in np.arange(len(locations['base'])):
            if(locations['base'][i] == host):
                #if found in its cache then set destination to host and path to empty
                routes['base'] = [{'host': host, 'destination': host,  '_path': []}]  
                inlocalcache = 1
                
            
            
        #if not found in the cache itself look at the switch that the host is connected to
        if(inlocalcache == 0):
            hostObject = self.topology.get(host)
            hostAttachmentSwitch = hostObject.switch
            for i in np.arange(len(hostAttachmentSwitch.hosts)):
                for j in np.arange(len(locations['base'])):
                    if(hostAttachmentSwitch.hosts[i].name == locations['base'][j]):
                            #if found then assign the route
                            # return 2 routes for the base layer 
                            routes['base'] = [{'host': host,
                                               'destination':hostAttachmentSwitch.hosts[i].name ,
                                               '_path': [hostAttachmentSwitch.name]}]
                            }]
                            innghhost = 1
    
            if(innghhost == 0):
                hostAttachmentSwitch = self.topology.switches[0]
                sink_tree_root = hostAttachmentSwitch.name
                #print sink_tree_root
                sink_tree = []
                not_traversed = 0
                L = []
                L.append([sink_tree_root])
                #print L

                l1s = hostAttachmentSwitch.switches
                #print l1s
                X = []
                for i in np.arange(len(l1s)):
                    X.append(l1s[i].name)
                    #print l1s[i].name
                L.append(X)
                #print L[1][1]
                
                Y = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        if cur_l2s[j].name not in L[0] and cur_l2s[j].name not in L[1] and cur_l2s[j].name not in Y:
                            Y.append(cur_l2s[j].name)
                
                L.append(Y)  
                #print L

                Z = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        cur_l3s = cur_l2s[j].switches
                        for k in np.arange(len(cur_l3s)):
                            if cur_l3s[k].name not in L[0] and cur_l3s[k].name not in L[1] and cur_l3s[k].name not in L[2]and cur_l3s[k].name not in Z:
                                Z.append(cur_l3s[k].name)

                L.append(Z)  
                probable_paths = []
                routes = {}
                #for each of the base storing host look at the switch
                for i in np.arange(len(locations['base'])):
                    #hj
                    cur_host = self.topology.get(locations['base'][i])
                    #print cur_host.name + ' ' +cur_host.switch.name
                    #if cur_host.switch is in level 1 of L
                    for a in np.arange(len(L[1])):        
                        if(cur_host.switch.name == L[1][a]):
                            if(L[0][0] == hostAttachmentSwitch.name):
                                #print L[1][a]
                                probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, cur_host.switch.name]})
                    #else if cur_host.switch is in level 2 of L
                    for a in np.arange(len(L[2])):    
                        if(cur_host.switch.name == L[2][a]):
                            for j in np.arange(len(L[1])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[1][j]):
                                        #print L[2][a] + ' ' + L[1][j]
                                        probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][j], cur_host.switch.name]})
                    #else if cur_host.switch is in level 3 of L
                    for a in np.arange(len(L[3])):     
                        if(cur_host.switch.name == L[3][a]):
                            #print L[3]
                            for j in np.arange(len(L[2])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[2][j]):
                                        for b in np.arange(len(L[1])):
                                            for c in np.arange(len(cur_host.switch.switches[k].switches)):
                                                if(cur_host.switch.switches[k].switches[c].name == L[1][b]):
                                                    #print L[3][a] + ' ' + L[2][j] + ' ' + L[1][b]
                                                    probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][b], L[2][j], cur_host.switch.name]})

          
                
                
                LOW_ENERGY    = 30;
                MEDIUM_ENERGY = 40;
                HIGH_ENERGY   = 50;

                best = 100000000
                best_path = {}
                second_best = 100000000
                second_best_path = {}

                for i in np.arange(len(probable_paths)):
                    cur_path_energy = 0
                    cur_path = probable_paths[i]['_path']
                    #print cur_path
                    for j in np.arange(len(cur_path)-1):
                        cur_switch = cur_path[j]
                        next_switch   = cur_path[j+1]
                        #print cur_switch
                        s_switch = self.topology.get(cur_switch)
                        n_switch = self.topology.get(next_switch)
                        #print s_switch.energyClass + ' ' + 'xxx'
                        stats = self.collectStatistics()
                        rec = stats[s_switch.name][n_switch.name]['bits-per-second-rx']
                        tx  = stats[s_switch.name][n_switch.name]['bits-per-second-tx']
                        limit = stats[s_switch.name][n_switch.name]['link-speed-bits-per-second']
                        if(rec + tx < limit):
                            if  (s_switch.energyClass == 'low'):
                                cur_path_energy = cur_path_energy + LOW_ENERGY
                            elif(s_switch.energyClass == 'medium'):
                                cur_path_energy = cur_path_energy + MEDIUM_ENERGY
                            else:
                                cur_path_energy = cur_path_energy + HIGH_ENERGY
                        else:
                            cur_path_energy = cur_path_energy + HIGH_ENERGY
                            
                    cur_switch = cur_path[len(cur_path)-1]
                    #print cur_switch
                    s_switch = self.topology.get(cur_switch)
                       
                    if  (s_switch.energyClass == 'low'):
                        cur_path_energy = cur_path_energy + LOW_ENERGY
                    elif(s_switch.energyClass == 'medium'):
                        cur_path_energy = cur_path_energy + MEDIUM_ENERGY
                    else:
                        cur_path_energy = cur_path_energy + HIGH_ENERGY
                             
                    
                    if(cur_path_energy < best):
                        second_best = best
                        second_best_path = best_path 
                        best = cur_path_energy
                        best_path = probable_paths[i]
                        routes['base'] = [best_path,second_best_path] 
                #print best_path
                #print second_best_path
                
        ######################################################################################       
        #initially look at the cache of the requesting host itself        
        inlocalcache = 0   
        innghhost = 0
        for i in np.arange(len(locations['enhancement'])):
            if(locations['enhancement'][i] == host):
                #if found in its cache then set destination to host and path to empty
                routes['enhancement'] = [{'host': host, 'destination': host,  '_path': []}]  
                inlocalcache = 1
                
            
            
        #if not found in the cache itself look at the switch that the host is connected to
        if(inlocalcache == 0):
            hostObject = self.topology.get(host)
            hostAttachmentSwitch = hostObject.switch
            for i in np.arange(len(hostAttachmentSwitch.hosts)):
                for j in np.arange(len(locations['enhancement'])):
                    if(hostAttachmentSwitch.hosts[i].name == locations['enhancement'][j]):
                            #if found then assign the route
                            # return 2 routes for the base layer 
                            routes['enhancement'] = [{'host': host,
                                               'destination':hostAttachmentSwitch.hosts[i].name ,
                                               '_path': [hostAttachmentSwitch.name]}]
                            innghhost = 1
    
            if(innghhost == 0):
                hostAttachmentSwitch = self.topology.switches[0]
                sink_tree_root = hostAttachmentSwitch.name
                #print sink_tree_root
                sink_tree = []
                not_traversed = 0
                L = []
                L.append([sink_tree_root])
                #print L

                l1s = hostAttachmentSwitch.switches
                #print l1s
                X = []
                for i in np.arange(len(l1s)):
                    X.append(l1s[i].name)
                    #print l1s[i].name
                L.append(X)
                #print L[1][1]
                
                Y = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        if cur_l2s[j].name not in L[0] and cur_l2s[j].name not in L[1] and cur_l2s[j].name not in Y:
                            Y.append(cur_l2s[j].name)
                
                L.append(Y)  
                #print L

                Z = []
                for i in np.arange(len(l1s)):
                    cur_l2s = l1s[i].switches
                    for j in np.arange(len(cur_l2s)):
                        cur_l3s = cur_l2s[j].switches
                        for k in np.arange(len(cur_l3s)):
                            if cur_l3s[k].name not in L[0] and cur_l3s[k].name not in L[1] and cur_l3s[k].name not in L[2]and cur_l3s[k].name not in Z:
                                Z.append(cur_l3s[k].name)

                L.append(Z)  
                probable_paths = []
                
                #for each of the base storing host look at the switch
                for i in np.arange(len(locations['enhancement'])):
                    #hj
                    cur_host = self.topology.get(locations['enhancement'][i])
                    #print cur_host.name + ' ' +cur_host.switch.name
                    #if cur_host.switch is in level 1 of L
                    for a in np.arange(len(L[1])):        
                        if(cur_host.switch.name == L[1][a]):
                            if(L[0][0] == hostAttachmentSwitch.name):
                                #print L[1][a]
                                probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, cur_host.switch.name]})
                    #else if cur_host.switch is in level 2 of L
                    for a in np.arange(len(L[2])):    
                        if(cur_host.switch.name == L[2][a]):
                            for j in np.arange(len(L[1])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[1][j]):
                                        #print L[2][a] + ' ' + L[1][j]
                                        probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][j], cur_host.switch.name]})
                    #else if cur_host.switch is in level 3 of L
                    for a in np.arange(len(L[3])):     
                        if(cur_host.switch.name == L[3][a]):
                            #print L[3]
                            for j in np.arange(len(L[2])):
                                for k in np.arange(len(cur_host.switch.switches)):
                                    if(cur_host.switch.switches[k].name == L[2][j]):
                                        for b in np.arange(len(L[1])):
                                            for c in np.arange(len(cur_host.switch.switches[k].switches)):
                                                if(cur_host.switch.switches[k].switches[c].name == L[1][b]):
                                                    #print L[3][a] + ' ' + L[2][j] + ' ' + L[1][b]
                                                    probable_paths.append({'host': host,'destination':cur_host.name ,'_path': [hostAttachmentSwitch.name, L[1][b], L[2][j], cur_host.switch.name]})

          
                
                
                LOW_ENERGY    = 30;
                MEDIUM_ENERGY = 40;
                HIGH_ENERGY   = 50;

                best = 100000000
                best_path = {}
                second_best = 100000000
                second_best_path = {}

                for i in np.arange(len(probable_paths)):
                    cur_path_energy = 0
                    cur_path = probable_paths[i]['_path']
                    #print cur_path
                    for j in np.arange(len(cur_path)-1):
                        cur_switch = cur_path[j]
                        next_switch   = cur_path[j+1]
                        #print cur_switch
                        s_switch = self.topology.get(cur_switch) 
                        n_switch = self.topology.get(next_switch)
                        #print s_switch.energyClass + ' ' + 'xxx'
                        stats = self.collectStatistics()
                        rec = stats[s_switch.name][n_switch.name]['bits-per-second-rx']
                        tx  = stats[s_switch.name][n_switch.name]['bits-per-second-tx']
                        limit = stats[s_switch.name][n_switch.name]['link-speed-bits-per-second']
                        if(rec + tx < limit):
                            if  (s_switch.energyClass == 'low'):
                                cur_path_energy = cur_path_energy + LOW_ENERGY
                            elif(s_switch.energyClass == 'medium'):
                                cur_path_energy = cur_path_energy + MEDIUM_ENERGY
                            else:
                                cur_path_energy = cur_path_energy + HIGH_ENERGY
                        else:
                            cur_path_energy = cur_path_energy + HIGH_ENERGY

                    cur_switch = cur_path[len(cur_path)-1]
                    #print cur_switch
                    s_switch = self.topology.get(cur_switch)
                       
                    if  (s_switch.energyClass == 'low'):
                        cur_path_energy = cur_path_energy + LOW_ENERGY
                    elif(s_switch.energyClass == 'medium'):
                        cur_path_energy = cur_path_energy + MEDIUM_ENERGY
                    else:
                        cur_path_energy = cur_path_energy + HIGH_ENERGY
                            
                            
                    if(cur_path_energy < best):
                        second_best = best
                        second_best_path = best_path 
                        best = cur_path_energy
                        best_path = probable_paths[i]

                #print best_path
                #print second_best_path
                routes['enhancement'] = [best_path]
        return routes         

