import random
import numpy as np
import itertools
import pyAgrum as gum
from prettytable import PrettyTable


def transfer_parent_node_parameter(model1_params, model2_params, parent_node_name):

    row_to_transfer = None
    for row in model2_params:
        if row[0] == parent_node_name:
            row_to_transfer = row
            break

    if row_to_transfer is None:
        raise ValueError(
            f"Parent node '{parent_node_name}' not found in model2 parameters."
        )

    for row in model1_params:
        if row[0] == parent_node_name:
            print(f"Parent node '{parent_node_name}' already exists in the parameters.")
            return model1_params

    updated_model1_params = np.vstack([model1_params, row_to_transfer])

    return updated_model1_params


def calculate_utility_values(model, utility_node_name, parameters):
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

        for i, (parent_name, state) in enumerate(
            zip(parent_names, parent_state_combination)
        ):
            num_states = len(parent_domains[parent_name])
            state_index = parent_domains[parent_name].index(state)

            incremental_value = (num_states - state_index - 1) * increments[i]
            weighted_value = weights[i] * incremental_value
            utility_value += weighted_value

        utilities[parent_state_combination] = utility_value

    for parent_state_combination, utility_value in utilities.items():
        state_dict = {
            parent_name: state
            for parent_name, state in zip(parent_names, parent_state_combination)
        }
        model.utility(utility_node_id)[state_dict] = utility_value


def decision_alternative_transfer(model1, model2, decision_node):
    model1, decision_node = update_decision_node_options(model1, model2, decision_node)
    if model1 is None:
        print(
            f"Failed to update decision node options for '{decision_node}'. Terminating process."
        )
        return None

    add_equal_probabilities_for_new_option(model1)
    return model1


def update_decision_node_options(model1, model2, decision_node_name):
    try:
        model1_decision_node_id = model1.idFromName(decision_node_name)
        model2_decision_node_id = model2.idFromName(decision_node_name)
    except gum.NotFound:
        print(f"Object not found: No element with the key '{decision_node_name}'")
        return None, None

    if not (
        model1.isDecisionNode(model1_decision_node_id)
        and model2.isDecisionNode(model2_decision_node_id)
    ):
        print(f"The node '{decision_node_name}' is not a decision node in both models.")
        return None, None

    model1_options = model1.variable(decision_node_name).labels()
    model2_options = model2.variable(decision_node_name).labels()

    print(
        f"Options for decision node '{decision_node_name}' before updating: {model1_options}"
    )

    missing_options = [
        option for option in model2_options if option not in model1_options
    ]

    parents_of_decision_node = [
        parent for parent in model1.parents(model1_decision_node_id)
    ]
    children_of_decision_node = [
        child for child in model1.children(model1_decision_node_id)
    ]

    original_cpts = {
        child: model1.cpt(child).tolist() for child in children_of_decision_node
    }

    if missing_options:
        model1.erase(decision_node_name)

        all_options = list(model1_options) + missing_options
        updated_decision_var = gum.LabelizedVariable(
            decision_node_name, "Decision Node", all_options
        )
        model1.addDecisionNode(updated_decision_var)

        for parent in parents_of_decision_node:
            model1.addArc(model1.variable(parent).name(), decision_node_name)

        for child in children_of_decision_node:
            model1.addArc(decision_node_name, model1.variable(child).name())
            for idx, option in enumerate(model1_options):
                model1.cpt(child)[{decision_node_name: option}] = original_cpts[child][
                    idx
                ]

        updated_model1_options = model1.variable(decision_node_name).labels()
        print(
            f"Updated options for decision node '{decision_node_name}': {updated_model1_options}"
        )

    return model1, decision_node_name


def add_equal_probabilities_for_new_option(model):
    if model is None:
        print("Model is None, cannot add equal probabilities for new options.")
        return

    decision_node_id = next(
        node for node in model.nodes() if model.isDecisionNode(node)
    )
    decision_node_name = model.variable(decision_node_id).name()
    all_decision_states = model.variable(decision_node_id).labels()

    for child in model.children(decision_node_id):
        cpt = model.cpt(child)
        for state in all_decision_states:
            cpt[{decision_node_name: state}] = 1.0 / len(all_decision_states)


