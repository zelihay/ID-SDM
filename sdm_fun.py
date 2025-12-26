
import itertools 
import numpy as np
import pandas as pd
from pyAgrum import ShaferShenoyLIMIDInference

def calculate_utility_values(model, utility_node_name, parameters):
    """
    This function computes utility values based on parent states, weights, and increments.
    """
    utility_node_id = model.idFromName(utility_node_name)
    utility_parents = model.parents(utility_node_id)
    parent_names = [model.variable(parent_id).name() for parent_id in utility_parents]

    weights = []
    increments = []

    for parent in parent_names:
        found = False
        for row in parameters:
            if row[0] == parent:
                weights.append(float(row[1]))
                increments.append(float(row[2]))
                found = True
                break

        if not found:
            raise ValueError(f"No parameters found for parent '{parent}'")


    assert len(weights) == len(utility_parents), (
        f"Number of weights must match number of parents. "
        f"Found {len(weights)} weights for {len(utility_parents)} parents."
    )
    assert len(increments) == len(utility_parents), (
        f"Number of increments must match number of parents. "
        f"Found {len(increments)} increments for {len(utility_parents)} parents."
    )

    utilities = {}

    parent_domains = {
        parent_name: model.variable(model.idFromName(parent_name)).labels()
        for parent_name in parent_names
    }

    for parent_state_combination in itertools.product(*parent_domains.values()):
        utility_value = 0

        for i, (parent_name, state) in enumerate(zip(parent_names, parent_state_combination)):
            num_states = len(parent_domains[parent_name])
            state_index = parent_domains[parent_name].index(state)

            incremental_value = (num_states - state_index - 1) * increments[i]
            weighted_value = weights[i] * incremental_value
            utility_value += weighted_value

        utilities[parent_state_combination] = utility_value

    for parent_state_combination, utility_value in utilities.items():
        state_dict = {parent_name: state for parent_name, state in zip(parent_names, parent_state_combination)}
        model.utility(utility_node_id)[state_dict] = utility_value
        
        
        
def preference_transfer(variable_name, host_model, target_model, host_preference = {}, target_preference = {}):  
      
    host_utility_name = get_utility_nodes(host_model)[0]
    target_utility_name = get_utility_nodes(target_model)[0]
    target_utility_id = get_utility_node_ids(target_model)[0]

    if not host_model.isChanceNode(variable_name):
        raise ValueError(f"Cannot transfer '{variable_name}': expected chance node")

    if not host_model.existsArc(variable_name, host_utility_name):
        raise ValueError(f"'{variable_name}' is not a parent of utility node")

    if not target_model.exists(variable_name):
        raise ValueError(f"Variable '{variable_name}' does not exist in target model. Apply chance node transfer first.")

    if not target_model.existsArc(variable_name, target_utility_name):
        target_model.addArc(variable_name, target_utility_name)

    target_utility_parents = target_model.parents(target_utility_id)

    prefs = dict()
    for parent_id in target_utility_parents:
        parent_name = target_model.variable(parent_id).name()
        if parent_name.lower() == variable_name.lower():
            prefs[parent_name] = host_preference[parent_name]
        else:
            #prefs[parent_name] = target_preference[parent_name]
            prefs[parent_name] = target_preference.get(parent_name, 0.0)
    num_parents = len(prefs)
    pref_values = np.array(list(prefs.values()))
    new_parents = list(prefs.keys())
    new_weights = pref_values / pref_values.sum()
    
    utility_parameters = np.vstack([new_parents, new_weights, np.repeat(100,num_parents)]).T
    calculate_utility_values(target_model, target_utility_name, utility_parameters)
    #print(new_weights,new_parents)

    return prefs


