class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type  # 'operator' or 'operand'
        self.value = value  # The operator or condition value
        self.left = left  # Left child node
        self.right = right  # Right child node

    def to_dict(self):
        return {
            'type': self.type,
            'value': self.value,
            'left': self.left.to_dict() if self.left else None,
            'right': self.right.to_dict() if self.right else None
        }

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        return cls(
            type=data['type'],
            value=data['value'],
            left=cls.from_dict(data['left']),
            right=cls.from_dict(data['right'])
        )

def validate_rule_string(rule_string, valid_attributes):
    tokens = rule_string.replace('(', ' ( ').replace(')', ' ) ').split()
    # Basic validation for correct tokens
    if len(tokens) < 3 or tokens[1] not in ['>', '<', '=', 'AND', 'OR']:
        return False
    if tokens[0] not in valid_attributes:
        return False
    return True

def parse_rule_string(rule_string):
    tokens = rule_string.replace('(', ' ( ').replace(')', ' ) ').split()

    def parse_expression():
        stack = [[]]
        for token in tokens:
            if token == '(':
                stack.append([])
            elif token == ')':
                expr = stack.pop()
                stack[-1].append(expr)
            elif token in ['AND', 'OR']:
                stack[-1].append(token)
            else:
                stack[-1].append(token)

        def build_tree(expr):
            if isinstance(expr, list):
                if len(expr) == 1:
                    return build_tree(expr[0])
                elif 'OR' in expr:
                    idx = expr.index('OR')
                    return Node('operator', 'OR', build_tree(expr[:idx]), build_tree(expr[idx+1:]))
                elif 'AND' in expr:
                    idx = expr.index('AND')
                    return Node('operator', 'AND', build_tree(expr[:idx]), build_tree(expr[idx+1:]))
            return Node('operand', ' '.join(expr))

        return build_tree(stack[0])

    return parse_expression()