def show_decision_utilities3(model):
    decision_node_id = next(
        node for node in model.nodes() if model.isDecisionNode(node)
    )
    decision_node = model.variable(decision_node_id)
    limid = gum.ShaferShenoyLIMIDInference(model)

    state_utilities = {}
    max_expected_utility = float("-inf")
    max_utility_state = None

    decision_domain = decision_node.labels()

    for state in decision_domain:
        limid.setEvidence({decision_node.name(): state})
        limid.makeInference()
        meu = limid.MEU()

        expected_utility = (
            meu.get("mean", float("-inf")) if isinstance(meu, dict) else meu
        )
        state_utilities[state] = expected_utility

        if expected_utility > max_expected_utility:
            max_expected_utility = expected_utility
            max_utility_state = state

    return state_utilities, max_expected_utility, max_utility_state


def compare_final_decisions(utilities_model1, utilities_model2, threshold=5):
    threshold = threshold if threshold is not None else 5
    result = PrettyTable()

    utilities_model1_rounded = {
        state: round(utility, 2) for state, utility in utilities_model1.items()
    }
    utilities_model2_rounded = {
        state: round(utility, 2) for state, utility in utilities_model2.items()
    }

    max_utility_state_model1 = max(utilities_model1_rounded.items(), key=lambda x: x[1])
    max_utility_state_model2 = max(utilities_model2_rounded.items(), key=lambda x: x[1])

    sorted_states_model1 = sorted(
        utilities_model1.items(), key=lambda x: x[1], reverse=True
    )
    sorted_states_model2 = sorted(
        utilities_model2.items(), key=lambda x: x[1], reverse=True
    )

    second_best_state_model1, second_best_utility_model1 = sorted_states_model1[1]
    second_best_state_model2, second_best_utility_model2 = sorted_states_model2[1]

    result.field_names = ["The Comparisons", "Result"]

    print("Student Model:", utilities_model1_rounded)
    print("Advisor Model:", utilities_model2_rounded)

    if max_utility_state_model1[0] == max_utility_state_model2[0]:
        result.add_row(
            [
                "Max Utility Decisions",
                f"Student: {max_utility_state_model1}, Advisor: {max_utility_state_model2}",
            ]
        )
        result.add_row(["Result", "Full Consensus"])
    elif (
        second_best_state_model1[0] == max_utility_state_model2[0]
        or max_utility_state_model1[0] == second_best_state_model2[0]
        or second_best_state_model1[0] == second_best_state_model2[0]
    ):
        result.add_row(
            [
                "Max Utility Decisions",
                f"Student: {max_utility_state_model1}, Advisor: {max_utility_state_model2}",
            ]
        )
        result.add_row(
            [
                "Second Best Decision",
                f"Student: {second_best_state_model1}, Advisor: {second_best_state_model2}",
            ]
        )
        result.add_row(["Result", f"Partial Consensus"])
    else:
        result.add_row(
            [
                "Max Utility Decisions",
                f"Student: {max_utility_state_model1}, Advisor: {max_utility_state_model2}",
            ]
        )
        result.add_row(
            [
                "Second Best Decision",
                f"Student: {second_best_state_model1}, Advisor: {second_best_state_model2}",
            ]
        )
        result.add_row(["Result", "No Agreement"])

    return result


