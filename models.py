import pyAgrum as gum

def clinician_id():
        # Doctor's Influence Diagram
    yn_states = ['no','yes']
    treatments = ['antithyroid', 'RAI', 'thyroidectomy']


    gbn = gum.InfluenceDiagram()
    # Decision
    treatment = gbn.addDecisionNode(gum.LabelizedVariable("treatment", "Treatment", treatments))
    satisfaction = gbn.addUtilityNode(gum.LabelizedVariable("DoctorU", "Doctor Utility", 1))   
    eye = gbn.add(gum.LabelizedVariable("eye disease", "Thyroid Eye Disease", yn_states))  
    smoking = gbn.add(gum.LabelizedVariable("smoking", "Smoking", yn_states))  
    hyperthyroidism = gbn.add(gum.LabelizedVariable("hyperthyroidism", "hyperthyroidism", yn_states))  
    goiter = gbn.add(gum.LabelizedVariable("goiter", "goiter", ["Small", "Large"]))
    Pre_TSH_Level = gbn.add(gum.LabelizedVariable("Pre_TSH_Level", "General TSH_Level Status", 3)) # Low, Medium, High
    eye_post = gbn.add(gum.LabelizedVariable("eye_post", "Post treatment eye disease", yn_states))
    hypothyroidism = gbn.add(gum.LabelizedVariable("hypothyroidism", "Hypothyroidism", yn_states))
    remission = gbn.add(gum.LabelizedVariable("remission", "Remission", ["yes","no"]))
    Post_TSH_Level = gbn.add(gum.LabelizedVariable("Post_TSH_Level", "General TSH_Level Status", 3)) # High, Medium, Low
    # Arcs

    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Small','hyperthyroidism':'no'}] = [0.10, 0.50, 0.40]
    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Large','hyperthyroidism':'no'}] = [0.20, 0.45, 0.35]
    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Small','hyperthyroidism':'yes'}] = [0.18, 0.42, 0.40]
    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Large','hyperthyroidism':'yes'}] = [0.41, 0.39, 0.20]


    gbn.addArc(eye, eye_post)
    #gbn.addArc(goiter,treatment)
    gbn.addArc(hyperthyroidism, goiter)
    gbn.addArc(smoking, eye)

    gbn.addArc(treatment, remission)
    gbn.addArc(treatment, eye_post)
    gbn.addArc(smoking, eye_post)

    gbn.addArc(hyperthyroidism,Pre_TSH_Level)
    gbn.addArc(goiter, Pre_TSH_Level)
    #gbn.addArc(Pre_TSH_Level,treatment)
    gbn.addArc(hypothyroidism, Post_TSH_Level)

    gbn.addArc(hyperthyroidism,remission)
    gbn.addArc(hyperthyroidism,eye_post)

    # Side Effects

    hypoparathyroidism = gbn.add(gum.LabelizedVariable("hypoparathyroidism", "Hypoparathyroidism", yn_states))
    laryngeal = gbn.add(gum.LabelizedVariable("laryngeal", "Laryngeal nerve damage", yn_states))
    hepatoxicity = gbn.add(gum.LabelizedVariable("hepatoxicity", "Hepatoxicity", yn_states))
    agranulocytosis = gbn.add(gum.LabelizedVariable("agranulocytosis", "Agrunolocytosis", yn_states))

    lifelong_thyroid_replacement = gbn.add(gum.LabelizedVariable("lifelong_thyroid_replacement", "Lifelong_Thyroid_Replacement", 2))  # No, Yes
    cost = gbn.add(gum.LabelizedVariable("cost", "Perceived Cost", 2))  # Low, High


    gbn.addArc(treatment, hypothyroidism)
    gbn.addArc(treatment, hypoparathyroidism)
    gbn.addArc(treatment, laryngeal)
    gbn.addArc(treatment, hepatoxicity)
    gbn.addArc(treatment, agranulocytosis)
    gbn.addArc(treatment,Post_TSH_Level)
    gbn.addArc(treatment,cost)
    # gbn.addArc(treatment,lifelong_thyroid_replacement)
    gbn.addArc(hypothyroidism,lifelong_thyroid_replacement)

    ## for patients vocal cord dysfunction elenebilir

    gbn.addArc(hypothyroidism, satisfaction)
    gbn.addArc(hypoparathyroidism, satisfaction)
    gbn.addArc(laryngeal, satisfaction)
    gbn.addArc(hepatoxicity, satisfaction)
    gbn.addArc(agranulocytosis, satisfaction)



    #gbn.addArc(cost, satisfaction)
    #gbn.addArc(lifelong_thyroid_replacement, satisfaction)
    #gbn.addArc(rash, satisfaction)
    #gbn.addArc(hypothyroidism, satisfaction)
    gbn.addArc(eye_post, satisfaction)
    gbn.addArc(remission, satisfaction)

    gbn.cpt("hyperthyroidism").fillWith([0, 1])
    gbn.cpt("smoking").fillWith([0.65, 0.35]) # Probabilities for Non-Smoker (No) and Smoker (Yes)


    gbn.cpt('eye disease')[{'smoking': 'no'}] = [0.85, 0.15]  
    gbn.cpt('eye disease')[{'smoking': 'yes'}] = [0.42, 0.58]

    ### buna kanıt lazım
    gbn.cpt('goiter')[{'hyperthyroidism': 'no'}] = [0.95,0.05]  
    gbn.cpt('goiter')[{'hyperthyroidism': 'yes'}] = [0.30,0.70]



    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'no', 'eye disease': 'no', 'hyperthyroidism': 'yes'}] = [0.41, 0.59]
    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'yes', 'eye disease': 'no', 'hyperthyroidism': 'yes'}] = [0.10, 0.90]
    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'no', 'eye disease': 'yes', 'hyperthyroidism': 'yes'}] = [0.22, 0.78]
    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'yes', 'eye disease': 'yes', 'hyperthyroidism': 'yes'}] = [0.04, 0.96]

    # Antithyroid Drugs
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'no', 'eye disease': 'no', 'hyperthyroidism': 'yes'}] = [0.59, 0.41]
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'yes', 'eye disease': 'no', 'hyperthyroidism': 'yes'}] = [0.37, 0.63]
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'no', 'eye disease': 'yes', 'hyperthyroidism': 'yes'}] = [0.40, 0.60]
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'yes', 'eye disease': 'yes', 'hyperthyroidism': 'yes'}] = [0.21, 0.79]

    # Thyroidectomy
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'no', 'eye disease': 'no', 'hyperthyroidism': 'yes'}] = [0.93, 0.07]
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'yes', 'eye disease': 'no', 'hyperthyroidism': 'yes'}] = [0.77, 0.23]
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'no', 'eye disease': 'yes', 'hyperthyroidism': 'yes'}] = [0.85, 0.15]
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'yes', 'eye disease': 'yes', 'hyperthyroidism': 'yes'}] = [0.59, 0.41]

    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'no', 'eye disease': 'no', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'yes', 'eye disease': 'no', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'no', 'eye disease': 'yes', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'RAI', 'smoking': 'yes', 'eye disease': 'yes', 'hyperthyroidism': 'no'}] = [0.5, 0.5]

    # Antithyroid Drugs
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'no', 'eye disease': 'no', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'yes', 'eye disease': 'no', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'no', 'eye disease': 'yes', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'antithyroid', 'smoking': 'yes', 'eye disease': 'yes', 'hyperthyroidism': 'no'}] = [0.5, 0.5]

    # Thyroidectomy
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'no', 'eye disease': 'no', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'yes', 'eye disease': 'no', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'no', 'eye disease': 'yes', 'hyperthyroidism': 'no'}] = [0.5, 0.5]
    gbn.cpt("eye_post")[{'treatment': 'thyroidectomy', 'smoking': 'yes', 'eye disease': 'yes', 'hyperthyroidism': 'no'}] = [0.5, 0.5]


    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Small','hyperthyroidism':'no'}] = [0.10, 0.50, 0.40]
    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Large','hyperthyroidism':'no'}] = [0.20, 0.45, 0.35]

    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Small','hyperthyroidism':'yes'}] = [0.18, 0.42, 0.40]
    gbn.cpt("Pre_TSH_Level")[{'goiter': 'Large','hyperthyroidism':'yes'}] = [0.41, 0.39, 0.20]

    gbn.cpt('remission')[{'treatment': 'antithyroid', 'hyperthyroidism': 'yes'}] = [0.50, 0.50]  
    gbn.cpt('remission')[{'treatment': 'RAI', 'hyperthyroidism': 'yes'}] = [0.90,0.05]  
    gbn.cpt('remission')[{'treatment': 'thyroidectomy', 'hyperthyroidism': 'yes'}] = [1,0]  

    gbn.cpt('remission')[{'treatment': 'antithyroid', 'hyperthyroidism': 'no'}] = [0.50, 0.50]  
    gbn.cpt('remission')[{'treatment': 'RAI', 'hyperthyroidism': 'no'}] = [0.5,0.5]  
    gbn.cpt('remission')[{'treatment': 'thyroidectomy', 'hyperthyroidism': 'no'}] = [0.5,0.5]  

    gbn.cpt('hypoparathyroidism')[{'treatment': 'antithyroid'}] = [1,0]
    gbn.cpt('hypoparathyroidism')[{'treatment': 'RAI'}] = [1, 0]
    gbn.cpt('hypoparathyroidism')[{'treatment': 'thyroidectomy'}] = [0.98,0.02]

    gbn.cpt('laryngeal')[{'treatment': 'antithyroid'}] = [1, 0]
    gbn.cpt('laryngeal')[{'treatment': 'RAI'}] = [1, 0]
    gbn.cpt('laryngeal')[{'treatment': 'thyroidectomy'}] = [0.97,0.03]

    gbn.cpt('hypothyroidism')[{'treatment': 'antithyroid'}] = [.93,.07]     
    gbn.cpt('hypothyroidism')[{'treatment': 'RAI'}] = [.59,.41]  
    gbn.cpt('hypothyroidism')[{'treatment': 'thyroidectomy'}] = [.03,.97]  

    gbn.cpt("hepatoxicity")[{'treatment': 'antithyroid'}] = [0.999,0.001]
    gbn.cpt("hepatoxicity")[{'treatment': 'RAI'}] = [1, 0]
    gbn.cpt("hepatoxicity")[{'treatment': 'thyroidectomy'}] = [1, 0]

    gbn.cpt("agranulocytosis")[{'treatment': 'antithyroid'}] = [0.9972,0.0028]
    gbn.cpt("agranulocytosis")[{'treatment': 'RAI'}] = [1, 0]
    gbn.cpt("agranulocytosis")[{'treatment': 'thyroidectomy'}] = [1, 0]

    # For Antithyroid Medication
    gbn.cpt("Post_TSH_Level")[{'treatment': 'antithyroid','hypothyroidism':'no'}] = [0.10, 0.80, 0.10]
    gbn.cpt("Post_TSH_Level")[{'treatment': 'RAI','hypothyroidism':'no'}] = [0.35, 0.55, 0.1]
    gbn.cpt("Post_TSH_Level")[{'treatment': 'thyroidectomy','hypothyroidism':'no'}] = [0.55, 0.20, 0.25]

    gbn.cpt("Post_TSH_Level")[{'treatment': 'antithyroid','hypothyroidism':'yes'}] = [0.60, 0.05, 0.35]
    gbn.cpt("Post_TSH_Level")[{'treatment': 'RAI','hypothyroidism':'yes'}] = [0.80, 0.02, 0.18]
    gbn.cpt("Post_TSH_Level")[{'treatment': 'thyroidectomy','hypothyroidism':'yes'}] = [0.85, 0.03, 0.12]

    gbn.cpt(cost)[{'treatment': 'RAI'}] = [0.55, 0.45]  
    gbn.cpt(cost)[{'treatment': 'antithyroid'}] = [0.70, 0.30]  
    gbn.cpt(cost)[{'treatment': 'thyroidectomy'}] = [0.20, 0.80]   

    #gbn.cpt("lifelong_thyroid_replacement")[{'treatment': 'antithyroid'}] = [0.50, 0.50]  
    #gbn.cpt("lifelong_thyroid_replacement")[{'treatment': 'RAI'}] = [0.02, 0.98] 
    #gbn.cpt("lifelong_thyroid_replacement")[{'treatment': 'thyroidectomy'}] = [0.02, 0.98] 
    
    
    gbn.cpt("lifelong_thyroid_replacement")[{'hypothyroidism': 'no'}] = [0.99, 0.01]  
    gbn.cpt("lifelong_thyroid_replacement")[{'hypothyroidism': 'yes'}] = [0.0001, 0.9999]  
    return gbn



