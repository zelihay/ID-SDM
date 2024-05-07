import pyAgrum as gum
import pyAgrum.lib.notebook as gnb
import pyAgrum.lib.image as gimg
import math
import random
import numpy as np
from IPython.display import Image
from graphviz import Source
from itertools import product
import copy
import pandas as pd
import pyAgrum.lib.ipython as gnb




def update_decision_node_options(student_model, advisor_model):

    student_decision_node_id = next(node for node in student_model.nodes() if student_model.isDecisionNode(node))
    advisor_decision_node_id = next(node for node in advisor_model.nodes() if advisor_model.isDecisionNode(node))

    student_decision_node_name = student_model.variable(student_decision_node_id).name()
    advisor_decision_node_name = advisor_model.variable(advisor_decision_node_id).name()

    student_options = student_model.variable(student_decision_node_name).labels()
    advisor_options = advisor_model.variable(advisor_decision_node_name).labels()
 
    missing_options = [option for option in advisor_options if option not in student_options]    
    
    children_of_decision_node = [child for child in student_model.children(student_decision_node_id)]

    original_cpts = {}
    for child in children_of_decision_node:
        original_cpts[child] = student_model.cpt(child).tolist()

    if missing_options:        
        student_model.erase(student_decision_node_name)

        all_options = list(student_options) + missing_options
        updated_decision_var = gum.LabelizedVariable(student_decision_node_name, 'Decision Node', all_options)
        student_model.addDecisionNode(updated_decision_var)
        
        for child in children_of_decision_node:
            student_model.addArc(student_decision_node_name, student_model.variable(child).name())
            
            
            for idx, option in enumerate(student_options):
                student_model.cpt(child)[{student_decision_node_name: option}] = original_cpts[child][idx]

    return student_model, student_decision_node_name

def update_decision_node_options2(student_model, advisor_model):

    student_decision_node_id = next(node for node in student_model.nodes() if student_model.isDecisionNode(node))
    advisor_decision_node_id = next(node for node in advisor_model.nodes() if advisor_model.isDecisionNode(node))

    student_decision_node_name = student_model.variable(student_decision_node_id).name()
    advisor_decision_node_name = advisor_model.variable(advisor_decision_node_id).name()
    
    student_options = student_model.variable(student_decision_node_name).labels()
    advisor_options = advisor_model.variable(advisor_decision_node_name).labels()
    
    missing_options = [option for option in advisor_options if option not in student_options]    
    
    children_of_decision_node = [child for child in student_model.children(student_decision_node_id)]
   
    if missing_options:
        
        student_model.erase(student_decision_node_name)

        
        all_options = list(student_options) + missing_options
        updated_decision_var = gum.LabelizedVariable(student_decision_node_name, 'Decision Node', all_options)
        student_model.addDecisionNode(updated_decision_var)

               
    return student_model, student_decision_node_name


def add_nodes_from_advisor_to_student(student_model, advisor_model):
    
    interaction_counter = 0
    
    advisor_nodes = set(filter(lambda node: not advisor_model.isUtilityNode(node), advisor_model.names()))    
    student_nodes = set(student_model.names())
    
    unmatched_nodes_advisor = advisor_nodes - student_nodes
    
    for node in unmatched_nodes_advisor:
        if not advisor_model.isUtilityNode(node): 
            node_info = advisor_model.variableFromName(node)            
            
            student_model.add(node_info)  
            
            interaction_counter += 1

    #print(f"Total interactions made: {interaction_counter}")
    return student_model, interaction_counter, unmatched_nodes_advisor

# print("Nodes in the updated student model:")
# for node_name in student_model.names():
#      print(node_name)

def add_equal_probabilities_for_new_option(student_model):
    
    decision_node_id = next(node for node in student_model.nodes() if student_model.isDecisionNode(node))
    decision_node_name = student_model.variable(decision_node_id).name()    
    
    all_decision_states = student_model.variable(decision_node_id).labels()    
    new_decision_state = all_decision_states[-1]        
    children_of_decision = student_model.children(decision_node_id)        
    for child_id in children_of_decision:
        child_name = student_model.variable(child_id).name()        
        
        if not student_model.isUtilityNode(child_id):
            child_labels = student_model.variable(child_id).labels()
            
            num_labels = len(child_labels)            
            equal_prob = 1.0 / num_labels
            
            equal_probs = [equal_prob] * num_labels
            
            try:                
                student_model.cpt(child_name)[{decision_node_name: new_decision_state}] = equal_probs
            except Exception as e:
                
                print(f"Error updating CPT for {child_name}: {e}")
                pass


def get_utility_parents(influence_diagram):
    utility_node_id = [node for node in influence_diagram.names() if influence_diagram.isUtilityNode(node)]

    if not utility_node_id:
        return []  

    utility_node_id = utility_node_id[0]  

    parents = []
    for parent_id in influence_diagram.parents(utility_node_id):
        parent_name = influence_diagram.variable(parent_id).name()
        parents.append(parent_name)

    return parents

def get_parents_of_matched_parents(matched_parents, model):
    parents_of_matched_parents = {}

    for parent_name in matched_parents:
        parent_id = model.idFromName(parent_name)
        parent_parents = [model.variable(parent_id).name() for parent_id in model.parents(parent_id)]
        parents_of_matched_parents[parent_name] = parent_parents

    return parents_of_matched_parents
   
    
def add_nodes_from_student_to_advisorORJ(advisor_model, student_model):
    interaction_counter = 0
    
    advisor_nodes = set(filter(lambda node: not advisor_model.isUtilityNode(node), advisor_model.names()))
    student_nodes = set(student_model.names())
    
    unmatched_nodes_student = student_nodes - advisor_nodes  
    
    for node in unmatched_nodes_student:
        if not student_model.isUtilityNode(node):   
            node_info = student_model.variableFromName(node)
            
            advisor_model.add(node_info)  

            interaction_counter += 1

    return advisor_model, interaction_counter, unmatched_nodes_student


def add_nodes_from_student_to_advisor(advisor_model, student_model):
    advisor_nodes = set(filter(lambda node: not advisor_model.isUtilityNode(node), advisor_model.names()))
    student_nodes = set(student_model.names())
    
    unmatched_nodes_student = student_nodes - advisor_nodes  
    
    # Find parent nodes of the utility node in the student model
    utility_node_name = next(node for node in student_model.names() if student_model.isUtilityNode(node))
    utility_node_id = student_model.idFromName(utility_node_name)
    parent_ids = student_model.parents(utility_node_id)
    parent_names = [student_model.variable(id).name() for id in parent_ids]
    
    # Include nodes related to any parent nodes of the utility node
    for parent_name in parent_names:
        related_nodes = set(student_model.children(student_model.idFromName(parent_name))) - advisor_nodes
        unmatched_nodes_student |= related_nodes
    
    # Add unmatched nodes to the advisor model
    for node in unmatched_nodes_student:
        if not student_model.isUtilityNode(node):
            if node not in advisor_model.names():  # Check if node label already exists in advisor model
                node_info = student_model.variableFromName(node)
                advisor_model.add(node_info)

    return advisor_model