def arc_transfer(model1, model2, node_name):
    model1_utility_node_name = next(
        (
            node
            for node in model1.names()
            if model1.isUtilityNode(model1.idFromName(node))
        ),
        None,
    )
    model2_utility_node_name = next(
        (
            node
            for node in model2.names()
            if model2.isUtilityNode(model2.idFromName(node))
        ),
        None,
    )

    if not model1_utility_node_name or not model2_utility_node_name:
        print("Utility nodes do not exist in one or both models.")
        return model1

    model1_utility_node_id = model1.idFromName(model1_utility_node_name)
    model2_utility_node_id = model2.idFromName(model2_utility_node_name)

    for parent_id in model1.parents(model1_utility_node_id):
        parent_name = model1.variable(parent_id).name()
        if parent_name in model2.names():
            parent_id_model2 = model2.idFromName(parent_name)
            if not model2.existsArc(parent_id_model2, model2_utility_node_id):
                model2.addArc(parent_id_model2, model2_utility_node_id)

    for child_id in model1.children(model1_utility_node_id):
        child_name = model1.variable(child_id).name()
        if child_name in model2.names():
            child_id_model2 = model2.idFromName(child_name)
            if not model2.existsArc(model2_utility_node_id, child_id_model2):
                model2.addArc(model2_utility_node_id, child_id_model2)

    model2_decision_node_name = next(
        (
            node
            for node in model2.names()
            if model2.isDecisionNode(model2.idFromName(node))
        ),
        None,
    )
    model1_decision_node_name = next(
        (
            node
            for node in model1.names()
            if model1.isDecisionNode(model1.idFromName(node))
        ),
        None,
    )

    if not model1_decision_node_name or not model2_decision_node_name:
        print("Decision nodes do not exist in one or both models.")
        return model1

    model2_decision_node_id = model2.idFromName(model2_decision_node_name)
    model1_decision_node_id = model1.idFromName(model1_decision_node_name)

    for child_id in model2.children(model2_decision_node_id):
        child_name = model2.variable(child_id).name()
        if child_name in model1.names() and not model1.existsArc(
            model1_decision_node_id, model1.idFromName(child_name)
        ):
            model1.addArc(model1_decision_node_id, model1.idFromName(child_name))

    for parent_id in model2.parents(model2_decision_node_id):
        parent_name = model2.variable(parent_id).name()
        if parent_name in model1.names() and not model1.existsArc(
            model1.idFromName(parent_name), model1_decision_node_id
        ):
            model1.addArc(model1.idFromName(parent_name), model1_decision_node_id)

    model2_utility_node = model2.idFromName(model2_utility_node_name)
    model1_utility_node = model1.idFromName(model1_utility_node_name)

    model2_utility_parents = set(model2.parents(model2_utility_node))
    model1_utility_parents = set(model1.parents(model1_utility_node))
    common_parents = model2_utility_parents & model1_utility_parents

    for common_parent_id in common_parents:
        common_parent_name = model2.variable(common_parent_id).name()
        if common_parent_name in model1.names():
            for parent_id in model1.parents(model1.idFromName(common_parent_name)):
                parent_name = model1.variable(parent_id).name()
                if model1.existsArc(
                    model1.idFromName(parent_name),
                    model1.idFromName(common_parent_name),
                ):
                    model1.eraseArc(
                        model1.idFromName(parent_name),
                        model1.idFromName(common_parent_name),
                    )

    for node in model2.names():
        if model2.isChanceNode(model2.idFromName(node)) and node in model1.names():
            for parent_id in model2.parents(model2.idFromName(node)):
                parent_name = model2.variable(parent_id).name()
                if parent_name in model1.names() and not model1.existsArc(
                    model1.idFromName(parent_name), model1.idFromName(node)
                ):
                    model1.addArc(
                        model1.idFromName(parent_name), model1.idFromName(node)
                    )

    if node_name in model2.names():
        node_id_model2 = model2.idFromName(node_name)
        for parent_id in model2.parents(node_id_model2):
            parent_name = model2.variable(parent_id).name()
            if parent_name in model1.names() and not model1.existsArc(
                model1.idFromName(parent_name), model1.idFromName(node_name)
            ):
                model1.addArc(
                    model1.idFromName(parent_name), model1.idFromName(node_name)
                )
    else:
        print(f"Node {node_name} does not exist in model2.")

    return model1


