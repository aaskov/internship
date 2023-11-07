# -*- coding: utf-8 -*-
"""Assignment solver for internships.

This module contains the assignment solver for the student allocation problem. 
The assignment solver returns the optimized solution to a given input.

"""
from ortools.sat.python import cp_model


def solve_internship(students, weeks, internships, allocations):
    """Solve internship allocation.

    This function solves the allocation task given the following input
    arguments. The function returns a list of indices representing the assigned
    internship for each student.

    Args:
        students : Array of student identities.
            Array of student identities represented by name or index
        weeks : Array of available weeks for allocation.
            Array of weeks that are available for internship allocations.
        internships : Array of Array of internship and locations.
            Array conatining internship and location relation.
        allocations : Array of int.
            Array defining the allocation rules in relation to the internships.

    Returns:
        bool: The return value. True for success, False otherwise.

    """
    assignment = {}

    model = cp_model.CpModel()

    # Initialize: Assignment dictionary
    for s, student in enumerate(students):
        for w, week in enumerate(weeks):
            for i, internship in enumerate(internships):
                for l, location in enumerate(internship):
                    name = f"assign_s{s}_w{w}_i{i}_l{l}"
                    assignment[(s, w, i, l)] = model.NewIntVar(0, 1, name)

    # ====
    # Define constrains
    # ----

    # ----
    # Rule: For a given week add add exactly one allocation per student
    # ----
    for s, student in enumerate(students):
        for w, week in enumerate(weeks):
            model.AddExactlyOne(assignment[(s, w, i, l)]
                                for i, internship in enumerate(internships)
                                for l, location in enumerate(internship))

    # ----
    # Rule: Any student must follow the allocation rules
    # ----
    for s, student in enumerate(students):
        for a, allocation in enumerate(allocations):
            allocated = [assignment[(s, w, i, l)]
                         for w, _ in enumerate(weeks)
                         for l, _ in enumerate(internships[a])]

            model.Add(sum(allocated) == allocation)

    # ----
    # Rule: In any week at any location the capacity constrain must be met
    # ----
    for w, week in enumerate(weeks):
        for i, internship in enumerate(internships):
            for l, location in enumerate(internship):
                allocated = [assignment[(s, w, i, l)]
                             for s, _ in enumerate(students)]

                model.Add(sum(allocated) <= location[1][w])


    # ====
    # Set objectives
    # ----

    loss = []

    # Initialize: Loss list
    for s in range(len(students)):
        for w in range(len(weeks)-1):
            for i in range(len(internships)):
                for l in range(len(internships[i])):
                    name = f"loss_s{s}_w{w}_i{i}_l{l}"
                    loss.append(model.NewIntVar(0, 1, name))

    # ---
    # Rule: Pennalize 'jumps' in internships
    # ---
    idx = 0

    for s in range(len(students)):
        for w in range(len(weeks)-1):
            for i in range(len(internships)):
                for l in range(len(internships[i])):
                    name = f"pennalize_s{s}_w{w}_i{i}_l{l}"
                    variable = model.NewIntVar(-1, 1, name)

                    # Pennalize changes "in the next week" allocation
                    model.Add(variable == assignment[(s, w, i, l)] - 
                              assignment[(s, w+1, i, l)])
                    model.AddAbsEquality(loss[idx], variable)

                    idx = idx + 1


    model.Minimize(sum(loss))

    # ====
    # Invoke the solver
    # ----
    solver = cp_model.CpSolver()

    # Set a time limit
    solver.parameters.max_time_in_seconds = 60 * 1

    # Start
    status = solver.Solve(model)

    return(assignment, solver, status)