def add_decision_related_arcs_from_advisor_to_student(advisor_model, student_model):
    
    advisor_decision_node = [node for node in advisor_model.names() if advisor_model.isDecisionNode(node)][0]
    student_decision_node = [node for node in student_model.names() if student_model.isDecisionNode(node)][0]

    
    for child_id in advisor_model.children(advisor_decision_node):
        child_name = advisor_model.variable(child_id).name()
        if child_name in student_model.names() and not student_model.existsArc(student_decision_node, child_name):
            student_model.addArc(student_decision_node, child_name)
            #print(f"Added arc from {student_decision_node} to {child_name} in student's model")
    
    for parent_id in advisor_model.parents(advisor_decision_node):
        parent_name = advisor_model.variable(parent_id).name()
        if parent_name in student_model.names() and not student_model.existsArc(parent_name, student_decision_node):
            student_model.addArc(parent_name, student_decision_node)
       #     print(f"Added arc from {parent_name} to {student_decision_node} in student's model")

    return student_model



def add_decision_related_arcs_from_student_to_advisor2(student_model, advisor_model):
    
    student_decision_node = [node for node in student_model.names() if student_model.isDecisionNode(node)][0]
    advisor_decision_node = [node for node in advisor_model.names() if advisor_model.isDecisionNode(node)][0]
    
    for child_id in student_model.children(student_decision_node):
        child_name = student_model.variable(child_id).name()
        if child_name in advisor_model.names() and not advisor_model.existsArc(advisor_decision_node, child_name):
            advisor_model.addArc(advisor_decision_node, child_name)
            #print(f"Added arc from {advisor_decision_node} to {child_name} in advisor's model")
    
    for parent_id in student_model.parents(student_decision_node):
        parent_name = student_model.variable(parent_id).name()
        if parent_name in advisor_model.names() and not advisor_model.existsArc(parent_name, advisor_decision_node):
            advisor_model.addArc(parent_name, advisor_decision_node)
            #print(f"Added arc from {parent_name} to {advisor_decision_node} in advisor's model")

    return advisor_model
    

def add_utility_related_arcs_from_advisor_to_studentORJ(advisor_model, student_model):

    advisor_utility_node = [node for node in advisor_model.names() if advisor_model.isUtilityNode(node)][0]
    student_utility_node = [node for node in student_model.names() if student_model.isUtilityNode(node)][0]

    for child_id in advisor_model.children(advisor_utility_node):
        child_name = advisor_model.variable(child_id).name()
        if child_name in student_model.names() and not student_model.existsArc(student_utility_node, child_name):
            student_model.addArc(student_utility_node, child_name)
       #     print(f"Added arc from {student_utility_node} to {child_name} in student's model")


    for parent_id in advisor_model.parents(advisor_utility_node):
        parent_name = advisor_model.variable(parent_id).name()
        if parent_name in student_model.names() and not student_model.existsArc(parent_name, student_utility_node):
            student_model.addArc(parent_name, student_utility_node)
          #  print(f"Added arc from {parent_name} to {student_utility_node} in student's model")

    return student_model


def add_utility_related_arcs_from_advisor_to_student(advisor_model, student_model):
    advisor_utility_node_name = next(node for node in advisor_model.names() if advisor_model.isUtilityNode(node))
    student_utility_node_name = next(node for node in student_model.names() if student_model.isUtilityNode(node))

    advisor_utility_node_id = advisor_model.idFromName(advisor_utility_node_name)
    student_utility_node_id = student_model.idFromName(student_utility_node_name)

    # Add arcs from unmatched utility parents in advisor model to utility node in student model
    for parent_id in advisor_model.parents(advisor_utility_node_id):
        parent_name = advisor_model.variable(parent_id).name()
        if parent_name in student_model.names():
            parent_id_student = student_model.idFromName(parent_name)
            if not student_model.existsArc(parent_id_student, student_utility_node_id):
                student_model.addArc(parent_id_student, student_utility_node_id)

    # Add arcs from utility node in advisor model to unmatched children in student model
    for child_id in advisor_model.children(advisor_utility_node_id):
        child_name = advisor_model.variable(child_id).name()
        if child_name in student_model.names():
            child_id_student = student_model.idFromName(child_name)
            if not student_model.existsArc(student_utility_node_id, child_id_student):
                student_model.addArc(student_utility_node_id, child_id_student)

    return student_model




def add_utility_related_arcs_from_student_to_advisorORJ(student_model, advisor_model):

    student_utility_node = [node for node in student_model.names() if student_model.isUtilityNode(node)][0]
    advisor_utility_node = [node for node in advisor_model.names() if advisor_model.isUtilityNode(node)][0]

    for child_id in student_model.children(student_utility_node):
        child_name = student_model.variable(child_id).name()
        if child_name in advisor_model.names() and not advisor_model.existsArc(advisor_utility_node, child_name):
            advisor_model.addArc(advisor_utility_node, child_name)
          #  print(f"Added arc from {advisor_utility_node} to {child_name} in advisor's model")


    for parent_id in student_model.parents(student_utility_node):
        parent_name = student_model.variable(parent_id).name()
        if parent_name in advisor_model.names() and not advisor_model.existsArc(parent_name, advisor_utility_node):
            advisor_model.addArc(parent_name, advisor_utility_node)
         #   print(f"Added arc from {parent_name} to {advisor_utility_node} in advisor's model")

    return advisor_model


def add_utility_related_arcs_from_student_to_advisor(student_model, advisor_model):
    student_utility_node_name = next(node for node in student_model.names() if student_model.isUtilityNode(node))
    advisor_utility_node_name = next(node for node in advisor_model.names() if advisor_model.isUtilityNode(node))

    student_utility_node_id = student_model.idFromName(student_utility_node_name)
    advisor_utility_node_id = advisor_model.idFromName(advisor_utility_node_name)

    # Add arcs from unmatched utility parents in student model to utility node in advisor model
    for parent_id in student_model.parents(student_utility_node_id):
        parent_name = student_model.variable(parent_id).name()
        if parent_name in advisor_model.names():
            parent_id_advisor = advisor_model.idFromName(parent_name)
            if not advisor_model.existsArc(parent_id_advisor, advisor_utility_node_id):
                advisor_model.addArc(parent_id_advisor, advisor_utility_node_id)

    # Add arcs from utility node in student model to unmatched children in advisor model
    for child_id in student_model.children(student_utility_node_id):
        child_name = student_model.variable(child_id).name()
        if child_name in advisor_model.names():
            child_id_advisor = advisor_model.idFromName(child_name)
            if not advisor_model.existsArc(advisor_utility_node_id, child_id_advisor):
                advisor_model.addArc(advisor_utility_node_id, child_id_advisor)

    return advisor_model


def add_chance_related_arcs_from_advisor_to_student(advisor_model, student_model):
    for node in advisor_model.names():
        if advisor_model.isChanceNode(node) and node in student_model.names():
            for parent_id in advisor_model.parents(advisor_model.idFromName(node)):
                parent_name = advisor_model.variable(parent_id).name()
                
                if parent_name in student_model.names() and not student_model.existsArc(parent_name, node):
                    student_model.addArc(parent_name, node)
               #     print(f"Added arc from {parent_name} to {node} in student's model")
    
    return student_model
    

