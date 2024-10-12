
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

    
    
    return student_model