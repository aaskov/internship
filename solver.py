# -*- coding: utf-8 -*-
"""Assignment solver for internships.

This module contains the assignment solver for the student allocation problem. 
The assignment solver returns the optimized solution to a given input.

"""
from ortools.sat.python import cp_model

# THIS SECTION IS SIABLED FOR NOW - CONTIANS ALL_STUDENT_PRIORITIES
#def solve_internship(all_location_names, all_location_capacities, 
#                     all_student_names, all_student_priorities, all_week_names, 
#                     all_internships, allocation_rule):
#    """Solve internship allocation.
#
#    This function solves the allocation task given the following input
#    arguments. The function returns a list of indices representing the assigned
#    internship for each student.
#
#    Args:
#        all_location_names : Array of string.
#            A list of available location names.
#        all_location_capacities : Array of Array of string.
#            A list of capacities (per week) for indices in 'all_location_names'.
#        all_student_names : Array of string.
#            A list of student names.
#        all_student_priorities : Array of Array of Array of Int.
#            Student priorities per internship.
#        all_week_names : Array of string.
#            A list of week names (sorted by time, ASC).
#        all_internships : Array of Array of Int.
#            Array indexing 'all_location_names' belonging to a 'internship'.
#        allocation_rule : Array of int.
#            Array of week count following the index of 'all_internships'.
#
#    Returns:
#        assignment : Dictionary of student allocations.
#            Dictionary with a 4d-tuple containing boolean allocation.
#        solver : CP-model solver.
#            Variable containing the cp-model model solver.
#        status : Status for the model solver.
#            Variable containing the status of the model solver.
#
#    """
#    assignment = {}
#
#    model = cp_model.CpModel()
#
#    # ====
#    # Pre-rule: Compensate for missing weeks (weeks w. no allocation)
#    # ----
#    delta = 0
#    if len(all_week_names) > sum(allocation_rule):
#        delta = len(all_week_names) - sum(allocation_rule)
#
#        # Append a 'not allocated' location
#        all_location_names.append("NOT_A_LOCATION")
#
#        # Append infinity capacity
#        all_location_capacities.append([999999 for i in range(len(all_week_names))])
#
#        # Append new allocation rule (which must compensate the difference)
#        allocation_rule.append(delta)
#
#        # Append new internship
#        last_index = len(all_location_names) - 1
#        all_internships.append([last_index])
#
#
#    # ====
#    # Initialize: Assignment dictionary
#    # ----
#    for s in range(len(all_student_names)):
#        for w in range(len(all_week_names)):
#            for i in range(len(all_internships)):
#                for j in range(len(all_internships[i])):
#                    name = f"assign_s{s}_w{w}_i{i}_j{j}"
#                    assignment[(s, w, i, j)] = model.NewIntVar(0, 1, name)
#
#    # ====
#    # Define constrains
#    # ----
#
#    # ----
#    # Rule: For a given week add add exactly one allocation per student
#    # ----
#    for s in range(len(all_student_names)):
#        for w in range(len(all_week_names)):
#            model.AddExactlyOne(assignment[(s, w, i, j)]
#                                for i in range(len(all_internships))
#                                for j in range(len(all_internships[i])))
#
#    # ----
#    # Rule: Any student must follow the allocation rules
#    # ----
#    for s in range(len(all_student_names)):
#        for a, allocation in enumerate(allocation_rule):
#            allocated = [assignment[(s, w, a, j)]
#                         for w in range(len(all_week_names))
#                         for j in range(len(all_internships[a]))]
#
#            model.Add(sum(allocated) == allocation)
#
#    # ----
#    # Rule: In any week at any location the capacity constrain must be met
#    # ----
#    for w in range(len(all_week_names)):
#        for i in range(len(all_internships)):
#            for j in range(len(all_internships[i])):
#                allocated = [assignment[(s, w, i, j)]
#                             for s in range(len(all_student_names))]
#
#                # Get the capacity for a location (if none is defined, set 0)
#                _capacities = all_location_capacities[all_internships[i][j]]
#                _capacity = _capacities[w] if w < len(_capacities) else 0
#                
#                model.Add(sum(allocated) <= _capacity)
#
#
#    # ====
#    # Set objectives
#    # ----
#
#    # ---
#    # Rule: Pennalize 'jumps' in internships
#    # ---
#
#    loss_jumps = []
#
#    # Initialize: Loss list
#    for s in range(len(all_student_names)):
#        for w in range(len(all_week_names)-1):
#            for i in range(len(all_internships)):
#                for j in range(len(all_internships[i])):
#                    name = f"loss_s{s}_w{w}_i{i}_j{j}"
#                    loss_jumps.append(model.NewIntVar(0, 1, name))
#
#    # Create loss equation
#    idx = 0
#    for s in range(len(all_student_names)):
#        for w in range(len(all_week_names)-1):
#            for i in range(len(all_internships)):
#                for j in range(len(all_internships[i])):
#                    name = f"pennalize_s{s}_w{w}_i{i}_j{j}"
#                    variable = model.NewIntVar(-1, 1, name)
#
#                    # Pennalize changes "in the next week" allocation
#                    model.Add(variable == assignment[(s, w, i, j)] - 
#                              assignment[(s, w+1, i, j)])
#                    model.AddAbsEquality(loss_jumps[idx], variable)
#
#                    idx = idx + 1
#
#
#    # ---
#    # Rule: Enforce priorities
#    # ---
#
#    m = len(all_location_names) # Max loss value
#    loss_priority = []
#
#    # Initialize: Loss list
#    for s in range(len(all_student_names)):
#        for w in range(len(all_week_names)):
#            for i in range(len(all_internships)):
#                for j in range(len(all_internships[i])):
#                    name = f"x_loss_s{s}_w{w}_i{i}_j{i}"
#                    loss_priority.append(model.NewIntVar(0, m, name))
#
#    idx = 0
#    for s in range(len(all_student_names)):
#        for w in range(len(all_week_names)):
#            for i in range(len(all_internships) - delta): # Important
#                for j in range(len(all_internships[i])):
#                    name = f"priority_s{s}_w{w}_i{i}_j{j}"
#                    variable = model.NewIntVar(-m, m, name)
#
#                    # Pennalize difference in priority assignment
#                    model.Add(variable <= assignment[(s, w, i, j)] * 
#                        (j - all_student_priorities[s][i][j]))
#                    model.AddAbsEquality(loss_priority[idx], variable)
#
#                    idx = idx +1
#
#    # ---
#    # Function: Minimize
#    # ---
#
#    model.Minimize( sum(loss_jumps) + sum(loss_priority) )
#
#
#
#    # ====
#    # Invoke the solver
#    # ----
#    solver = cp_model.CpSolver()
#
#    # Set a time limit
#    solver.parameters.max_time_in_seconds = 55 # Max timeout in application
#
#    # Start
#    status = solver.Solve(model)
#
#    return(assignment, solver, status)