def add_chance_related_arcs_from_student_to_advisorORJ(student_model, advisor_model):
    for node in student_model.names():
        if student_model.isChanceNode(node) and node in advisor_model.names():
            for parent_id in student_model.parents(student_model.idFromName(node)):
                parent_name = student_model.variable(parent_id).name()
                
                if parent_name in advisor_model.names() and not advisor_model.existsArc(parent_name, node):
                    advisor_model.addArc(parent_name, node)
               #     print(f"Added arc from {parent_name} to {node} in advisor's model")
    
    return advisor_model


def add_chance_related_arcs_from_student_to_advisor(student_model, advisor_model):
    student_utility_node = next(node for node in student_model.names() if student_model.isUtilityNode(node))
    advisor_utility_node = next(node for node in advisor_model.names() if advisor_model.isUtilityNode(node))

    for node in student_model.names():
        if student_model.isChanceNode(node) and node in advisor_model.names():
            for parent_id in student_model.parents(student_model.idFromName(node)):
                parent_name = student_model.variable(parent_id).name()

                if parent_name != student_utility_node:  # Exclude arcs leading to the utility node itself
                    if parent_name not in student_model.parents(student_model.idFromName(student_utility_node)):
                        if parent_name in advisor_model.names() and not advisor_model.existsArc(parent_name, node):
                            advisor_model.addArc(parent_name, node)

    return advisor_model



def remove_unwanted_arcs(advisor_model, student_model, matched_parents):
    student_utility_node = next(node for node in student_model.names() if student_model.isUtilityNode(node))
    advisor_utility_node = next(node for node in advisor_model.names() if advisor_model.isUtilityNode(node))

    for parent_id in student_model.parents(student_model.idFromName(student_utility_node)):
        parent_name = student_model.variable(parent_id).name()
        if parent_name in matched_parents:
            # Check if the parent node itself has any parents in the student model
            grandparent_ids_student = student_model.parents(parent_id)
            for grandparent_id_student in grandparent_ids_student:
                grandparent_name_student = student_model.variable(grandparent_id_student).name()
                # Check if the grandparent node exists in the advisor model
                grandparent_ids_advisor = advisor_model.parents(advisor_model.idFromName(parent_name))
                grandparent_names_advisor = [advisor_model.variable(id).name() for id in grandparent_ids_advisor]
                for grandparent_name_advisor in grandparent_names_advisor:
                    if grandparent_name_advisor not in grandparent_name_student:
                        # Remove the arc between the grandparent node and the parent node
                        advisor_model.eraseArc(grandparent_name_advisor, parent_name)

            # Check the arc between the parent node and the utility node in the student model
            if not advisor_model.existsArc(parent_name, advisor_utility_node):
                advisor_model.eraseArc(parent_name, advisor_utility_node)

    return advisor_model






###----FUNCTIONS TO GET CPTs ------------

def list_cpts_of_model(model):
    cpt_dict = {}

    for node in model.nodes():
        if model.isChanceNode(node):
            node_name = model.variable(node).name()
            cpt = model.cpt(node).tolist()

            # Create a human-readable format for the CPT
            formatted_cpt = []
            domain_sizes = model.cpt(node).names()
            formatted_cpt.append(domain_sizes)
            for idx, p in enumerate(cpt):
                values = model.cpt(node).var(*domain_sizes, idx)  # Use * to unpack the tuple
                formatted_cpt.append([values] + [f"{prob:.4f}" for prob in p])

            cpt_dict[node_name] = formatted_cpt

    return cpt_dict




#student_cpts = list_cpts_of_model(student_model)
#print(student_cpts)

#advisor_cpts = list_cpts_of_model(advisor_model)
#print(advisor_cpts)


def list_unmatched_node_cpts(model, unmatched_nodes):
    cpt_list = {}

    for node in unmatched_nodes:
        if node in model.names():  # Check if node exists in the model
            # Ensure the node is a chance node and not a utility node
            if model.isChanceNode(node) and not model.isUtilityNode(node):
                cpt_list[node] = model.cpt(node).tolist()

    return cpt_list

#print(unmatched_cpts)

def add_noise_to_cpt(cpt_array, noise_factor=0.1):  
    noisy_cpt = cpt_array + noise_factor * np.random.randn(*cpt_array.shape)
    
    noisy_cpt = np.clip(noisy_cpt, 0, 1)
    
    sums = noisy_cpt.sum(axis=-1, keepdims=True)
    normalized_cpt = noisy_cpt / sums

    return normalized_cpt



def fill_student_cpts_with_noisy_data(student_model, advisor_model, unmatched_nodes, noise_factor=0.1):
    for node in unmatched_nodes:
        if advisor_model.isChanceNode(node) and not advisor_model.isUtilityNode(node):
            advisor_cpt = advisor_model.cpt(node)  
        
            noisy_cpt = add_noise_to_cpt(np.array(advisor_cpt.tolist()), noise_factor)                 
            
            student_model.cpt(node)[:] = noisy_cpt
    return student_model



def fill_advisor_cpts_with_noisy_data(advisor_model, student_model, unmatched_nodes, noise_factor=0.1):
    for node in unmatched_nodes:
        if student_model.isChanceNode(node) and not student_model.isUtilityNode(node):
            student_cpt = student_model.cpt(node)  
        
            noisy_cpt = add_noise_to_cpt(np.array(student_cpt.tolist()), noise_factor)                 
            
            advisor_model.cpt(node)[:] = noisy_cpt
    return advisor_model
    
    
def print_cpts_for_comparison(student_model, advisor_model, unmatched_nodes):
    
    #unmatched_chance_nodes = [node for node in unmatched_nodes if 
    #0                         not advisor_model.isUtilityNode(node) or 
    #                         not student_model.isUtilityNode(node)]

    for node_name in unmatched_nodes:
        advisor_cpt = advisor_model.cpt(node_name)
    
        student_cpt = student_model.cpt(node_name)
        
        print(f"Node: {node_name}")
        print("Advisor CPT:")
        print(advisor_cpt)
        print("\nStudent CPT:")
        print(student_cpt)
        print("--------")


def has_empty_cpts(model):

    for node in model.names():
        if model.isChanceNode(node):
            cpt = model.cpt(node)
            if cpt.max() == 0 and cpt.min() == 0:
                return True
    return False


#if has_empty_cpts(student_model):
#    print("The model has empty CPTs!")
#else:
#    print("All CPTs in the model are filled!")


def print_all_cpts(model):
    for node_name in model.names():
        if model.isChanceNode(node_name):
            print(f"CPT of {node_name}:")
            print(model.cpt(node_name))
            print("\n----------------------\n")


def print_all_utilitiesX(model):
    for node_name in model.names():
        if model.isUtilityNode(node_name):
            print(f"Utility of {node_name}:")
            print(model.utility(node_name))
            print("\n----------------------\n")


def show_decisions(limid):
    gnb.flow.row(limid.optimalDecision("course"),
                   f"$${limid.MEU()['mean']:5.3f}\\ (stdev : {math.sqrt(ie.MEU()['variance']):5.3f})$$",
                   captions=["Strategy for course",
                             "MEU and its standard deviation>"])


