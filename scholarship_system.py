import ast
import json
import math
import operator
import sys

results = {}
MERIT_FORMULA = "gpa * 10 + credits * 2"
INCOME_LIMIT = 800000
CUTOFF = 85

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def safe_eval(node, variables):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body, variables)
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.Name) and node.id in variables:
        return variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = safe_eval(node.left, variables)
        right = safe_eval(node.right, variables)
        return OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -safe_eval(node.operand, variables)
    raise ValueError("unsupported expression")

def calculate_merit_score(gpa, credits):
    tree = ast.parse(MERIT_FORMULA, mode="eval")
    return safe_eval(tree, {"gpa": gpa, "credits": credits})

def evaluate_applicant(student_id, test_scores, logs=[]):
    gpa = test_scores["gpa"]
    credits = test_scores.get("credits", 0)
    income = test_scores.get("income", 0)
    score = calculate_merit_score(gpa, credits)
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    results[student_id] = {"score": score, "eligible": eligible}
    logs.append("%s scored %s" % (student_id, score))
    return eligible

def change_formula(new_formula):
    global MERIT_FORMULA
    try:
        tree = ast.parse(new_formula, mode="eval")
        safe_eval(tree, {"gpa": 1, "credits": 1})
    except (SyntaxError, ValueError, ZeroDivisionError):
        return False
    MERIT_FORMULA = new_formula
    return True

def persist_results(file="scholarships.json"):
    f = open(file, "w")
    f.write(json.dumps(results))
    f.close()

def load_results(file="scholarships.json"):
    global results
    try:
        results = json.loads(open(file).read())
    except (OSError, json.JSONDecodeError):
        print("No saved results loaded")

def printShortlist():
    print("Shortlisted applicants:")
    for r in results:
        if results[r]["eligible"] == True:
            print(" ", r, "score =", results[r]["score"])

def main():
    evaluate_applicant("U001", {"gpa": 9.1, "credits": 4, "income": 450000})
    evaluate_applicant("U002", {"gpa": 7.2, "credits": 1, "income": 300000})
    evaluate_applicant("U003", {"gpa": 12.5, "credits": -3, "income": -1})
    evaluate_applicant("U004", {"gpa": 6.5})
    formula = input("Merit formula (Enter to keep default): ")
    if formula and not change_formula(formula):
        print("Invalid formula, keeping the default")
    evaluate_applicant("U005", {"gpa": 8.4, "credits": 3, "income": 600000})
    persist_results()
    load_results()
    printShortlist()

main()