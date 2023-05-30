import re
import itertools
import json
from graphviz import Digraph


#pattern is a string containing the pattern pattern
#pattern = "(([A-B])|C)[A-Z])+"
#pattern = "(((a((a|b)*))b)[a-z])"

# find square brackets in a string
def find_square_brackets(string):
    list_of_square_brackets = []
    while(string.find("[")!=-1):
        # find the first square bracket
        first_square_bracket = string.find("[")
        # find the first square bracket
        last_square_bracket = string.find("]")
        list_of_square_brackets.append(string[first_square_bracket:last_square_bracket + 1])
        string = string.replace(string[first_square_bracket:last_square_bracket + 1],"(X)",1)
    return string,list_of_square_brackets


def concatenation_replace(pattern):
    afterat = []
    for i in range(len(pattern)-1):
        if((pattern[i].isalpha() | pattern[i].isdigit() | (pattern[i] == ')') | (pattern[i] == '*') | (pattern[i] == '+') |(pattern[i] in '?:/$_.')) and ((i == len(pattern)-1) or ((pattern[i+1] != '|') and (pattern[i+1] != '+') and (pattern[i+1] != '*') and (pattern[i+1] != ')') and (pattern[i+1] != '?')))):
            afterat.append(pattern[i])
            afterat.append('@')
        else:
            afterat.append(pattern[i])
    afterat.append(pattern[len(pattern)-1])
    return ''.join(afterat)


#Converting Regular Expressions to Postfix Notation with the Shunting-Yard Algorithm
def shunting_yard(pattern):
    # the operator stack
    opstack = []
    # the postfix list
    postfix = []
    # the operator precedence
    prec = {'*': 100, '+': 100 ,'@':70,'|':60,')': 40, '(': 20}
    # loop through the pattern
    for c in pattern:
        if c == '(':
            opstack.append(c)
        elif c == ')':
            while opstack[-1] != '(':
                postfix.append(opstack.pop())
            opstack.pop()
        elif c in prec:
            while opstack and prec[c] <= prec[opstack[-1]]:
                postfix.append(opstack.pop())
            opstack.append(c)
        else:
            postfix.append(c)
    while opstack:
        postfix.append(opstack.pop())
    return ''.join(postfix)

#######################################################

#Converting Postfix Notation to NFA
class State:
    id_obj = itertools.count()
    edges = {} # label -> state
    # Constructor for the state
    def __init__(self,edges):
        self.id = next(State.id_obj)
        self.edges=edges

# An NFA is represented by its initial and accept states.
class my_NFA:
    initial = None
    accept = None
 
    # Constructor for the NFA
    def __init__(self, initial, accept):
        self.initial = initial
        self.accept = accept

# Create a new instance of the NFA class
def compile(postfix,list_of_square_inputs):
    nfastack = []
    x_counter =0
    for c in postfix:
        if c == '|':
            # Pop two NFA's off the stack
            nfa2 = nfastack.pop()
            nfa1 = nfastack.pop()
            # Create a new initial state, connect it to initial states of the two NFA's popped from the stack
            initial = State({'E':[nfa1.initial,nfa2.initial]})
            # Create a new accept state, connecting the accept states of the two NFA's popped from the stack, to the new state
            accept = State({'E':list()})
            nfa1.accept.edges['E'].append(accept)
            nfa2.accept.edges['E'].append(accept)
            # Push new NFA to the stack
            newnfa = my_NFA(initial, accept)
            nfastack.append(newnfa)
        elif c == '*':
            # Pop a single NFA from the stack
            nfa = nfastack.pop()
            # Create a new initial state, connect it to the initial state of the NFA popped from the stack and the new accept state
            initial = State(edges={'E':[nfa.initial,nfa.accept]})
            # Create a new accept state, connecting it to the initial state and the new accept state
            accept = State(edges={'E':[nfa.initial]})
            nfa.accept.edges['E']=[accept]
            # Push new NFA to the stack
            newnfa = my_NFA(initial, accept)
            nfastack.append(newnfa)
        elif c == '?':
            # Pop two NFA's off the stack
            nfa2 = nfastack.pop()
            accept1 = State({'E':list()})
            initial1 = State({'E': [accept1]})
            # Create new NFA instance and push it to the stack
            nfa1 = my_NFA(initial1, accept1)
            # Create a new initial state, connect it to initial states of the two NFA's popped from the stack
            initial = State({'E':[nfa1.initial,nfa2.initial]})
            # Create a new accept state, connecting the accept states of the two NFA's popped from the stack, to the new state
            accept = State({'E':list()})
            nfa1.accept.edges['E']=[accept]
            nfa2.accept.edges['E']=[accept]
            # Push new NFA to the stack
            newnfa = my_NFA(initial, accept)
            nfastack.append(newnfa)
        elif c == '@':
            # Pop two NFA's off the stack
            nfa2 = nfastack.pop()
            nfa1 = nfastack.pop()
            # Connect first NFA's accept state to the second's initial state
            nfa1.accept.edges['E'].append(nfa2.initial)
            # Push NFA to the stack
            newnfa = my_NFA(nfa1.initial, nfa2.accept)
            nfastack.append(newnfa)
        elif c == '+':
            # Pop a single NFA from the stack
            nfa = nfastack.pop()
            # Create a new initial state, connect it to the initial state of the NFA popped from the stack
            initial = State({'E':[nfa.initial]})
            # Create a new accept state, connecting it to the initial state and the new accept state
            accept = State({'E':list()})
            nfa.accept.edges['E'].append(accept)
            nfa.accept.edges['E'].append(initial)
            # Push new NFA to the stack
            newnfa = my_NFA(initial, accept)
            nfastack.append(newnfa)
        else:
            if c == 'X': 
                c = list_of_square_inputs[x_counter]
                x_counter += 1
            accept = State({'E':list()})
            initial = State({c: [accept]})
            # Create new NFA instance and push it to the stack
            nfastack.append(my_NFA(initial, accept))
    return nfastack.pop()