def preference_transfer2(variable_name, host_model, target_model, 
                        host_preference = {}, # This will be the full set of Patient Prefs (pu_parameters)
                        target_preference = {}, # This will be the full set of Clinician Prefs (cu_parameters)
                        current_combined_prefs = {}, # NEW: The current state of combined prefs
                        weight_factor=1):
    
    # --- Standard initialization and checks ---
    host_utility_name = get_utility_nodes(host_model)[0]
    target_utility_name = get_utility_nodes(target_model)[0]
    target_utility_id = get_utility_node_ids(target_model)[0]

    if not host_model.isChanceNode(variable_name):
        raise ValueError(f"Cannot transfer '{variable_name}': expected chance node")
    # Note: We relax the host_model.existsArc check here as we are treating ALL patient prefs as 'transferred' globally.
    # We must ensure the variable exists in the target model structure (added via chance_node_transfer, though not shown).

    if not target_model.exists(variable_name):
        # We assume the variable is added to the target model structure outside this function
        # e.g., via chance_node_transfer or manual addition to support the utility arc.
        raise ValueError(f"Variable '{variable_name}' does not exist in target model.")

    # Ensure an arc exists in the target model for the transferred variable
    if not target_model.existsArc(variable_name, target_utility_name):
        target_model.addArc(variable_name, target_utility_name)
    # --- End Standard initialization and checks ---

    # --- COLLECTIVE BLENDING LOGIC (Applied only on the first variable transfer) ---
    
    # Check if this is the first transfer (i.e., current_combined_prefs is empty).
    # We only calculate the full blended set once.
    if not current_combined_prefs:
        alpha = weight_factor
        
        # 1. Identify all unique criteria (parents of the utility node in the final model)
        # We must include all parents from both models.
        all_criteria_names = set(host_preference.keys()) | set(target_preference.keys())
        
        # 2. Calculate the combined unnormalized preference for all criteria
        combined_prefs = dict()
        for criterion in all_criteria_names:
            # Get unnormalized weights, using 0.0 if not present in the model's preference dictionary
            w_patient = host_preference.get(criterion, 0.0)
            w_doctor = target_preference.get(criterion, 0.0)
            
            # Apply the collective blending formula: W_C = (alpha * W_P) + ((1 - alpha) * W_D)
            combined_prefs[criterion] = (alpha * w_patient) + ((1 - alpha) * w_doctor)
            
        # The result of the blending is stored in the current_combined_prefs for return
        # and subsequent use/modification if needed (though here it's complete).
        current_combined_prefs.update(combined_prefs)

    # Re-calculate and set the utility values in the target model based on the combined_prefs
    # We assume 'utility_parameters_from_weights' handles the normalization.
    utility_parameters = utility_parameters_from_weights(current_combined_prefs) 
    calculate_utility_values(target_model, target_utility_name, utility_parameters)

    # Return the full set of combined unnormalized preferences
    return current_combined_prefs
    
def get_utility_nodes(id):
    """
    Get names of all utility nodes in the influence diagram.
    
    Parameters
    ----------
    id : pyagrum.InfluenceDiagram
        The influence diagram to search
        
    Returns
    -------
    list of str
        List of utility node names
    """
    utility_nodes = []
    for node_name in id.names():
        if id.isUtilityNode(node_name):
            utility_nodes.append(node_name)
    return utility_nodes

def get_utility_node_ids(id):
    """
    Get IDs of all utility nodes in the influence diagram.
    
    Parameters
    ----------
    id : pyagrum.InfluenceDiagram
        The influence diagram to search
        
    Returns
    -------
    list of int
        List of utility node IDs
    """
    utility_nodes = []
    for node_id in id.nodes():
        if id.isUtilityNode(node_id):
            utility_nodes.append(node_id)
    return utility_nodes 
    
    
    

