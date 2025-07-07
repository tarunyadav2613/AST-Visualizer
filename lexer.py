# Part 3: Add Conditional Keywords

# Final Token types
TOKEN_SPECIFICATION = [
    ('NUMBER',   r'\d+'),
    ('AND',      r'&&'),
    ('OR',       r'\|\|'),
    ('NOT',      r'!'),
    ('EQ',       r'=='),
    ('NEQ',      r'!='),
    ('GTE',      r'>='),
    ('LTE',      r'<='),
    ('GT',       r'>'),
    ('LT',       r'<'),
    ('ADD',      r'\+'),
    ('SUB',      r'-'),
    ('MUL',      r'\*'),
    ('DIV',      r'/'),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('IF',       r'if'),
    ('THEN',     r'then'),
    ('ELSE',     r'else'),
    ('SKIP',     r'[ \t]+'),
    ('MISMATCH', r'.'),
]

TOKEN_REGEX = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in TOKEN_SPECIFICATION)

def tokenize(expression):
    tokens = []
    for match in re.finditer(TOKEN_REGEX, expression):
        kind = match.lastgroup
        value = match.group()
        if kind == 'NUMBER':
            tokens.append(('NUMBER', int(value)))
        elif kind in ('ADD', 'SUB', 'MUL', 'DIV', 'LPAREN', 'RPAREN',
                      'AND', 'OR', 'NOT', 'EQ', 'NEQ', 'GT', 'LT', 'GTE', 'LTE',
                      'IF', 'THEN', 'ELSE'):
            tokens.append((kind, value))
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f'Unexpected token: {value}')
    return tokens
