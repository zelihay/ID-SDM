

import pyAgrum as gum

  
#------------------------------------------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------ADVISOR MODEL------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------------------------
def create_advisor_model():
    import pyAgrum as gum

    # Create an Influence Diagram for the advisor's model
    advisor_model = gum.InfluenceDiagram()

    # Decision node: course choice
    course = advisor_model.addDecisionNode(gum.LabelizedVariable("course", "course Type", ["Course1", "Course2", "Course3"]))

    # Chance nodes
    credit = advisor_model.addChanceNode(gum.LabelizedVariable("credit", "Total credit so far", ["below 21", "above or equal 21"]))
    gpa = advisor_model.addChanceNode(gum.LabelizedVariable("gpa", "Total credit so far", ["below 3.5", "above or equal 3.5"]))
    requirement = advisor_model.addChanceNode(gum.LabelizedVariable("requirement", "meet requirements", ["yes", "no"]))
    prerequisite = advisor_model.addChanceNode(gum.LabelizedVariable("prerequisite", "prerequisite", ["Yes", "No"]))
    content = advisor_model.addChanceNode(gum.LabelizedVariable("content", "content of the course", ["Suitable For Student", "Not Suitable For Student"]))
    career_development = advisor_model.addChanceNode(gum.LabelizedVariable("career_development", "Affect on Career development", ["positive", "neutral", "negative"]))
    workload = advisor_model.addChanceNode(gum.LabelizedVariable('workload', 'workload of course', ['high', 'medium', 'low']))
    # Utility node: Optimal course reputation
    UtilityA = advisor_model.addUtilityNode(gum.LabelizedVariable("Advisor Utility", "Optimal course benefit", 1))
    format = advisor_model.addChanceNode(gum.LabelizedVariable("format", "format", ["Online", "Inperson"]))
    classsize = advisor_model.addChanceNode(gum.LabelizedVariable("classsize", "classsize", ['high', 'medium', 'low']))

    # Arcs
    advisor_model.addArc(format, classsize)
    advisor_model.addArc(course, format)
    advisor_model.addArc(course, prerequisite)
    advisor_model.addArc(credit, course)
    advisor_model.addArc(credit, requirement)
    advisor_model.addArc(gpa, course)
    advisor_model.addArc(gpa, requirement)
    advisor_model.addArc(course, content)
    advisor_model.addArc(content, career_development)
    advisor_model.addArc(content, workload)
    advisor_model.addArc(gpa, career_development)

    # Utility arcs
    advisor_model.addArc(classsize, UtilityA)
    advisor_model.addArc(workload, UtilityA)
    advisor_model.addArc(prerequisite, UtilityA)
    advisor_model.addArc(requirement, UtilityA)
    advisor_model.addArc(career_development, UtilityA)

    # CPTs for the advisor's model
    advisor_model.cpt(credit).fillWith([0.2, 0.8])
    advisor_model.cpt(gpa).fillWith([0.75, 0.25])
    advisor_model.cpt(prerequisite)[{'course': 'Course1'}] = [0.7, 0.3]
    advisor_model.cpt(prerequisite)[{'course': 'Course2'}] = [0.5, 0.5]
    advisor_model.cpt(prerequisite)[{'course': 'Course3'}] = [0.8, 0.2]
    advisor_model.cpt(content)[{'course': 'Course1'}] = [0.6, 0.4]
    advisor_model.cpt(content)[{'course': 'Course2'}] = [0.5, 0.5]
    advisor_model.cpt(content)[{'course': 'Course3'}] = [0.7, 0.3]
    advisor_model.cpt(requirement)[{'credit': 'below 21', 'gpa': 'below 3.5'}] = [0.2, 0.8]
    advisor_model.cpt(requirement)[{'credit': 'below 21', 'gpa': 'above or equal 3.5'}] = [0.4, 0.6]
    advisor_model.cpt(requirement)[{'credit': 'above or equal 21', 'gpa': 'below 3.5'}] = [0.5, 0.5]
    advisor_model.cpt(requirement)[{'credit': 'above or equal 21', 'gpa': 'above or equal 3.5'}] = [0.8, 0.2]
    advisor_model.cpt(career_development)[{'content': 'Suitable For Student', 'gpa': 'below 3.5'}] = [0.4, 0.4, 0.2]
    advisor_model.cpt(career_development)[{'content': 'Suitable For Student', 'gpa': 'above or equal 3.5'}] = [0.7, 0.2, 0.1]
    advisor_model.cpt(career_development)[{'content': 'Not Suitable For Student', 'gpa': 'below 3.5'}] = [0.1, 0.4, 0.5]
    advisor_model.cpt(career_development)[{'content': 'Not Suitable For Student', 'gpa': 'above or equal 3.5'}] = [0.3, 0.4, 0.3]

    advisor_model.cpt(workload)[{'content': 'Suitable For Student', 'gpa': 'below 3.5'}] = [0.4, 0.4, 0.2]
    advisor_model.cpt(workload)[{'content': 'Suitable For Student', 'gpa': 'above or equal 3.5'}] = [0.7, 0.2, 0.1]
    advisor_model.cpt(workload)[{'content': 'Not Suitable For Student', 'gpa': 'below 3.5'}] = [0.1, 0.4, 0.5]
    advisor_model.cpt(workload)[{'content': 'Not Suitable For Student', 'gpa': 'above or equal 3.5'}] = [0.3, 0.4, 0.3]

    advisor_model.cpt(format)[{'course': 'Course1'}] = [0.7, 0.3]
    advisor_model.cpt(format)[{'course': 'Course2'}] = [0.5, 0.5]
    advisor_model.cpt(format)[{'course': 'Course3'}] = [0.8, 0.2]

    advisor_model.cpt(classsize)[{'format': 'Online'}] = [0.6, 0.2, 0.1]
    advisor_model.cpt(classsize)[{'format': 'Inperson'}] = [0.7, 0.2, 0.1]
    
    

    # utility values:
    utilities = {}
    for pre_val in ["Yes", "No"]:
        for req_val in ["yes", "no"]:
            for career_val in ["positive", "neutral", "negative"]:
                for wr_val in ["high", "medium", "low"]:
                    for cl_val in ["high", "medium", "low"]:
                        u = 50 if pre_val == "Yes" else 5
                        v = 60 if req_val == "yes" else 10
                        if career_val == "positive":
                            y = 50
                        elif career_val == "neutral":
                            y = 30
                        else:
                            y = 0
                        if wr_val == "high":
                            x = 20
                        elif wr_val == "medium":
                            x = 30
                        else:
                            x = 40    
                        if cl_val == "high":
                            z = 20
                        elif cl_val == "medium":
                            z = 30
                        else:
                            z = 40   
    
                        utilities[(pre_val, req_val, career_val, wr_val, cl_val)] = 0.2 * u + 0.3 * v + 0.5 * y + 0.1 * x + 0.1 * z
    
    # Fill the utility node with the computed values
    for pre_val in ["Yes", "No"]:
        for req_val in ["yes", "no"]:
            for career_val in ["positive", "neutral", "negative"]:
                for wr_val in ["high", "medium", "low"]:
                    for cl_val in ["high", "medium", "low"]:
                        # Set the utility value using the generated utilities
                        advisor_model.utility(UtilityA)[{'prerequisite': pre_val, 'requirement': req_val, 'career_development': career_val, 'workload': wr_val, 'classsize': cl_val}] = utilities[(pre_val, req_val, career_val, wr_val, cl_val)]


    
    return advisor_model
