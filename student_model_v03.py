
import pyAgrum as gum
import random
import itertools


#------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------STUDENT MODEL------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------

def create_student_model():

# Create the Influence Diagram for student
    student_model = gum.InfluenceDiagram()

# Decision node representing course options
    course = student_model.addDecisionNode(gum.LabelizedVariable("course", "course Type", ["Course1", "Course2"]))

# Chance nodes
    reputation = student_model.addChanceNode(gum.LabelizedVariable('reputation', 'Reputation of course professor', ['positive', 'negative']))
    difficulty = student_model.addChanceNode(gum.LabelizedVariable('difficulty', 'Difficulty of course', ['high', 'medium', 'low']))
    friends = student_model.addChanceNode(gum.LabelizedVariable('friends', 'friends in the course', ['yes', 'no']))
    grade = student_model.addChanceNode(gum.LabelizedVariable('Grade', 'Grade', ['>C', 'D', 'F']))
    interest = student_model.addChanceNode(gum.LabelizedVariable('interest', 'interested in course', ['yes', 'no']))
    classsize = student_model.addChanceNode(gum.LabelizedVariable("classsize", "classsize", ['high', 'medium', 'low']))
    workload = student_model.addChanceNode(gum.LabelizedVariable('workload', 'workload of course', ['high', 'medium', 'low']))
    
# Utility node
    utilityS = student_model.addUtilityNode(gum.LabelizedVariable('Student Utility', 'Student Utility', 1))

# Arcs

    # Arcs
    
    student_model.addArc(course, classsize)
    student_model.addArc(course, difficulty)
    
    student_model.addArc(difficulty, reputation)
    student_model.addArc(course, friends)
    student_model.addArc(course, interest)    
    student_model.addArc(difficulty, grade)
    student_model.addArc(difficulty, workload)

    student_model.addArc(classsize, utilityS)
    
    student_model.addArc(workload, utilityS)
    student_model.addArc(interest, utilityS)
    student_model.addArc(grade, utilityS)
    student_model.addArc(friends, utilityS)


# Setting CPDs

    student_model.cpt(difficulty)[{'course': 'Course1'}] = [0.6, 0.3, 0.1]
    student_model.cpt(difficulty)[{'course': 'Course2'}] = [0.4, 0.4, 0.2]

    student_model.cpt(reputation)[{'difficulty': 'high'}] = [0.2, 0.8]
    student_model.cpt(reputation)[{'difficulty': 'medium'}] = [0.5, 0.5]
    student_model.cpt(reputation)[{'difficulty': 'low'}] = [0.8, 0.2]

    student_model.cpt(friends)[{'course': 'Course1'}] = [0.5, 0.5]
    student_model.cpt(friends)[{'course': 'Course2'}] = [0.6, 0.4]

    student_model.cpt(interest)[{'course': 'Course1'}] = [0.7, 0.3]
    student_model.cpt(interest)[{'course': 'Course2'}] = [0.6, 0.4]

    student_model.cpt(grade)[{'difficulty': 'high'}] = [0.2, 0.5, 0.3]
    student_model.cpt(grade)[{'difficulty': 'medium'}] = [0.5, 0.3, 0.2]
    student_model.cpt(grade)[{'difficulty': 'low'}] = [0.8, 0.15, 0.05]

    student_model.cpt(workload)[{'difficulty': 'high'}] = [0.3, 0.5, 0.2]
    student_model.cpt(workload)[{'difficulty': 'medium'}] = [0.4, 0.3, 0.3]
    student_model.cpt(workload)[{'difficulty': 'low'}] = [0.7, 0.25, 0.05]

    student_model.cpt(classsize)[{'course': 'Course1'}] = [0.5, 0.4, 0.1]
    student_model.cpt(classsize)[{'course': 'Course2'}] = [0.6, 0.3, 0.1]
    
# Iterate over all possible combinations of states
# Define a dictionary to store utility values
    utilities = {}

# Iterate over all possible combinations of states
    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for wr_val in ["high", "medium", "low"]:
                    for cl_val in ["high", "medium", "low"]:
                        # Base value for having interest
                        u = 50 if int_val == "yes" else 5
    
                        # Incremental value for having friends
                        v = 60 if fr_val == "yes" else 10
    
                        # Value adjustments based on grade
                        if grade_val == ">C":
                            y = 50
                        elif grade_val == "D":
                            y = 30
                        else:
                            y = 0
    
                        # Value adjustments based on workload
                        if wr_val == "high":
                            x = 20
                        elif wr_val == "medium":
                            x = 30
                        else:
                            x = 40
    
                        # Value adjustments based on workload
                        if cl_val == "high":
                            z = 20
                        elif cl_val == "medium":
                            z = 30
                        else:
                            z = 40
    
                        # Store the utility value for the combination of states
                        utilities[(int_val, grade_val, fr_val, wr_val, cl_val)] = 0.1*u + 0.2*v + 0.5*y + 0.1*x + 0.1*z
    
    # Fill the utility node with the computed values
    for int_val in ["yes", "no"]:
        for grade_val in [">C", "D", "F"]:
            for fr_val in ["yes", "no"]:
                for wr_val in ["high", "medium", "low"]:
                    for cl_val in ["high", "medium", "low"]:
                        # Set the utility value using the generated utilities
                        student_model.utility(utilityS)[{'interest': int_val, 'Grade': grade_val, 'friends': fr_val, 'workload': wr_val, 'classsize': cl_val}] = utilities[(int_val, grade_val, fr_val, wr_val, cl_val)]

    return student_model