def get_utilities_as_dict_with_names(model):
    utilities_dict = {}    
    
    utility_node_name = next(node for node in model.nodes() if model.isUtilityNode(node))
    utility_table = model.utility(utility_node_name)
    
    instantiation = gum.Instantiation(utility_table)
    
    instantiation.setFirst()
    while not instantiation.end():
        
        current_vals = {}
        for i in range(instantiation.nbrDim()):
            variable = utility_table.variable(i)
            current_vals[variable.name()] = variable.label(instantiation[i])
        
        current_vals_without_utility = tuple(current_vals.items())[1:]

        utilities_dict[current_vals_without_utility] = utility_table[instantiation]
        instantiation.inc()

    return utilities_dict


def print_all_utilities(model):    
    utility_node_name = [node for node in model.nodes() if model.isUtilityNode(node)][0]
    utility_table = model.utility(utility_node_name)
    
    instantiation = gum.Instantiation(utility_table)
    instantiation.setFirst()
    
    while not instantiation.end():
        print(instantiation, "Utility:", utility_table[instantiation])
        instantiation.inc()

    return None

def print_all_utilitiesXX(model):    
    utility_node_name = [node for node in model.nodes() if model.isUtilityNode(node)][0]
    utility_table = model.utility(utility_node_name)
    
    instantiation = gum.Instantiation(utility_table)
    instantiation.setFirst()
    
    while not instantiation.end():        
        current_vals = {instantiation.variable(i).name(): instantiation.variable(i).label(instantiation[i]) 
                        for i in range(instantiation.nbrDim())}        
        
        print("<", end="")
        print(", ".join([f"{k}:{v}" for k, v in current_vals.items()]), end="")
        print(f"> Utility: {utility_table[instantiation]}")
        
        instantiation.inc()

    return None




def show_decisions(model):
    
    limid = gum.ShaferShenoyLIMIDInference(model)    
    dd = limid.toDD()    
    optimal_decision = dd.optimalDecision()    
    meu = dd.MEU(optimal_decision)    
    decision_str = f"Optimal Decision: {optimal_decision}"
    meu_str = f"MEU: {meu['mean']:.3f} (stdev: {math.sqrt(meu['variance']):.3f})"
    return f"{decision_str}\n{meu_str}"



## pool of CPTs for the new option


CPT1_difficulty = [
    0.5, 0.3, 0.2
]

CPT1_difficulty = [
    0.5, 0.3, 0.2
]

CPT1_friends = [
    0.31, 0.69
    
]

CPT1_interest = [
    0.6, 0.4
]

CPT2_difficulty = [    
    0.5, 0.4, 0.1
]

CPT2_friends = [  
    0.41, 0.59
]

CPT2_interest = [    
    0.4, 0.6
]

CPT3_difficulty = [    
    0.5, 0.4, 0.1
]

CPT3_friends = [    
    0.35, 0.65
]

CPT3_interest = [    
    0.3, 0.7
]

CPT4_difficulty = [    
    0.5, 0.4, 0.1
]

CPT4_friends = [    
    0.7, 0.3
]

CPT4_interest = [    
    0.7, 0.3
]

CPT5_difficulty = [    
    0.5, 0.4, 0.1
]

CPT5_friends = [   
    0.8, 0.2
]

CPT5_interest = [    
    0.8, 0.2
]




pool = {
    "difficulty": [CPT1_difficulty,CPT2_difficulty,CPT3_difficulty,CPT4_difficulty,CPT5_difficulty],
    "friends": [CPT1_friends,CPT2_friends,CPT3_friends,CPT4_friends,CPT5_friends],
    "interest": [CPT1_interest,CPT2_interest,CPT3_interest,CPT4_interest,CPT5_interest]
}



selected_cpt_difficulty = random.choice(pool["difficulty"])
selected_cpt_friends = random.choice(pool["friends"])
selected_cpt_interest = random.choice(pool["interest"])


def add_cpt_from_pool(student_model, selected_cpt_difficulty, selected_cpt_friends, selected_cpt_interest):
    student_model.cpt('difficulty')[{'course': 'Course3'}] = selected_cpt_difficulty
    student_model.cpt('friends')[{'course': 'Course3'}] = selected_cpt_friends
    student_model.cpt('interest')[{'course': 'Course3'}] = selected_cpt_interest


def perform_LIMID_inferenceXX(model, decision_node_name,):
        inference = gum.ShaferShenoyLIMIDInference(model)       
        inference.makeInference()
        optimal_decision = inference.optimalDecision(decision_node_name)
        return optimal_decision


import random

def calculate_and_set_utilities_StudentS(combined_model, weight_factor:None):
    utility_node_id = next(node for node in combined_model.nodes() if combined_model.isUtilityNode(node))
    combined_node_name = combined_model.variable(utility_node_id).name()    
    
    utilities = {}

    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for pre_val in ["Yes", "No"]:
                    for req_val in ["yes", "no"]:
                        for career_val in ["positive", "neutral", "negative"]:
                            u = 50 if int_val == "yes" else 5
                            v = 60 if fr_val == "yes" else 10
                            if grade_val == ">C":
                                y = 50
                            elif grade_val == "D":
                                y = 30
                            else:
                                y = 0
                            a = 50 if pre_val == "Yes" else 5
                            b = 60 if req_val == "yes" else 0
                            if career_val == "positive":
                                c = 50
                            elif career_val == "neutral":
                                c = 30
                            else:
                                c = 10
                            
                            # Introduce the weight factor
                            weight = random.uniform(-2, 2) if weight_factor is None else weight_factor                            
                            utilities[(int_val, grade_val, fr_val, pre_val, req_val, career_val)] = (0.04 * u + 0.06 * v + 0.1 * y) + (0.25 * weight * a + 0.35 * weight * b + 0.2 * weight * c)
    
    # Fill the utility node with the computed values
    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for pre_val in ["Yes", "No"]:
                    for req_val in ["yes", "no"]:
                        for career_val in ["positive", "neutral", "negative"]:
                            combined_model.utility(combined_node_name)[{'interest': int_val, 'Grade': grade_val, 'friends': fr_val, 'prerequisite': pre_val, 'requirement': req_val, 'career_development': career_val}] = utilities[(int_val, grade_val, fr_val, pre_val, req_val, career_val)]

    return combined_model, weight



def calculate_and_set_utilities_AdvisorS(combined_model, weight_factor:None):
    utility_node_id = next(node for node in combined_model.nodes() if combined_model.isUtilityNode(node))
    combined_node_name = combined_model.variable(utility_node_id).name()

            
    # Calculate and set utilities
    utilities = {}

    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for pre_val in ["Yes", "No"]:
                    for req_val in ["yes", "no"]:
                        for career_val in ["positive", "neutral", "negative"]:
                            u = 50 if int_val == "yes" else 5
                            v = 60 if fr_val == "yes" else 10
                            if grade_val == ">C":
                                y = 50
                            elif grade_val == "D":
                                y = 30
                            else:
                                y = 0
                            a = 50 if pre_val == "Yes" else 5
                            b = 60 if req_val == "yes" else 0
                            if career_val == "positive":
                                c = 50
                            elif career_val == "neutral":
                                c = 30
                            else:
                                c = 10

                            weight = random.uniform(-2, 2) if weight_factor is None else weight_factor
                            utilities[(int_val, grade_val, fr_val, pre_val, req_val, career_val)] = (0.04 * weight * u + 0.06 * weight * v + 0.1 * weight * y) + (0.25 * a + 0.35 * b + 0.2 * c)


    
    # Fill the utility node with the computed values
    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for pre_val in ["Yes", "No"]:
                    for req_val in ["yes", "no"]:
                        for career_val in ["positive", "neutral", "negative"]:
                            combined_model.utility(combined_node_name)[{'interest': int_val, 'Grade': grade_val, 'friends': fr_val, 'prerequisite': pre_val, 'requirement': req_val, 'career_development': career_val}] = utilities[(int_val, grade_val, fr_val, pre_val, req_val, career_val)]
    
        
    return combined_model, weight