def add_nodes_from_model2_to_model1(model1, model2, node_name):
    interaction_counter = 0

    if not model2.exists(node_name):
        print(f"Node {node_name} does not exist in model2.")
        return model1, None

    node_id_model2 = model2.idFromName(node_name)

    if not model2.isChanceNode(node_id_model2):
        print(f"Node {node_name} is not a chance node in model2.")
        return model1, None

    if model1.exists(node_name):
        print(f"Node {node_name} already exists in the model1 model.")
        return model1, node_name

    node_info = model2.variable(node_id_model2)
    model1.add(node_info)

    for parent_id in model2.parents(node_id_model2):
        parent_name = model2.variable(parent_id).name()
        if not model1.exists(parent_name):
            model1.add(model2.variable(parent_id))
        model1.addArc(model1.idFromName(parent_name), model1.idFromName(node_name))

    print(f"Node {node_name} added to the model1 model with its parents.")
    interaction_counter += 1

    return model1, node_name


def arc_transfer(model1, model2, node_name):

    try:
        student_utility_node_name = next(
            node for node in model1.names() if model1.isUtilityNode(node)
        )
        advisor_utility_node_name = next(
            node for node in model2.names() if model2.isUtilityNode(node)
        )
    except StopIteration:
        print(
            "No utility nodes found in one of the models. Arc transfer cannot proceed."
        )
        return model1

    student_utility_node_id = model1.idFromName(student_utility_node_name)
    advisor_utility_node_id = model2.idFromName(advisor_utility_node_name)

    for parent_id in model1.parents(student_utility_node_id):
        parent_name = model1.variable(parent_id).name()
        if parent_name in model2.names():
            parent_id_advisor = model2.idFromName(parent_name)
            if not model2.existsArc(parent_id_advisor, advisor_utility_node_id):
                model2.addArc(parent_id_advisor, advisor_utility_node_id)

    for child_id in model1.children(student_utility_node_id):
        child_name = model1.variable(child_id).name()
        if child_name in model2.names():
            child_id_advisor = model2.idFromName(child_name)
            if not model2.existsArc(advisor_utility_node_id, child_id_advisor):
                model2.addArc(advisor_utility_node_id, child_id_advisor)

    try:
        advisor_decision_node = [
            node for node in model2.names() if model2.isDecisionNode(node)
        ][0]
        student_decision_node = [
            node for node in model1.names() if model1.isDecisionNode(node)
        ][0]
    except IndexError:
        print(
            "No decision nodes found in one of the models. Arc transfer for decision nodes cannot proceed."
        )
        return model1

    for child_id in model2.children(advisor_decision_node):
        child_name = model2.variable(child_id).name()
        if child_name in model1.names() and not model1.existsArc(
            student_decision_node, child_name
        ):
            model1.addArc(student_decision_node, child_name)

    for parent_id in model2.parents(advisor_decision_node):
        parent_name = model2.variable(parent_id).name()
        if parent_name in model1.names() and not model1.existsArc(
            parent_name, student_decision_node
        ):
            model1.addArc(parent_name, student_decision_node)

    advisor_utility_parents = set(model2.parents(advisor_utility_node_id))
    student_utility_parents = set(model1.parents(student_utility_node_id))
    common_parents = advisor_utility_parents & student_utility_parents

    #    for common_parent_id in common_parents:
    #        common_parent_name = model2.variable(common_parent_id).name()
    #        if common_parent_name in model1.names():
    #            for parent_id in model1.parents(common_parent_id):
    #                parent_name = model1.variable(parent_id).name()
    #                if model1.existsArc(parent_name, common_parent_name):
    #                    model1.eraseArc(parent_name, common_parent_name)

    for node in model2.names():
        if model2.isChanceNode(node) and node in model1.names():
            for parent_id in model2.parents(model2.idFromName(node)):
                parent_name = model2.variable(parent_id).name()
                if parent_name in model1.names() and not model1.existsArc(
                    parent_name, node
                ):
                    model1.addArc(parent_name, node)

    if model2.isChanceNode(node_name):
        child_ids_model2 = model2.children(model2.idFromName(node_name))

        if child_ids_model2:
            child_id_model2 = list(child_ids_model2)[0]
            child_name_model2 = model2.variable(child_id_model2).name()

            if model2.isUtilityNode(child_name_model2):
                utility_nodes_model1 = [
                    node for node in model1.names() if model1.isUtilityNode(node)
                ]
                if utility_nodes_model1:
                    child_name_model1 = utility_nodes_model1[0]
                    if not model1.existsArc(node_name, child_name_model1):
                        model1.addArc(node_name, child_name_model1)
                        print(
                            f"Arc added between {node_name} and {child_name_model1} in model1."
                        )
                else:
                    print("No utility node found in model1.")
            else:
                print("Child node in model2 is not a utility node.")
        else:
            print("No child nodes found in model2 for node:", node_name)
    else:
        print(f"{node_name} is not a chance node.")

    return model1


