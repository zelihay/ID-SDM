
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
    
    gpa = student_model.addChanceNode(gum.LabelizedVariable("gpa", "Total credit so far", ["below 3.5", "above or equal 3.5"]))
    difficulty = student_model.addChanceNode(gum.LabelizedVariable('difficulty', 'Difficulty of course', ['high', 'medium', 'low']))
    friends = student_model.addChanceNode(gum.LabelizedVariable('friends', 'friends in the course', ['yes', 'no']))
    grade = student_model.addChanceNode(gum.LabelizedVariable('Grade', 'Grade', ['>C', 'D', 'F']))
    
    
    workload = student_model.addChanceNode(gum.LabelizedVariable('workload', 'workload of course', ['high', 'medium', 'low']))
    
# Utility node
    utilityS = student_model.addUtilityNode(gum.LabelizedVariable('Student Utility', 'Student Utility', 1))

# Arcs

    # Arcs
    
    student_model.addArc(gpa, course)
    student_model.addArc(course, difficulty)
    
    
    student_model.addArc(course, friends)
    
    student_model.addArc(difficulty, grade)
    student_model.addArc(difficulty, workload)

    
    
    student_model.addArc(workload, utilityS)
    
    student_model.addArc(grade, utilityS)
    student_model.addArc(friends, utilityS)


# Setting CPDs
    student_model.cpt(gpa).fillWith([0.75, 0.25])
    student_model.cpt(difficulty)[{'course': 'Course1'}] = [0.6, 0.3, 0.1]
    student_model.cpt(difficulty)[{'course': 'Course2'}] = [0.4, 0.4, 0.2]

    student_model.cpt(friends)[{'course': 'Course1'}] = [0.5, 0.5]
    student_model.cpt(friends)[{'course': 'Course2'}] = [0.6, 0.4]

    student_model.cpt(grade)[{'difficulty': 'high'}] = [0.2, 0.5, 0.3]
    student_model.cpt(grade)[{'difficulty': 'medium'}] = [0.5, 0.3, 0.2]
    student_model.cpt(grade)[{'difficulty': 'low'}] = [0.8, 0.15, 0.05]

    student_model.cpt(workload)[{'difficulty': 'high'}] = [0.3, 0.5, 0.2]
    student_model.cpt(workload)[{'difficulty': 'medium'}] = [0.4, 0.3, 0.3]
    student_model.cpt(workload)[{'difficulty': 'low'}] = [0.7, 0.25, 0.05]

    
    
# Iterate over all possible combinations of states
# Define a dictionary to store utility values
    utilities = {}

# Iterate over all possible combinations of states

    for grade_val in [">C", "D", "F"]:
        for fr_val in ["yes", "no"]:
            for wr_val in ["high", "medium", "low"]:

                        # Base value for having interest

    
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

                        # Store the utility value for the combination of states
                    utilities[(grade_val, fr_val, wr_val)] = 0.2*v + 0.5*y + 0.1*x 
    
    # Fill the utility node with the computed values

    for grade_val in [">C", "D", "F"]:
        for fr_val in ["yes", "no"]:
            for wr_val in ["high", "medium", "low"]:
                
                        # Set the utility value using the generated utilities
                    student_model.utility(utilityS)[{'Grade': grade_val, 'friends': fr_val, 'workload': wr_val}] = utilities[( grade_val, fr_val, wr_val)]

    return student_model