def calculate_and_set_utilities_All(combined_model, weight_factor:None):
    utility_node_id = next(node for node in combined_model.nodes() if combined_model.isUtilityNode(node))
    combined_node_name = combined_model.variable(utility_node_id).name()    
    
    utilities = {}

    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for pre_val in ["Yes", "No"]:
                    for req_val in ["yes", "no"]:
                        for career_val in ["positive", "neutral", "negative"]:
                            u = 50 if int_val == "yes" else 5
                            v = 60 if fr_val == "yes" else 10
                            if grade_val == ">C":
                                y = 50
                            elif grade_val == "D":
                                y = 30
                            else:
                                y = 0
                            a = 50 if pre_val == "Yes" else 5
                            b = 60 if req_val == "yes" else 0
                            if career_val == "positive":
                                c = 50
                            elif career_val == "neutral":
                                c = 30
                            else:
                                c = 10                            
                            
                            weight = random.uniform(-2, 2) if weight_factor is None else weight_factor                            
                            utilities[(int_val, grade_val, fr_val, pre_val, req_val, career_val)] = (0.04 * u + 0.06 * v + 0.1 * y) + (0.25 * weight * a + 0.35 * weight * b + 0.2 * weight * c)    
    
    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for pre_val in ["Yes", "No"]:
                    for req_val in ["yes", "no"]:
                        for career_val in ["positive", "neutral", "negative"]:
                            combined_model.utility(combined_node_name)[{'interest': int_val, 'Grade': grade_val, 'friends': fr_val, 'prerequisite': pre_val, 'requirement': req_val, 'career_development': career_val}] = utilities[(int_val, grade_val, fr_val, pre_val, req_val, career_val)]

    return combined_model, weight
    
def calculate_utilities_for_states(model):    
    decision_node_id = next(node for node in model.nodes() if model.isDecisionNode(node))
    decision_node = model.variable(decision_node_id)
    
    limid = gum.ShaferShenoyLIMIDInference(model)    
    state_utilities = {}
    
    for state in decision_node.states():        
        limid.setEvidence({decision_node: state})
        
        meu = limid.MEU()
        
        state_utilities[state] = meu['mean']

    return state_utilities

def compare_decision_utilities(model1, model2):    
    decision_node_id_model1 = next(node for node in model1.nodes() if model1.isDecisionNode(node))
    decision_node_name_model1 = model1.variable(decision_node_id_model1).name()
    
    decision_node_id_model2 = next(node for node in model2.nodes() if model2.isDecisionNode(node))
    decision_node_name_model2 = model2.variable(decision_node_id_model2).name()

    utilities_model1 = calculate_utilities_for_states(model1)
    utilities_model2 = calculate_utilities_for_states(model2)

    partial_consensus_threshold = 0.1

    consensus = "Full Consensus"
    max_utility_states_model1 = {}
    max_utility_states_model2 = {}

    for state in decision_utilities_model1.keys():
        utility_model1 = decision_utilities_model1[state]
        utility_model2 = decision_utilities_model2.get(state, 0.0)

        if abs(utility_model1 - utility_model2) > partial_consensus_threshold:
            consensus = "Partial Consensus"

        if state not in max_utility_states_model1 or utility_model1 > max_utility_states_model1[state][0]:
            max_utility_states_model1[state] = (utility_model1, decision_node_name_model1)

        if state not in max_utility_states_model2 or utility_model2 > max_utility_states_model2[state][0]:
            max_utility_states_model2[state] = (utility_model2, decision_node_name_model2)

    print("Decision Utilities for Model 1:")
    for state, (utility, decision) in max_utility_states_model1.items():
        print(f"For {decision} {state}: {utility:.1f}")

    print("\nDecision Utilities for Model 2:")
    for state, (utility, decision) in max_utility_states_model2.items():
        print(f"For {decision} {state}: {utility:.1f}")

    print(f"\nLevel of consensus: {consensus}")

def show_decision_utilities(model):
    decision_node_id = next(node for node in model.nodes() if model.isDecisionNode(node))
    decision_node = model.variable(decision_node_id)

    limid = gum.ShaferShenoyLIMIDInference(model)

    state_utilities = {}
    
    decision_domain = decision_node.domain()

    states = decision_domain.strip('{}').split("|")
    
    for state in states:
        limid.setEvidence({decision_node.name(): state})
        limid.makeInference()  
        meu = limid.MEU()
        
        state_utilities[state] = meu['mean']

    return state_utilities

from prettytable import PrettyTable

def show_decision_utilities2(model):
    decision_node_id = next(node for node in model.nodes() if model.isDecisionNode(node))
    decision_node = model.variable(decision_node_id)

    limid = gum.ShaferShenoyLIMIDInference(model)

    state_utilities = {}
    max_expected_utility =0
    max_utility_state = None
    decision_domain = decision_node.domain()

    states = decision_domain.strip('{}').split("|")
    
    for state in states:
        limid.setEvidence({decision_node.name(): state})
        limid.makeInference()  
        meu = limid.MEU()
        
        state_utilities[state] = meu['mean']
        
        current_expected_utility = state_utilities[state]
        #print (current_expected_utility)
        if current_expected_utility > max_expected_utility:
            max_expected_utility = current_expected_utility
            max_utility_state = state

    return state_utilities,max_expected_utility,max_utility_state


import prettytable as pt

from prettytable import PrettyTable

def show_decision_utilities4(model):
    decision_node_id = next(node for node in model.nodes() if model.isDecisionNode(node))
    decision_node = model.variable(decision_node_id)

    limid = gum.ShaferShenoyLIMIDInference(model)

    state_utilities = {}
    max_expected_utility = 0
    max_utility_state = None
    decision_domain = decision_node.domain()

    states = decision_domain.strip('{}').split("|")
    
    for state in states:
        limid.setEvidence({decision_node.name(): state})
        limid.makeInference()  
        meu = limid.MEU()
        
        state_utilities[state] = meu['mean']
        
        current_expected_utility = state_utilities[state]
        if current_expected_utility > max_expected_utility:
            max_expected_utility = current_expected_utility
            max_utility_state = state

 # Create a pretty table for output
    table = PrettyTable()
    table.field_names = ["State", "Utility"]
    for state, utility in state_utilities.items():
        table.add_row([state, utility])

    output = table.get_string()
    output += f"\nMaximum Expected Utility: {max_expected_utility}, State: {max_utility_state}"

    return output

