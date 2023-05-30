import json
from graphviz import Digraph

def EpsilonClosure(state,states):
    isFinal = 'NOSTATE'
    statesStack=[]
    Eclosure=[]
    Eclosure.append(state)
    statesStack.append(state)
    while len(statesStack) >0:
        currState=statesStack.pop()
        for key in states[currState]:
            if key=='E':
                for s in states[currState][key]:
                    if s not in Eclosure:
                        Eclosure.append(s)
                        statesStack.append(s)
    return Eclosure,isFinal


def subsetConstruction(initialState,transitions,inputs,finalState):
    markedstates=dict()
    unmarkedstates=[]
    unmarkedstates.append(EpsilonClosure(initialState,transitions))
    while len(unmarkedstates)>0:
        states,_=unmarkedstates.pop(0)
        stateName=",".join([str(item) for item in states])
        markedstates[stateName]={}
        for input in inputs:
            newdfastate=[]
            for s in states:
                for key in transitions[s]:
                    if key==input:
                        newnfastate=transitions[s][input]
                        for st in newnfastate:
                            ret=EpsilonClosure(st,transitions)
                            newdfastate+=ret[0]
                        break
            if len(newdfastate)!=0:
                dfastateName=",".join([str(item) for item in newdfastate])
                if input not in markedstates[stateName]:
                    markedstates[stateName][input]=dfastateName
                else:
                    markedstates[stateName][input][0].join(','+dfastateName)
                if  newdfastate not in unmarkedstates and dfastateName not in markedstates:
                    unmarkedstates.append((newdfastate,ret[1]))
            if 'isTerminating' not in markedstates[stateName]:
                markedstates[stateName]['isTerminating']=(finalState in stateName)
    markedstates['StartingState']=",".join([str(item) for item in EpsilonClosure(initialState,transitions)[0]])
    return markedstates

def map_state_to_partion(state,partitions):
    for partition in partitions:
        if state in partition:
            return partitions.index(partition)

# to minimize the DFA apply the partitioning algorithm
def minimizeDFA(dfa,inputs):
    # get the states in the dfa
    # get the final states in the dfa
    # get the non-final states in the dfa
    non_final_states = []
    final_states = []
    states = []
    for key in dfa:
        if key != 'StartingState':
            states.append(key)
            if dfa[key]['isTerminating'] == True:
                final_states.append(key)
            elif dfa[key]['isTerminating'] == False:
                non_final_states.append(key)
    # create a partitions list
    partitions = []
    partitions.append(final_states)
    partitions.append(non_final_states)
    to_partition = True
    while to_partition == True and (len(partitions) != len(states)):
            old_partitions = partitions.copy()
            for partition in partitions:
                if len(partition)!=1:
                    for input in inputs:
                        used_partions_index ={}
                        for state in partition:
                            if input in dfa[state]:
                                index = map_state_to_partion(dfa[state][input],partitions)
                                if index not in used_partions_index:
                                    used_partions_index[index] = [state]
                                else:
                                    used_partions_index[index].append(state)
                            else:
                                if '-1' not in used_partions_index:
                                    used_partions_index['-1'] = [state]
                                else:
                                    used_partions_index['-1'].append(state)
                        if len(used_partions_index) > 1:
                            partitions.remove(partition)
                            for value in used_partions_index.values():
                                partitions.append(value)
                            break
            if old_partitions == partitions:
                to_partition = False
    new_dfa = {}
    for key,value in dfa.items():
        if key != 'StartingState':
            index = map_state_to_partion(key,partitions)
            new_dfa['s'+str(index)] ={}
            for input, next_state in value.items():
                if input != 'isTerminating':
                    new_dfa['s'+str(index)][input] = 's'+str(map_state_to_partion(next_state,partitions))
                else:
                    new_dfa['s'+str(index)]['isTerminating'] = value[input]
        else:
            new_dfa['StartingState'] = 's'+str(map_state_to_partion(value,partitions))
    return new_dfa

# draw nfa using graphviz 
def draw_dfa(dfa):
    graph = Digraph()
    for key,value in dfa.items():
        if key != 'StartingState':
            for key1,value1 in value.items():
                if key1 != 'isTerminating':
                    graph.edge(key,value1,label=key1)
                else:
                    if value1 == True:
                        graph.node(key,shape='doublecircle')
                    else:
                        graph.node(key,shape='circle')
        else:
            graph.node(value,shape='square')
    graph.render('dfa',view=True)
                            
############################################################################################################
f= open ('sample.json')
states = json.load(f)
f.close()
newstates=dict()

#getting all the inputs available in the diagram
allinputs=set()
for state in states:
    if state !='StartingState':
        for input in states[state]:
            if input!='E' and input!='isTerminating':
                allinputs.add(input)
            elif input=='isTerminating':
                if states[state][input]==True:
                    finalState = state

nfaInitialState=states['StartingState']
dfa=subsetConstruction(nfaInitialState,states,allinputs,finalState)
minimumDFA=minimizeDFA(dfa,allinputs)
# Serializing json
json_object = json.dumps(minimumDFA, indent=5)
# Writing to sample.json
with open("DFA.json", "w") as outfile:
    outfile.write(json_object)
outfile.close()
draw_dfa(minimumDFA)