def chance_node_transfer(variable_name, host_model, target_model):
    host_vid = host_model.idFromName(variable_name)
    host_parent_ids = host_model.parents(host_vid)

    if not host_model.isChanceNode(variable_name):
        raise ValueError(f"Cannot transfer '{variable_name}': expected chance node")

    # Add node if it does not exist
    if not target_model.exists(variable_name):
        node = host_model.variableFromName(variable_name).clone()
        target_model.addChanceNode(node)
    
    target_vid = target_model.idFromName(variable_name)
    target_parent_ids = target_model.parents(target_vid)

    # Add parents if they do not exist in host model
    for target_parent_id in target_parent_ids:
        target_parent_name = target_model.variable(target_parent_id).name()
        if not host_model.exists(target_parent_name):
            target_model.eraseArc(target_parent_name, variable_name)
            continue
        
        if not host_model.existsArc(target_parent_name, variable_name):
            target_model.eraseArc(target_parent_name, variable_name)

    # Add parents if they do not exist
    for parent_id in host_parent_ids:
        parent_name = host_model.variable(parent_id).name()
        # If parent does not exists add it
        if not target_model.exists(parent_name):
            parent = host_model.variableFromName(parent_name)
            # If chance node
            if host_model.isChanceNode(parent_name):
                target_model.addChanceNode(parent)
                # Fill with uniform distribution
                parent_cpt = target_model.cpt(parent_name)
                num_states = parent_cpt.domainSize()
                uniform_probs = np.repeat(1/num_states, num_states)
                parent_cpt.fillWith(uniform_probs)
            # If decision node    
            elif host_model.isDecisionNode(parent_name):
                target_model.addDecisionNode(parent)
            else:
                raise ValueError(f"Parent '{parent_name}' of '{variable_name}' is not a decision or a chance node")
        # If an arc from parent does not exists add it
        if not target_model.existsArc(parent_name, variable_name):
            target_model.addArc(parent_name, variable_name)

    # Copy CPTS reorganized according to node order
    host_cpt = host_model.cpt(variable_name)
    target_cpt = target_model.cpt(variable_name)
    
    target_varnames = target_cpt.names
    target_cpt = host_cpt.reorganize(target_varnames)
    #print(variable_name,target_cpt)
    target_model.cpt(variable_name)[:] = target_cpt.toarray()
    
    return target_model


def show_decision_utilities(model, evidence = {}):
    """
    Calculate expected utilities for all decision states and identify the optimal choice.
    
    Parameters
    ----------
    model : pyagrum.InfluenceDiagram
        Influence diagram with exactly one decision node
        
    Returns
    -------
    tuple
        - dict: Decision states mapped to their expected utilities
        - float: Maximum expected utility value  
        - str: Optimal decision state label
    """
    decision_nodes = [node for node in model.nodes() if model.isDecisionNode(node)]
    decision_node_id = decision_nodes[0]
    decision_node = model.variable(decision_node_id)
    decision_name = decision_node.name()
    decision_labels =   decision_node.labels()

    limid = ShaferShenoyLIMIDInference(model)
    limid.makeInference()
    limid.setEvidence(evidence)
    post_utility = limid.posteriorUtility(decision_name).toarray()
    
    state_utilities = dict(zip(decision_labels, post_utility.tolist()))
    max_expected_utility = np.max(post_utility)
    max_utility_state = decision_labels[np.argmax(post_utility)]

    return state_utilities, max_expected_utility, max_utility_state


def utility_parameters_from_weights(prefs):
    """Temporary function to be compatible with Zeliha's weights"""
    num_parents = len(prefs)    
    parents = list(prefs.keys())    
    pref_values = np.array(list(prefs.values()))    
    weights = pref_values / pref_values.sum() 
    return np.vstack([parents, weights, np.repeat(100,num_parents)]).T



def voe(id):
    """"
    Compute value of evidence per state for each non-decision, non-utility node.
    Uses Shafer–Shenoy LIMID inference to compare base MEU to MEU with each node clamped,
    returning a DataFrame of {node, label, utility_delta} sorted by utility (desc).
    """
    res = []
    limid = ShaferShenoyLIMIDInference(id)
    limid.setEvidence({})
    limid.makeInference()
    base_utility = limid.MEU()["mean"]
    node_names = id.names()
    for node_name in node_names:
        node = id.variableFromName(node_name)
        if id.isDecisionNode(node_name) or id.isUtilityNode(node_name):
            continue
        labels = node.labels()
        for label in labels: 
            limid.setEvidence({node_name: label})
            limid.makeInference()
            utility = limid.MEU()["mean"]
            res.append({"node": node_name, "label": label, "utility": utility - base_utility})
    return pd.DataFrame.from_dict(res).sort_values('utility', ascending=False)