def show_decision_utilities3(model):
    decision_node_id = next(node for node in model.nodes() if model.isDecisionNode(node))
    decision_node = model.variable(decision_node_id)
    limid = gum.ShaferShenoyLIMIDInference(model)

    state_utilities = {}
    max_expected_utility = 0
    max_utility_state = None
    decision_domain = decision_node.domain()
    states = decision_domain.strip('{}').split("|")

    for state in states:
        limid.setEvidence({decision_node.name(): state})
        limid.makeInference()
        meu = limid.MEU()

        state_utilities[state] = meu['mean']

        current_expected_utility = state_utilities[state]
        if current_expected_utility > max_expected_utility:
            max_expected_utility = current_expected_utility
            max_utility_state = state

    return state_utilities, max_expected_utility, max_utility_state

from prettytable import PrettyTable

def compare_final_decisions(utilities_model1, utilities_model2, threshold=5):
    threshold = threshold if threshold is not None else 5
    result = PrettyTable()

    # Round the utility values and find the max utility states
    utilities_model1_rounded = {state: round(utility, 2) for state, utility in utilities_model1.items()}
    utilities_model2_rounded = {state: round(utility, 2) for state, utility in utilities_model2.items()}
    
    max_utility_state_model1 = max(utilities_model1_rounded.items(), key=lambda x: x[1])
    max_utility_state_model2 = max(utilities_model2_rounded.items(), key=lambda x: x[1])

    sorted_states_model1 = sorted(utilities_model1.items(), key=lambda x: x[1], reverse=True)
    sorted_states_model2 = sorted(utilities_model2.items(), key=lambda x: x[1], reverse=True)

    second_best_state_model1, second_best_utility_model1 = sorted_states_model1[1]
    second_best_state_model2, second_best_utility_model2 = sorted_states_model2[1]


    result.field_names = ["The Comparisons", "Result"]
    
    print("Student Model:", utilities_model1_rounded)
    print("Advisor Model:", utilities_model2_rounded)

    
    if max_utility_state_model1[0] == max_utility_state_model2[0]:
        result.add_row(["Max Utility Decisions", f"Student: {max_utility_state_model1}, Advisor: {max_utility_state_model2}"])
        result.add_row(["Result", "Full Consensus"])
    elif second_best_state_model1[0] == max_utility_state_model2[0] or max_utility_state_model1[0] == second_best_state_model2[0] or second_best_state_model1[0]==second_best_state_model2[0]:
        result.add_row(["Max Utility Decisions", f"Student: {max_utility_state_model1}, Advisor: {max_utility_state_model2}"])
        result.add_row(["Second Best Decision", f"Student: {second_best_state_model1}, Advisor: {second_best_state_model2}"])
        result.add_row(["Result", f"Partial Consensus"])
    else:
        result.add_row(["Max Utility Decisions", f"Student: {max_utility_state_model1}, Advisor: {max_utility_state_model2}"])
        result.add_row(["Second Best Decision", f"Student: {second_best_state_model1}, Advisor: {second_best_state_model2}"])
        result.add_row(["Result", "No Agreement"])


    return result





def compare_final_decisions_panda(utilities_model1, utilities_model2, threshold=None):
    threshold = threshold if threshold is not None else 5
    result_df = pd.DataFrame(columns=[
        "Final Decision of Student-State name",        
        "Final Decision of Student-Utility value",       
        "Final Decision of Advisor-State name",        
        "Final Decision of Advisor-Utility value",        
        "Second Best Decision (Min Difference State)",
        "Result"
    ])

    max_utility_state_model1, max_utility_value_model1 = max(utilities_model1.items(), key=lambda x: x[1])
    max_utility_state_model2, max_utility_value_model2 = max(utilities_model2.items(), key=lambda x: x[1])

    sorted_states_model1 = sorted(utilities_model1.items(), key=lambda x: x[1], reverse=True)
    sorted_states_model2 = sorted(utilities_model2.items(), key=lambda x: x[1], reverse=True)

# Get the second best state and its utility value
    second_best_state_model1, second_best_utility_model1 = sorted_states_model1[1]
    second_best_state_model2, second_best_utility_model2 = sorted_states_model2[1]


    #max_utility_state_model1 = max(utilities_model1, key=utilities_model1.get)
    #max_utility_state_model2 = max(utilities_model2, key=utilities_model2.get)

    
    differences = {state: abs(utilities_model1[state] - utilities_model2[state]) for state in utilities_model1}

    min_diff_state = min(differences, key=differences.get)
    min_diff_value = differences[min_diff_state]

    
    if max_utility_state_model1 == max_utility_state_model2:
        result_df.loc[0] = {
            "Final Decision of Student-State name": max_utility_state_model1,            
            "Final Decision of Student-Utility value": max_utility_value_model1,      
            "Final Decision of Advisor-State name": max_utility_state_model2,            
            "Final Decision of Advisor-Utility value": max_utility_value_model2,    
            "Second Best Decision(Min Difference State)":None,
            "Result": "Full Consensus"
        }
           

    if max_utility_state_model1 != max_utility_state_model2:    
        if min_diff_value < threshold:
            second_best_state = min_diff_state
            second_best_value = min_diff_value

            result_df.loc[0] = {
            "Final Decision of Student-State name": max_utility_state_model1,            
            "Final Decision of Student-Utility value": max_utility_value_model1,      
            "Final Decision of Advisor-State name": max_utility_state_model2,            
            "Final Decision of Advisor-Utility value": max_utility_value_model2,                 
                "Second Best Decision(Min Difference State)":second_best_state,
                "Result": f"Partial Consensus with {second_best_state}"
            }
        else:
            result_df.loc[0] = {
            "Final Decision of Student-State name": max_utility_state_model1,            
            "Final Decision of Student-Utility value": max_utility_value_model1,      
            "Final Decision of Advisor-State name": max_utility_state_model2,            
            "Final Decision of Advisor-Utility value": max_utility_value_model2,                 
                "Second Best Decision(Min Difference State)":None,
                "Result": "No Agreement"
            }

    return result_df

def compare_final_decisions_panda2(utilities_model1, utilities_model2, threshold=None):
    threshold = threshold if threshold is not None else 5
    result_df = pd.DataFrame(columns=[
        "Final Decision of Student-State name",        
        "Final Decision of Student-Utility value",       
        "Final Decision of Advisor-State name",        
        "Final Decision of Advisor-Utility value",       
        "Second Decision of Student-State name",        
        "Second Decision of Student-Utility value",       
        "Second Decision of Advisor-State name",        
        "Second Decision of Advisor-Utility value",    
        "Result"
    ])

    max_utility_state_model1, max_utility_value_model1 = max(utilities_model1.items(), key=lambda x: x[1])
    max_utility_state_model2, max_utility_value_model2 = max(utilities_model2.items(), key=lambda x: x[1])

    sorted_states_model1 = sorted(utilities_model1.items(), key=lambda x: x[1], reverse=True)
    sorted_states_model2 = sorted(utilities_model2.items(), key=lambda x: x[1], reverse=True)