def solve_internship(all_location_names, all_location_capacities, 
                     all_student_names, all_week_names, all_internships, 
                     allocation_rule, max_time=55):
    """Solve internship allocation.

    This function solves the allocation task given the following input
    arguments. The function returns a list of indices representing the assigned
    internship for each student.

    Args:
        all_location_names : Array of string.
            A list of available location names.
        all_location_capacities : Array of Array of string.
            A list of capacities (per week) for indices in 'all_location_names'.
        all_student_names : Array of string.
            A list of student names.
        all_week_names : Array of string.
            A list of week names (sorted by time, ASC).
        all_internships : Array of Array of Int.
            Array indexing 'all_location_names' belonging to a 'internship'.
        allocation_rule : Array of int.
            Array of week count following the index of 'all_internships'.
        max_time : Int
            Maximum time for solver in seconds.

    Returns:
        assignment : Dictionary of student allocations.
            Dictionary with a 4d-tuple containing boolean allocation.
        solver : CP-model solver.
            Variable containing the cp-model model solver.
        status : Status for the model solver.
            Variable containing the status of the model solver.

    """
    assignment = {}

    model = cp_model.CpModel()

    # ====
    # Pre-rule: Compensate for missing weeks (weeks w. no allocation)
    # ----
    if len(all_week_names) > sum(allocation_rule):
        dif = len(all_week_names) - sum(allocation_rule)

        # Append a 'not allocated' location
        all_location_names.append("NOT_A_LOCATION")

        # Append infinity capacity
        all_location_capacities.append([999999 for i in range(len(all_week_names))])

        # Append new allocation rule (which must compensate the difference)
        allocation_rule.append(dif)

        # Append new internship
        last_index = len(all_location_names) - 1
        all_internships.append([last_index])


    # ====
    # Initialize: Assignment dictionary
    # ----
    for s in range(len(all_student_names)):
        for w in range(len(all_week_names)):
            for i in range(len(all_internships)):
                for j in range(len(all_internships[i])):
                    name = f"assign_s{s}_w{w}_i{i}_j{j}"
                    assignment[(s, w, i, j)] = model.NewIntVar(0, 1, name)

    # ====
    # Define constrains
    # ----

    # ----
    # Rule: For a given week add add exactly one allocation per student
    # ----
    for s in range(len(all_student_names)):
        for w in range(len(all_week_names)):
            model.AddExactlyOne(assignment[(s, w, i, j)]
                                for i in range(len(all_internships))
                                for j in range(len(all_internships[i])))

    # ----
    # Rule: Any student must follow the allocation rules
    # ----
    for s in range(len(all_student_names)):
        for a, allocation in enumerate(allocation_rule):
            allocated = [assignment[(s, w, a, j)]
                         for w in range(len(all_week_names))
                         for j in range(len(all_internships[a]))]

            model.Add(sum(allocated) == allocation)

    # ----
    # Rule: In any week at any location the capacity constrain must be met
    # ----
    for w in range(len(all_week_names)):
        for i in range(len(all_internships)):
            for j in range(len(all_internships[i])):
                allocated = [assignment[(s, w, i, j)]
                             for s in range(len(all_student_names))]

                # Get all the capacity for a location (if none is defined, set 0)
                _capacities = all_location_capacities[all_internships[i][j]]
                _capacity = _capacities[w] if w < len(_capacities) else 0
                
                model.Add(sum(allocated) <= _capacity)


    # ====
    # Set objectives
    # ----

    loss = []

    # Initialize: Loss list
    for s in range(len(all_student_names)):
        for w in range(len(all_week_names)-1):
            for i in range(len(all_internships)):
                for j in range(len(all_internships[i])):
                    name = f"loss_s{s}_w{w}_i{i}_j{j}"
                    loss.append(model.NewIntVar(0, 1, name))

    # ---
    # Rule: Pennalize 'jumps' in internships
    # ---
    idx = 0

    for s in range(len(all_student_names)):
        for w in range(len(all_week_names)-1):
            for i in range(len(all_internships)):
                for j in range(len(all_internships[i])):
                    name = f"pennalize_s{s}_w{w}_i{i}_j{j}"
                    variable = model.NewIntVar(-1, 1, name)

                    # Pennalize changes "in the next week" allocation
                    model.Add(variable == assignment[(s, w, i, j)] - 
                              assignment[(s, w+1, i, j)])
                    model.AddAbsEquality(loss[idx], variable)

                    idx = idx + 1


    model.Minimize(sum(loss))

    # ====
    # Invoke the solver
    # ----
    solver = cp_model.CpSolver()

    # Set a time limit
    solver.parameters.max_time_in_seconds = max_time

    # Start
    status = solver.Solve(model)

    return(assignment, solver, status)