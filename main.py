class CompilationError(Exception):
    pass

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return "Token({0}, {1!r})".format(self.type, self.value)

def new_token(char):
    if char.isspace():
        return None
    elif char in "(":
        return Token("BEGIN_BRACKET", char)
    elif char in ")":
        return Token("END_BRACKET", char)
    elif char in "+-*/":
        return Token("OP", char)
    elif char.isdigit():
        return Token("NUMBER", char)
    else:
        raise CompilationError("Unknown character: \"{0}\"".format(char))

def continue_token(current, char):
    if current.type == "NUMBER":
        if char.isdigit():
            current.value += char
            return True
        else:
            return False
    elif current.type == "OP":
        return False
    elif current.type == "BRACKET":
        return False

def parse(s):
    tokens = []

    current_token = None

    for i in s:
        if current_token is None:
            current_token = new_token(i)
        else:
            if not continue_token(current_token, i):
                tokens.append(current_token)
                current_token = new_token(i)

    if current_token is not None:
        tokens.append(current_token)

    for i in tokens:
        if i.type == "NUMBER":
            i.value = int(i.value)
    
    return tokens

def create_groups_by_priority(group):
    operations = ["*/", "+-"]
    for op in operations:
        i = 0
        while i < len(group):
            v = group[i]
            if isinstance(v, Token) and v.type == "OP" and v.value in op:
                if i == 0 or i == len(group) - 1:
                    raise CompilationError("No argument for operation")
                group[i - 1:i + 2] = [[group[i - 1], group[i], group[i + 1]]]
            i += 1

def build_tree(tokens):
    group_stack = []
    current_group = []

    for i in tokens:
        if i.type == "BEGIN_BRACKET":
            group_stack.append(current_group)
            current_group = []
        elif i.type == "END_BRACKET":
            if len(group_stack) == 0:
                raise CompilationError("Wrong closing bracket")
            else:
                if len(current_group) == 1:
                    current_group = current_group[0]
                else:
                    create_groups_by_priority(current_group)
                group_stack[-1].append(current_group)
                current_group = group_stack.pop()
        else:
            current_group.append(i)

    if len(group_stack) > 0:
        raise CompilationError("Not enough closing brackets")

    create_groups_by_priority(current_group)

    return current_group

def print_node(node, depth):
    if isinstance(node, Token):
        if node.type in {"OP", "NUMBER"}:
            print(" " * (4 * depth) + str(node.value))
        else:
            print(" " * (4 * depth) + str(node))
    else:
        print_tree(node, depth)

def print_tree(tree, depth=0):
    print(" " * (4 * depth) + "[")
    for i in tree:
        print_node(i, depth + 1)
    print(" " * (4 * depth) + "]")

def execute(tree):
    if isinstance(tree, Token):
        if tree.type == "NUMBER":
            return tree.value
        else:
            raise CompilationError("Unexpected token")
    else:
        if len(tree) == 1:
            return execute(tree[0])
        elif len(tree) != 3:
            raise CompilationError("Not enough operations")
        else:
            tree[0] = execute(tree[0])
            tree[2] = execute(tree[2])

        if isinstance(tree[1], Token) and tree[1].type == "OP":
            if tree[1].value == "+":
                return tree[0] + tree[2]
            elif tree[1].value == "-":
                return tree[0] - tree[2]
            elif tree[1].value == "*":
                return tree[0] * tree[2]
            elif tree[1].value == "/":
                return tree[0] / tree[2]
        else:
            raise CompilationError("Unexpected token")

try:
    expr = input("Expression: ")
    tokens = parse(expr)
    tree = build_tree(tokens)
    print_tree(tree)
    print("Result: ", execute(tree))
except CompilationError as e:
    print("Compilation error: {0}".format(e))