def get_node_type(model, node_name):

    if not model.exists(node_name):
        print(f"Node {node_name} does not exist in the model.")
        return None

    if model.isChanceNode(node_name):
        return "chance"
    elif model.isDecisionNode(node_name):
        return "decision"
    elif model.isUtilityNode(node_name):
        return "utility"
    else:
        print(f"Node {node_name} is not a chance, decision, or utility node.")
        return None


def add_utility_related_arcs_from_student_to_advisor(student_model, advisor_model):
    student_utility_node_name = next(
        node for node in student_model.names() if student_model.isUtilityNode(node)
    )
    advisor_utility_node_name = next(
        node for node in advisor_model.names() if advisor_model.isUtilityNode(node)
    )

    student_utility_node_id = student_model.idFromName(student_utility_node_name)
    advisor_utility_node_id = advisor_model.idFromName(advisor_utility_node_name)

    for parent_id in student_model.parents(student_utility_node_id):
        parent_name = student_model.variable(parent_id).name()
        if parent_name in advisor_model.names():
            parent_id_advisor = advisor_model.idFromName(parent_name)
            if not advisor_model.existsArc(parent_id_advisor, advisor_utility_node_id):
                advisor_model.addArc(parent_id_advisor, advisor_utility_node_id)

    for child_id in student_model.children(student_utility_node_id):
        child_name = student_model.variable(child_id).name()
        if child_name in advisor_model.names():
            child_id_advisor = advisor_model.idFromName(child_name)
            if not advisor_model.existsArc(advisor_utility_node_id, child_id_advisor):
                advisor_model.addArc(advisor_utility_node_id, child_id_advisor)

    return advisor_model


def add_decision_related_arcs_from_advisor_to_student(advisor_model, student_model):

    advisor_decision_node = [
        node for node in advisor_model.names() if advisor_model.isDecisionNode(node)
    ][0]
    student_decision_node = [
        node for node in student_model.names() if student_model.isDecisionNode(node)
    ][0]

    for child_id in advisor_model.children(advisor_decision_node):
        child_name = advisor_model.variable(child_id).name()
        if child_name in student_model.names() and not student_model.existsArc(
            student_decision_node, child_name
        ):
            student_model.addArc(student_decision_node, child_name)

    for parent_id in advisor_model.parents(advisor_decision_node):
        parent_name = advisor_model.variable(parent_id).name()
        if parent_name in student_model.names() and not student_model.existsArc(
            parent_name, student_decision_node
        ):
            student_model.addArc(parent_name, student_decision_node)

    return student_model


