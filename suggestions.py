import re

def suggest_correction(expression):
    suggestions = []

    # Rule 1: Three or more consecutive arithmetic operators
    if re.search(r'([+\-*/]{3,})', expression):
        suggestions.append("Invalid operator repetition — please check your expression.")

    # Rule 2: Two consecutive arithmetic operators
    operator_pairs = re.findall(r'([+\-*/])([+\-*/])', expression)
    for pair in operator_pairs:
        corrected_expr_1 = expression.replace(f'{pair[0]}{pair[1]}', pair[0])
        corrected_expr_2 = expression.replace(f'{pair[0]}{pair[1]}', pair[1])
        if corrected_expr_1 != expression:
            suggestions.append(f"Did you mean: {corrected_expr_1}?")
        if corrected_expr_2 != expression:
            suggestions.append(f"Did you mean: {corrected_expr_2}?")

    # Rule 3: Expression ends with an operator
    if expression and expression[-1] in "+-*/":
        suggestions.append("Expression ends with an operator — did you forget a number?")

    # Rule 4: Unbalanced parentheses
    if expression.count('(') > expression.count(')'):
        suggestions.append("Missing closing parenthesis.")
    elif expression.count(')') > expression.count('('):
        suggestions.append("Missing opening parenthesis.")

    # Rule 5: Empty parentheses
    if "()" in expression:
        suggestions.append("Empty parentheses detected — did you mean something else?")

    # Rule 6: Unclosed opening parenthesis (redundant but included for clarity)
    if '(' in expression and ')' not in expression:
        suggestions.append("Unclosed parentheses detected.")

    # Rule 7: Operator spacing issue
    if re.search(r'[+\-*/]\s+[+\-*/]', expression):
        suggestions.append("Unexpected operator placement — did you mean a different operation?")

    # Rule 8: Things like `3*+2`
    corrected_expr = re.sub(r'([*/+-])\+', r'\1', expression)
    if corrected_expr != expression:
        suggestions.append(f"Did you mean {corrected_expr}?")

    # Rule 9: Logical operator issues
    if re.search(r'(&{3,}|\|{3,}|!{2,})', expression):
        suggestions.append("Too many logical operators — did you mean '&&', '||', or '!'?")
    if re.search(r'[^&]&[^&]', expression):
        suggestions.append("Single '&' used — did you mean '&&'?")
    if re.search(r'[^\|]\|[^\|]', expression):
        suggestions.append("Single '|' used — did you mean '||'?")

    # --- Conditional statement checks (basic heuristics) ---

    # Rule 10: Missing parentheses in if/while/for conditions (C/Java style)
    if re.search(r'\b(if|while|for)\b\s*[^{(]', expression):
        suggestions.append("Possible missing parentheses around condition in 'if', 'while', or 'for' statement.")

    # Rule 11: Missing colon for Python-style conditionals
    if re.search(r'\b(if|elif|else)\b[^\:]*$', expression.strip()) and not expression.strip().endswith(':'):
        suggestions.append("Missing ':' at the end of the conditional statement.")

    # Rule 12: Common misspellings of conditional keywords
    misspellings = {'iff': 'if', 'elsel': 'else', 'els': 'else', 'eliff': 'elif'}
    for wrong, correct in misspellings.items():
        if re.search(r'\b' + re.escape(wrong) + r'\b', expression):
            suggestions.append(f"Did you mean '{correct}' instead of '{wrong}'?")

    # Rule 13: Dangling else without if
    if re.search(r'^\s*else\b', expression) and not re.search(r'\bif\b', expression):
        suggestions.append("Found 'else' without a preceding 'if'.")

    # Rule 14: Empty or incomplete conditions in if statements
    if re.search(r'\bif\s*\(\s*\)', expression):
        suggestions.append("Empty condition in 'if' statement.")
    if re.search(r'\bif\s*\([^()]*[><=!&|+\-*/]{0}\s*\)', expression):
        suggestions.append("Incomplete condition in 'if' statement.")

    return list(set(suggestions))  # Remove duplicates
