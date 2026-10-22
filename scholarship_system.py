"""Student scholarship eligibility screener."""
import ast
import json
import operator

RESULTS = {}
SETTINGS = {"formula": "gpa * 10 + credits * 2"}
INCOME_LIMIT = 800000
CUTOFF = 85
MAX_GPA = 10.0

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def safe_eval(node, variables):
    """Evaluate a restricted arithmetic expression tree."""
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


def calculate_merit_score(gpa, activity_credits):
    """Return the merit score using the active formula."""
    tree = ast.parse(SETTINGS["formula"], mode="eval")
    return safe_eval(tree, {"gpa": gpa, "credits": activity_credits})


def validate_scores(test_scores):
    """Return validated (gpa, credits, income) or raise ValueError."""
    gpa = test_scores.get("gpa")
    activity_credits = test_scores.get("credits", 0)
    income = test_scores.get("income")
    if gpa is None or not 0 <= gpa <= MAX_GPA:
        raise ValueError("gpa must be between 0 and 10")
    if activity_credits < 0:
        raise ValueError("credits cannot be negative")
    if income is None or income < 0:
        raise ValueError("income is missing or negative")
    return gpa, activity_credits, income


def evaluate_applicant(student_id, test_scores, logs=None):
    """Score one applicant and record the result."""
    if logs is None:
        logs = []
    gpa, activity_credits, income = validate_scores(test_scores)
    score = calculate_merit_score(gpa, activity_credits)
    eligible = score >= CUTOFF and income < INCOME_LIMIT
    RESULTS[student_id] = {"score": score, "eligible": eligible}
    logs.append(f"{student_id} scored {score}")
    return eligible


def change_formula(new_formula):
    """Switch to a new formula if it is a valid arithmetic expression."""
    try:
        tree = ast.parse(new_formula, mode="eval")
        safe_eval(tree, {"gpa": 1, "credits": 1})
    except (SyntaxError, ValueError, ZeroDivisionError):
        return False
    SETTINGS["formula"] = new_formula
    return True


def persist_results(file="scholarships.json"):
    """Write results to a JSON file."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(RESULTS, handle)


def load_results(file="scholarships.json"):
    """Load results from a JSON file if it exists and is valid."""
    try:
        with open(file, encoding="utf-8") as handle:
            loaded = json.load(handle)
    except (OSError, json.JSONDecodeError):
        print("No saved results loaded")
        return
    RESULTS.clear()
    RESULTS.update(loaded)


def print_shortlist():
    """Print every eligible applicant."""
    print("Shortlisted applicants:")
    for student_id, record in RESULTS.items():
        if record["eligible"]:
            print(" ", student_id, "score =", record["score"])


def main():
    """Run the screener."""
    formula = input("Merit formula (Enter to keep default): ")
    if formula and not change_formula(formula):
        print("Invalid formula, keeping the default")
    applicants = [
        ("U001", {"gpa": 9.1, "credits": 4, "income": 450000}),
        ("U002", {"gpa": 7.2, "credits": 1, "income": 300000}),
        ("U003", {"gpa": 12.5, "credits": -3, "income": -1}),
        ("U004", {"gpa": 6.5}),
        ("U005", {"gpa": 8.4, "credits": 3, "income": 600000}),
    ]
    for student_id, scores in applicants:
        try:
            evaluate_applicant(student_id, scores)
        except ValueError as error:
            print(f"Rejected {student_id}: {error}")
    persist_results()
    load_results()
    print_shortlist()


if __name__ == "__main__":
    main()