def add_chance_related_arcs_from_advisor_to_student(advisor_model, student_model):
    # Find the utility node in both models
    advisor_utility_node = next(
        node for node in advisor_model.names() if advisor_model.isUtilityNode(node)
    )
    student_utility_node = next(
        node for node in student_model.names() if student_model.isUtilityNode(node)
    )

    advisor_utility_parents = set(
        advisor_model.parents(advisor_model.idFromName(advisor_utility_node))
    )
    student_utility_parents = set(
        student_model.parents(student_model.idFromName(student_utility_node))
    )
    common_parents = advisor_utility_parents & student_utility_parents

    for common_parent_id in common_parents:
        common_parent_name = advisor_model.variable(common_parent_id).name()
        if common_parent_name in student_model.names():
            for parent_id in student_model.parents(common_parent_id):
                parent_name = student_model.variable(parent_id).name()
                if student_model.existsArc(parent_name, common_parent_name):
                    student_model.eraseArc(parent_name, common_parent_name)

    for node in advisor_model.names():
        if advisor_model.isChanceNode(node) and node in student_model.names():
            for parent_id in advisor_model.parents(advisor_model.idFromName(node)):
                parent_name = advisor_model.variable(parent_id).name()

                if parent_name in student_model.names() and not student_model.existsArc(
                    parent_name, node
                ):
                    student_model.addArc(parent_name, node)

    return student_model


def fill_model1_cpts_with_noisy_data(
    model1, model2, selected_node_name, noise_factor=0.1
):
    model1_node_id = model1.idFromName(selected_node_name)
    model2_node_id = model2.idFromName(selected_node_name)

    if not model1.exists(model1_node_id) or not model2.exists(model2_node_id):
        print(f"Node '{selected_node_name}' does not exist in both models.")
        return model1

    model1_cpt = model1.cpt(model1_node_id)
    model2_cpt = model2.cpt(model2_node_id)

    if model1_cpt.shape != model2_cpt.shape:
        print(f"Shape mismatch for node '{selected_node_name}':")
        print(f"Model1 CPT shape: {model1_cpt.shape}")
        print(f"Model2 CPT shape: {model2_cpt.shape}")
        return model1

    noisy_cpt = add_noise_to_cpt(np.array(model2_cpt.tolist()), noise_factor)

    model1.cpt(model1_node_id)[:] = noisy_cpt

    return model1


def add_noise_to_cpt(cpt_array, noise_factor=0.1):
    noisy_cpt = cpt_array + noise_factor * np.random.randn(*cpt_array.shape)

    noisy_cpt = np.clip(noisy_cpt, 0, 1)

    sums = noisy_cpt.sum(axis=-1, keepdims=True)
    normalized_cpt = noisy_cpt / sums

    return normalized_cpt


def print_all_utilitiesX(model):
    for node_name in model.names():
        if model.isUtilityNode(node_name):
            print(f"Utility of {node_name}:")
            print(model.utility(node_name))
            print("\n----------------------\n")


def transfer_parent_node(model1_params, model2_params, parent_node_name):
    row_to_transfer = None
    for row in model2_params:
        if row[0] == parent_node_name:
            row_to_transfer = row
            break

    if row_to_transfer is None:
        raise ValueError(
            f"Parent node '{parent_node_name}' not found in model2 parameters."
        )

    updated_model1_params = np.vstack([model1_params, row_to_transfer])
    return updated_model1_params


def extract_parameters(model, utility_node_name):
    if utility_node_name == "Advisor Utility":
        parameters = np.array(
            [
                ["prerequisite", 0.6, 50],
                ["workload", 0.3, 30],
                ["career_development", 0.1, 10],
            ]
        )
    elif utility_node_name == "Student Utility":
        parameters = np.array(
            [["Grade", 0.2, 60], ["friends", 0.3, 40], ["workload", 0.5, 10]]
        )
    else:
        raise ValueError("Unknown utility node name.")
    return parameters


def add_noise_to_increments(parameters, mu=0, sigma=5):
    noisy_parameters = parameters.copy()
    noise = np.random.normal(mu, sigma, size=noisy_parameters.shape[0])
    noisy_parameters[:, 2] = noisy_parameters[:, 2].astype(float) + noise
    return noisy_parameters