# Get the second best state and its utility value
    second_best_state_model1, second_best_utility_model1 = sorted_states_model1[1]
    second_best_state_model2, second_best_utility_model2 = sorted_states_model2[1]


    #max_utility_state_model1 = max(utilities_model1, key=utilities_model1.get)
    #max_utility_state_model2 = max(utilities_model2, key=utilities_model2.get)

    
    differences = {state: abs(utilities_model1[state] - utilities_model2[state]) for state in utilities_model1}

    min_diff_state = min(differences, key=differences.get)
    min_diff_value = differences[min_diff_state]

    
    if max_utility_state_model1 == max_utility_state_model2:
        result_df.loc[0] = {
            "Final Decision of Student-State name": max_utility_state_model1,            
            "Final Decision of Student-Utility value": max_utility_value_model1,      
            "Final Decision of Advisor-State name": max_utility_state_model2,            
            "Final Decision of Advisor-Utility value": max_utility_value_model2,    
            "Second Decision of Student-State name": None,            
            "Second Decision of Student-Utility value": None,      
            "Second Decision of Advisor-State name": None,            
            "Second Decision of Advisor-Utility value": None,                
            "Result": "Full Consensus"
        }
           

    if max_utility_state_model1 != max_utility_state_model2:
        if (second_best_state_model1 == second_best_state_model2):    
            result_df.loc[0] = {
                "Final Decision of Student-State name": max_utility_state_model1,            
                "Final Decision of Student-Utility value": max_utility_value_model1,      
                "Final Decision of Advisor-State name": max_utility_state_model2,            
                "Final Decision of Advisor-Utility value": max_utility_value_model2,     
                "Second Decision of Student-State name": second_best_state_model1,            
                "Second Decision of Student-Utility value": second_best_utility_model1,      
                "Second Decision of Advisor-State name": second_best_state_model2,            
                "Second Decision of Advisor-Utility value": second_best_utility_model2,                             
                "Result": "Second Decision Agreement"
                }
    if max_utility_state_model1 != max_utility_state_model2:
        if (second_best_state_model1 != second_best_state_model2):
            result_df.loc[0] = {
                "Final Decision of Student-State name": max_utility_state_model1,            
                "Final Decision of Student-Utility value": max_utility_value_model1,      
                "Final Decision of Advisor-State name": max_utility_state_model2,            
                "Final Decision of Advisor-Utility value": max_utility_value_model2,  
                "Second Decision of Student-State name": second_best_state_model1,            
                "Second Decision of Student-Utility value": second_best_utility_model1,      
                "Second Decision of Advisor-State name": second_best_state_model2,            
                "Second Decision of Advisor-Utility value": second_best_utility_model2,  
                "Second Best Decision(Min Difference State)":None,
                "Result": "No Agreement"
                }

    return result_df


def compare_final_decisions_panda3(utilities_model1, utilities_model2, threshold=None):
    threshold = threshold if threshold is not None else 5
    result_df = pd.DataFrame(columns=[
        "Final Decision of Student-State name",        
        "Final Decision of Student-Utility value",       
        "Final Decision of Advisor-State name",        
        "Final Decision of Advisor-Utility value",       
        "Second Decision of Student-State name",        
        "Second Decision of Student-Utility value",       
        "Second Decision of Advisor-State name",        
        "Second Decision of Advisor-Utility value",    
        "Result"
    ])

    max_utility_state_model1, max_utility_value_model1 = max(utilities_model1.items(), key=lambda x: x[1])
    max_utility_state_model2, max_utility_value_model2 = max(utilities_model2.items(), key=lambda x: x[1])

    sorted_states_model1 = sorted(utilities_model1.items(), key=lambda x: x[1], reverse=True)
    sorted_states_model2 = sorted(utilities_model2.items(), key=lambda x: x[1], reverse=True)

    second_best_state_model1, second_best_utility_model1 = sorted_states_model1[1]
    second_best_state_model2, second_best_utility_model2 = sorted_states_model2[1]


    #max_utility_state_model1 = max(utilities_model1, key=utilities_model1.get)
    #max_utility_state_model2 = max(utilities_model2, key=utilities_model2.get)

    
    differences = {state: abs(utilities_model1[state] - utilities_model2[state]) for state in utilities_model1}

    min_diff_state = min(differences, key=differences.get)
    min_diff_value = differences[min_diff_state]


        
    if min_diff_value < threshold:
        result_df.loc[0] = {
            "Final Decision of Student-State name": max_utility_state_model1,            
            "Final Decision of Student-Utility value": max_utility_value_model1,      
            "Final Decision of Advisor-State name": max_utility_state_model2,            
            "Final Decision of Advisor-Utility value": max_utility_value_model2,    
            "Second Decision of Student-State name": None,            
            "Second Decision of Student-Utility value": None,      
            "Second Decision of Advisor-State name": None,            
            "Second Decision of Advisor-Utility value": None,                
            "Result": "Full Consensus"
        }
           

    if max_utility_state_model1 != max_utility_state_model2:
        if min_diff_value < threshold:    
            result_df.loc[0] = {
                "Final Decision of Student-State name": max_utility_state_model1,            
                "Final Decision of Student-Utility value": max_utility_value_model1,      
                "Final Decision of Advisor-State name": max_utility_state_model2,            
                "Final Decision of Advisor-Utility value": max_utility_value_model2,     
                "Second Decision of Student-State name": second_best_state_model1,            
                "Second Decision of Student-Utility value": second_best_utility_model1,      
                "Second Decision of Advisor-State name": second_best_state_model2,            
                "Second Decision of Advisor-Utility value": second_best_utility_model2,                             
                "Result": "Second Decision Agreement"
                }
    if max_utility_state_model1 != max_utility_state_model2:
        if second_best_state_model1 != second_best_state_model2:   
            result_df.loc[0] = {
                "Final Decision of Student-State name": max_utility_state_model1,            
                "Final Decision of Student-Utility value": max_utility_value_model1,      
                "Final Decision of Advisor-State name": max_utility_state_model2,            
                "Final Decision of Advisor-Utility value": max_utility_value_model2,  
                "Second Decision of Student-State name": second_best_state_model1,            
                "Second Decision of Student-Utility value": second_best_utility_model1,      
                "Second Decision of Advisor-State name": second_best_state_model2,            
                "Second Decision of Advisor-Utility value": second_best_utility_model2,  
                "Second Best Decision(Min Difference State)":None,
                "Result": "No Agreement"
                }

    return result_df
    
def calculate_initial_results(student_model, advisor_model, threshold):
    initial_utilities_model_student = show_decision_utilities(student_model)
    initial_utilities_model_advisor = show_decision_utilities(advisor_model)
    
    initial_result_df = compare_final_decisions_panda(
        initial_utilities_model_student,
        initial_utilities_model_advisor,
        threshold
    )

    return initial_result_df
    


def filter_chance_nodes(model, nodes_to_delete):

    

    for node_to_remove in nodes_to_delete:
        model.erase(node_to_remove)

    return model, nodes_to_delete

def filter_chance_nodes_ORJ(model, nodes_to_delete):

    utility_node_id = next(node for node in model.nodes() if model.isUtilityNode(node))
    utility_node_name = model.variable(utility_node_id).name()
    
    nodes_to_remove = []

    for node in nodes_to_delete:
            # Check if the chance node has arcs to the utility node
            has_arcs_to_utility = model.existsArc(node, utility_node_name)
            if has_arcs_to_utility:
                nodes_to_remove.append(node)

    for node_to_remove in nodes_to_remove:
        model.erase(node_to_remove)

    return model, nodes_to_remove
    