# create a transition dictionary for the nfa
def transition(nfa):
    transition = {}
    states = []
    states.append(nfa.initial)
    for state in states:
        for _,values in state.edges.items():
            for value in values:
                if value not in states:
                    states.append(value)
    for state in states:
        transition['s'+str(state.id)] = {}
        for key,values in state.edges.items():
            if key not in transition['s'+str(state.id)]:
                transition['s'+str(state.id)][key] = []
            for value in values:
                transition['s'+str(state.id)][key].append('s'+str(value.id))
    return transition

############################################################################################################
# draw nfa using graphviz 
def draw_nfa(transitions,initial,accepting):
    graph = Digraph()
    initial_state = 's'+str(initial)
    graph.node(initial_state , shape='square')
    Accepting_state = 's'+str(accepting)
    graph.node(Accepting_state, shape='doublecircle')
    # loop through the states
    for key,values in transitions.items():
        if key != initial_state and key != Accepting_state:
            graph.node(key,shape = 'circle')
        for key1,values1 in values.items():
            for value1 in values1:
                graph.edge(key,value1,label=key1)
    graph.render('nfa',view=True)
# setup for json file
def prepare_for_json(transitions,initial,accepting):
    transitions['StartingState'] = 's'+str(initial)
    transitions['s'+str(accepting)]['isTerminating'] = True
    for key,_ in transitions.items():
        if key != 'StartingState' and key != 's'+str(accepting):
            transitions[key]['isTerminating'] = False
    return transitions

############################################################################################################


# prompt user for a regular expression
pattern = '(a|b)*bc+'

#pattern = "https?://(www.)?[a-zA-Z0-9-_].(com|org|net)"
try:
    re.compile(pattern)

except re.error:
    print("Non valid pattern pattern")
    exit()

test,list_of_square_inputs =find_square_brackets(pattern)
print(list_of_square_inputs)
test1=concatenation_replace(test)

test2=shunting_yard(test1)
print(test2)

nfa = compile(test2,list_of_square_inputs)
transitions= transition(nfa)
draw_nfa(transitions,nfa.initial.id,nfa.accept.id)
to_json = prepare_for_json(transitions,nfa.initial.id,nfa.accept.id)
# Serializing json
json_object = json.dumps(to_json, indent=5)

# Writing to sample.json
with open("sample.json", "w") as outfile:
    outfile.write(json_object)

def main(pattern):
    try:
        re.compile(pattern)

    except re.error:
        print("Non valid pattern pattern")
        exit()
    test,list_of_square_inputs =find_square_brackets(pattern)
    test1=concatenation_replace(test)
    test2=shunting_yard(test1)
    nfa = compile(test2,list_of_square_inputs)
    transitions= transition(nfa)
    draw_nfa(transitions,nfa.initial.id,nfa.accept.id)
    to_json = prepare_for_json(transitions,nfa.initial.id,nfa.accept.id)
    # Serializing json
    json_object = json.dumps(to_json, indent=5)
    # Writing to sample.json
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)

