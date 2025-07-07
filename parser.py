class ASTNode:
    def __init__(self, type_, value=None, left=None, right=None, condition=None, true_branch=None, false_branch=None):
        self.type = type_
        self.value = value
        self.left = left
        self.right = right
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def __repr__(self):
        if self.type == "IF":
            return f"IF({self.condition}, {self.true_branch}, {self.false_branch})"
        if self.value is not None and not self.left and not self.right:
            return f"{self.type}({self.value})"
        return f"{self.type}({self.left}, {self.right})"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self, expected_type):
        token = self.current_token()
        if token and token[0] == expected_type:
            self.pos += 1
            return token
        return None

    def parse(self):
        node = self.conditional_expr()
        if self.pos < len(self.tokens):
            raise SyntaxError(f"Unexpected token at end: {self.tokens[self.pos]}")
        return node

    def conditional_expr(self):
        # Check for "if" expression
        if self.current_token() and self.current_token()[0] == 'IF':
            self.eat('IF')
            condition = self.or_expr()
            if not self.eat('THEN'):
                raise SyntaxError("Expected 'then' after 'if' condition")
            true_branch = self.or_expr()
            if not self.eat('ELSE'):
                raise SyntaxError("Expected 'else' after 'then' branch")
            false_branch = self.or_expr()
            return ASTNode('IF', condition=condition, true_branch=true_branch, false_branch=false_branch)
        else:
            return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.current_token() and self.current_token()[0] == 'OR':
            op = self.eat('OR')
            right = self.and_expr()
            node = ASTNode('OR', op[1], node, right)
        return node

    def and_expr(self):
        node = self.equality_expr()
        while self.current_token() and self.current_token()[0] == 'AND':
            op = self.eat('AND')
            right = self.equality_expr()
            node = ASTNode('AND', op[1], node, right)
        return node

    def equality_expr(self):
        node = self.comparison_expr()
        while self.current_token() and self.current_token()[0] in ('EQ', 'NEQ'):
            op = self.eat(self.current_token()[0])
            right = self.comparison_expr()
            node = ASTNode(op[0], op[1], node, right)
        return node

    def comparison_expr(self):
        node = self.expr()
        while self.current_token() and self.current_token()[0] in ('GT', 'GTE', 'LT', 'LTE'):
            op = self.eat(self.current_token()[0])
            right = self.expr()
            node = ASTNode(op[0], op[1], node, right)
        return node

    def expr(self):
        node = self.term()
        while self.current_token() and self.current_token()[0] in ('ADD', 'SUB'):
            op = self.eat(self.current_token()[0])
            right = self.term()
            node = ASTNode(op[0], op[1], node, right)
        return node

    def term(self):
        node = self.factor()
        while self.current_token() and self.current_token()[0] in ('MUL', 'DIV'):
            op = self.eat(self.current_token()[0])
            right = self.factor()
            node = ASTNode(op[0], op[1], node, right)
        return node

    def factor(self):
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of expression")

        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return ASTNode('Number', token[1])
        elif token[0] == 'NOT':
            self.eat('NOT')
            node = self.factor()
            return ASTNode('NOT', '!', node)
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            node = self.conditional_expr()
            if not self.eat('RPAREN'):
                raise SyntaxError("Missing closing parenthesis")
            return node
        else:
            raise SyntaxError(f"Unexpected token: {token}")