def combine_influence_diagrams(diagram1, diagram2):

    combined_diagram = gum.InfluenceDiagram()
    for node in diagram1.nodes():
        variable_info = diagram1.variable(node)
        if not diagram1.isDecisionNode(node) and not diagram1.isUtilityNode(node):
            combined_diagram.add(variable_info)

    for node in diagram2.nodes():
        variable_info = diagram2.variable(node)
        combined_diagram.add(variable_info)

    for arc in diagram1.arcs():
        combined_diagram.addArc(arc[0], arc[1])

    return combined_diagram


import random

def add_nodes_with_percentage(advisor_model, student_model, exchange_level):
    advisor_nodes = set(filter(lambda node: not advisor_model.isUtilityNode(node), advisor_model.names()))
    student_nodes = set(student_model.names())
    
    unmatched_nodes_advisor = student_nodes - advisor_nodes
    num_nodes_to_add = int(len(unmatched_nodes_advisor) * exchange_level)
    
    # If exchange level is 1, add all unmatched nodes
    if exchange_level == 1.0:
        nodes_to_add = unmatched_nodes_advisor
    else:
        # Convert set to list before using random.sample
        nodes_to_add = random.sample(list(unmatched_nodes_advisor), num_nodes_to_add)
    
    for node in nodes_to_add:
        if not student_model.isUtilityNode(node):   
            node_info = student_model.variableFromName(node)
            advisor_model.add(node_info)
    
    return advisor_model, unmatched_nodes_advisor,nodes_to_add
    
#***********************************




def find_matched_parents(model1, model2):
    model1_parents = get_utility_parents(model1)
    model2_parents = get_utility_parents(model2)

    matched_parents = set()
    for parent in model1_parents:
        if parent in model2_parents:
            matched_parents.add(parent)

    return matched_parents

def find_unmatched_parents(model1, model2):
    model1_parents = get_utility_parents(model1)
    model2_parents = get_utility_parents(model2)

    unmatched_parents = set()
    for parent in model1_parents:
        if parent not in model2_parents:
            unmatched_parents.add(parent)

    return unmatched_parents

def get_parents_of_unmatched_parents(unmatched_parents, model):
    parents_of_unmatched_parents = {}

    for parent_name in unmatched_parents:
        parent_id = model.idFromName(parent_name)
        parent_parents = [model.variable(parent_id).name() for parent_id in model.parents(parent_id)]
        parents_of_unmatched_parents[parent_name] = parent_parents

    return parents_of_unmatched_parents




def find_and_get_parents_of_unmatched_parents(model1, model2, advisor_model):
    unmatched_parents = find_unmatched_parents(model2,model1)
    parents_of_unmatched_parents = get_parents_of_unmatched_parents(unmatched_parents, model1)
    
    buyer_utility_parents = set(get_utility_parents(model2))
    
    remove_nodes = list(unmatched_parents)
    for parent_list in parents_of_unmatched_parents.values():
        remove_nodes.extend(parent_list)
    
    remove_nodes = [node for node in remove_nodes if node not in buyer_utility_parents]
    
    return remove_nodes


def find_and_get_parents_of_matched_parents(model1, model2, advisor_model):
    unmatched_parents = find_matched_parents(model1, model2)
    parents_of_matched_parents = get_parents_of_matched_parents(unmatched_parents, model1)
    
    buyer_utility_parents = set(get_utility_parents(model2))
    
    remove_nodes = list(unmatched_parents)
    for parent_list in parents_of_matched_parents.values():
        remove_nodes.extend(parent_list)
    
    remove_nodes = [node for node in remove_nodes if node not in buyer_utility_parents]
    
    return remove_nodes
    
def check_unmatched_parents_in_expert_model(unmatched_parents, model):
    
    expert_chance_nodes = [node for node in model.names() if model.isChanceNode(node)]

    unmatched_parents_in_expert = set()
    for parent in unmatched_parents:
        if parent not in expert_chance_nodes:
            unmatched_parents_in_expert.add(parent)

    return expert_chance_nodes, unmatched_parents_in_expert

def check_unmatched_parents_in_expert_model_final_situation(model1, model2):
    model1_chance_nodes = [node for node in model1.names() if model1.isChanceNode(node)]    
    model2_chance_nodes = [node for node in model2.names() if model2.isChanceNode(node)]

    unmatched_parents_in_expert = set()
    for parent in model1_chance_nodes:
        if parent not in model2_chance_nodes:
            unmatched_parents_in_expert.add(parent)

    return unmatched_parents_in_expert
    

def filter_chance_nodes(model, unmatched_parents):

    for node_to_remove in unmatched_parents:
        model.erase(node_to_remove)

    return model    

def get_arcs_to_utility(advisor_model, student_model):
    utility_node_id_advisor = next(node for node in advisor_model.nodes() if advisor_model.isUtilityNode(node))
    utility_node_name_advisor = advisor_model.variable(utility_node_id_advisor).name()

    utility_node_id_student = next(node for node in student_model.nodes() if student_model.isUtilityNode(node))
    utility_node_name_student = student_model.variable(utility_node_id_student).name()

    advisor_arcs_to_utility = []
    student_arcs_to_utility = []

    for arc in advisor_model.arcs():
        if arc[1] == utility_node_id_advisor:
            arc_info = (advisor_model.variable(arc[0]).name(), utility_node_name_advisor)
            advisor_arcs_to_utility.append(arc_info)

    for arc in student_model.arcs():
        if arc[1] == utility_node_id_student:
            arc_info = (student_model.variable(arc[0]).name(), utility_node_name_student)
            student_arcs_to_utility.append(arc_info)

    return advisor_arcs_to_utility, student_arcs_to_utility


def delete_unmatched_arcs(advisor_model, student_model):
    matched_parents = find_matched_parents(student_model, advisor_model)
    unmatched_parents = find_unmatched_parents(advisor_model, student_model)
    
    advisor_utility_node_id = next(node for node in advisor_model.nodes() if advisor_model.isUtilityNode(node))
    advisor_utility_node = advisor_model.variable(advisor_utility_node_id)

    unmatched_arcs = [(parent, advisor_utility_node.name()) for parent in unmatched_parents]

    
    for arc in unmatched_arcs:
        parent_id = advisor_model.idFromName(arc[0])
        utility_id = advisor_model.idFromName(arc[1])
        if (parent_id, utility_id) in advisor_model.arcs():
            advisor_model.eraseArc(parent_id, utility_id)
    
    return advisor_model


def transfer_utilities(student_model, combined_model):
    common_chance_nodes = set(student_model.names()) & set(combined_model.names())

    for states in product(*[student_model.variable(node).domain() for node in common_chance_nodes]):
  
        student_utility_node = next(node for node in student_model.nodes() if student_model.isUtilityNode(node))
        student_utility_potential = student_model.utility(student_utility_node).variable(student_utility_node)
        student_utility = student_utility_potential.get(*states)
        
        
        combined_utility_node = next(node for node in combined_model.nodes() if combined_model.isUtilityNode(node))        
        combined_utility_potential = combined_model.utility(combined_utility_node).variable(combined_utility_node)
        
       
        combined_utility_potential.set(*states, student_utility)

    return combined_model