def patient_id():
    patient_model = gum.InfluenceDiagram()

    # Step 2: Add Pretreatment Variables (Chance Nodes)
    smoking = patient_model.add(gum.LabelizedVariable("smoking", "Smoking", 2))  # No, Yes
    goiter = patient_model.add(gum.LabelizedVariable("goiter", "Goiter", 2))  # Small, Large
    lifelong_thyroid_replacement = patient_model.add(gum.LabelizedVariable("lifelong_thyroid_replacement", "lifelong_thyroid_replacement", 2))  # No, Yes
    hyperthyroidism = patient_model.add(gum.LabelizedVariable("hyperthyroidism", "hyperthyroidism", ['no', 'yes']))  

    # Step 3: Add Decision Node (Treatment Choice)
    #treatment = patient_model.addDecisionNode(gum.LabelizedVariable("treatment", "Patient's Treatment Choice", ["antithyroid", "RAI"]))  # ATD, RAI
    treatment = patient_model.addDecisionNode(gum.LabelizedVariable("treatment", "Patient's Treatment Choice", ["antithyroid", "RAI","thyroidectomy"]))  # ATD, RAI

    # Step 4: Add Posttreatment Variables (Chance Nodes)
    remission = patient_model.add(gum.LabelizedVariable("remission", "Perceived Remission Outcome", 2))  # Yes,No, 
    hypothyroidism = patient_model.add(gum.LabelizedVariable("hypothyroidism", "Perceived Hypothyroidism Risk", 2))  # No, Yes
    cost = patient_model.add(gum.LabelizedVariable("cost", "Perceived Cost", 2))  # Low, Medium, High

    # Step 5: Add Utility Node (Patient's Satisfaction)
    satisfaction = patient_model.addUtilityNode(gum.LabelizedVariable("PatientU", "Patient's Satisfaction", 1))

    #patient_model.add(gum.LabelizedVariable("Pre_TSH_Level", "Pre_TSH_Level", 3))
    #patient_model.addArc("Pre_TSH_Level", "treatment")
    #patient_model.cpt("Pre_TSH_Level").fillWith([0.24, 0.46, 0.30])

    # Step 6: Define Dependencies (Arcs)
    # patient_model.addArc(goiter, treatment)
    # patient_model.addArc(smoking, treatment)
    patient_model.addArc(treatment, remission)
    patient_model.addArc(treatment, hypothyroidism)
    patient_model.addArc(treatment, cost)
    patient_model.addArc(treatment, lifelong_thyroid_replacement)
    patient_model.addArc(remission, satisfaction)
    patient_model.addArc(hypothyroidism, satisfaction)
    patient_model.addArc(cost, satisfaction)
    patient_model.addArc(lifelong_thyroid_replacement, satisfaction)

    # Step 7: Define CPTs for Each Node
    # CPT for Age
    patient_model.cpt(hyperthyroidism)[{}] = [0, 1]
    # CPT for Smoking
    patient_model.cpt(smoking)[{}] = [0.65, 0.35]  # Probabilities for Non-Smoker (No) and Smoker (Yes)

    # CPT for Goiter Size
    patient_model.cpt(goiter)[{}] = [0.75, 0.25]  # Small 75%, Large 25%


    ### CPT for Lifelong_Thyroid_Replacement given Treatment
    patient_model.cpt(lifelong_thyroid_replacement)[{'treatment': 0}] = [0.70, 0.30]  # ATD
    patient_model.cpt(lifelong_thyroid_replacement)[{'treatment': 1}] = [0.85, 0.15]  # RAI
    patient_model.cpt(lifelong_thyroid_replacement)[{'treatment': 2}] = [0.5, 0.5]  # RAI

    # CPT for Remission based on Treatment
    patient_model.cpt(remission)[{'treatment': 0}] = [0.40, 0.60]  # 
    patient_model.cpt(remission)[{'treatment': 1}] = [0.20, 0.80]  # 
    patient_model.cpt(remission)[{'treatment': 2}] = [0.50, 0.50]  # 

    # CPT for Hypothyroidism based on Treatment and Goiter Size
    patient_model.cpt(hypothyroidism)[{'treatment': 0, 'goiter': 0}] = [0.90, 0.10]  # RAI, Small Goiter
    patient_model.cpt(hypothyroidism)[{'treatment': 0, 'goiter': 1}] = [0.85, 0.15]  # RAI, Large Goiter
    patient_model.cpt(hypothyroidism)[{'treatment': 1, 'goiter': 0}] = [0.15, 0.75]  # ATD, Small Goiter
    patient_model.cpt(hypothyroidism)[{'treatment': 1, 'goiter': 1}] = [0.75, 0.25]  # ATD, Large Goiter
    patient_model.cpt(hypothyroidism)[{'treatment': 2, 'goiter': 0}] = [0.5, 0.50]   
    patient_model.cpt(hypothyroidism)[{'treatment': 2, 'goiter': 1}] = [0.5, 0.5]   


    # CPT for Cost based on Treatment
    #patient_model.cpt(cost)[{'treatment': 0}] = [0.20, 0.60, 0.20]   
    #patient_model.cpt(cost)[{'treatment': 1}] = [0.50, 0.40, 0.10]  
    #patient_model.cpt(cost)[{'treatment': 2}] = [0.33, 0.33, 0.33]   

    patient_model.cpt(cost)[{'treatment': 0}] = [0.20, 0.8]   
    patient_model.cpt(cost)[{'treatment': 1}] = [0.50, 0.5]  
    patient_model.cpt(cost)[{'treatment': 2}] = [0.33, 0.67]   
    return patient_model