def delete_unmatched_arcs(advisor_model, student_model):
    matched_parents = find_matched_parents(student_model, advisor_model)
    unmatched_parents = find_unmatched_parents(advisor_model, student_model)

    advisor_utility_node_id = next(
        node for node in advisor_model.nodes() if advisor_model.isUtilityNode(node)
    )
    advisor_utility_node = advisor_model.variable(advisor_utility_node_id)

    unmatched_arcs = [
        (parent, advisor_utility_node.name()) for parent in unmatched_parents
    ]

    for arc in unmatched_arcs:
        parent_id = advisor_model.idFromName(arc[0])
        utility_id = advisor_model.idFromName(arc[1])
        if (parent_id, utility_id) in advisor_model.arcs():
            advisor_model.eraseArc(parent_id, utility_id)

    return advisor_model


def find_matched_parents(model1, model2):
    """List of variables that are parents of a utility node in model 1 but not a parent of utility node in model 2"""
    model1_parents = get_utility_parents(model1)
    model2_parents = get_utility_parents(model2)

    matched_parents = set()
    for parent in model1_parents:
        if parent in model2_parents:
            matched_parents.add(parent)

    return matched_parents


def get_utility_parents(influence_diagram):
    """List of parents of utility node(s) in the influence diagram"""
    utility_node_id = next(
        (
            node
            for node in influence_diagram.nodes()
            if influence_diagram.isUtilityNode(node)
        ),
        None,
    )

    if utility_node_id is None:
        return []

    parents = []
    for parent_id in influence_diagram.parents(utility_node_id):
        parent_name = influence_diagram.variable(parent_id).name()
        parents.append(parent_name)

    return parents


def find_unmatched_parents(model1, model2):
    """List of variables that are parents of a utility node in model 1 but not a parent of utility node in model 2"""

    model1_parents = get_utility_parents(model1)
    model2_parents = get_utility_parents(model2)

    unmatched_parents = set(model1_parents) - set(model2_parents)

    return list(unmatched_parents)


def has_empty_cpts(model):
    """Returns true if an influence diagram model has empty cpts
    """

    for node in model.names():
        if model.isChanceNode(node):
            cpt = model.cpt(node)
            if cpt.max() == 0 and cpt.min() == 0:
                return True
    return False


def print_all_cpts(model):
    """Prints all cpts of an influence diagram
    """
    for node_name in model.names():
        if model.isChanceNode(node_name):
            print(f"CPT of {node_name}:")
            print(model.cpt(node_name))
            print("\n-------------------------------\n")


CPT1_difficulty = [0.7, 0.2, 0.1]

CPT1_friends = [0.31, 0.69]

CPT1_interest = [0.6, 0.4]

CPT2_difficulty = [0.2, 0.65, 0.15]

CPT2_friends = [0.41, 0.59]

CPT2_interest = [0.4, 0.6]

CPT3_difficulty = [0.1, 0.2, 0.7]

CPT3_friends = [0.35, 0.65]

CPT3_interest = [0.3, 0.7]

CPT4_difficulty = [0.6, 0.3, 0.1]

CPT4_friends = [0.7, 0.3]

CPT4_interest = [0.7, 0.3]

CPT5_difficulty = [0.1, 0.1, 0.8]

CPT5_friends = [0.8, 0.2]

CPT5_interest = [0.8, 0.2]

CPT5_interest = [0.8, 0.2]


pool = {
    "difficulty": [
        CPT1_difficulty,
        CPT2_difficulty,
        CPT3_difficulty,
        CPT4_difficulty,
        CPT5_difficulty,
    ],
    "friends": [CPT1_friends, CPT2_friends, CPT3_friends, CPT4_friends, CPT5_friends],
    "interest": [
        CPT1_interest,
        CPT2_interest,
        CPT3_interest,
        CPT4_interest,
        CPT5_interest,
    ],
}

selected_cpt_difficulty = random.choice(pool["difficulty"])
selected_cpt_friends = random.choice(pool["friends"])
selected_cpt_interest = random.choice(pool["interest"])


def add_cpt_from_pool(student_model, selected_cpt_difficulty, selected_cpt_friends):
    student_model.cpt("difficulty")[{"course": "Course3"}] = selected_cpt_difficulty
    student_model.cpt("friends")[{"course": "Course3"}] = selected_cpt_friends
