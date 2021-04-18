from dataclasses import dataclass


class Expression:
    def compute(self):
        pass


class Operation(Expression):
    def __init__(self, value_1, value_2, operation):
        self.number_1 = value_1
        self.number_2 = value_2
        self.operation = operation

    def compute(self):
        operations = {'**': exponentiation, '+': addition, '-': subtraction, '*': multiplication, "/": division}
        if self.operation in operations:
            operation = operations[self.operation]
        else:
            raise ValueError(f"Неподдерживаемая операция {self.operation}")
        self.result = operation(self.number_1, self.number_2)
        return self.result


class Value(Expression):
    def __init__(self, value):
        if is_number(value):
            self.number = float(value)
        else:
            raise ValueError(f"Некорректное значение {value}")

    def compute(self):
        return self.number


class Multiplication(Operation):
    def __init__(self, value_1, value_2):
        super().__init__(value_1, value_2, '*')


class Addition(Operation):
    def __init__(self, value_1, value_2):
        super().__init__(value_1, value_2, '+')


def is_number(string):
    try:
        float(string)
        return True
    except Exception:
        return False


def exponentiation(a, b):
    return a.compute() ** b.compute()


def addition(a, b):
    return a.compute() + b.compute()


def subtraction(a, b):
    return a.compute() - b.compute()


def multiplication(a, b):
    return a.compute() * b.compute()


def division(a, b):
    return a.compute() / b.compute()


@dataclass()
class StateOfCalculator:
    operation_stack: list
    operand_stack: list
    expression: list
    expect_operand: bool = True
    expression_building: bool = False
    open_parenthesis: int = 0
    close_parenthesis: int = 0


def Calculator(expr):
    expr = expression_conversion(expr)
    state = StateOfCalculator([], [], [])
    for i, value in enumerate(expr):
        if value in [' ']:
            pass
        else:
            if state.expect_operand:
                if state.expression_building:
                    expression_building(value, state)
                elif value == '(':
                    state.open_parenthesis += 1
                    state.expression_building = True
                else:
                    state.operand_stack.append(Value(value))
                    state.expect_operand = False
            else:
                if state.operation_stack and\
                        get_priority_of_operation(value) >= get_priority_of_operation(state.operation_stack[-1]):
                    perform_an_operation(state)
                state.expect_operand = True
                state.operation_stack.append(value)
    for operation in state.operation_stack[::-1]:
       perform_an_operation(state, operation)
    return state.operand_stack[0]


def perform_an_operation(state, operation=None):
    number_2 = state.operand_stack.pop()
    number_1 = state.operand_stack.pop()
    if operation == None:
        operation = state.operation_stack.pop()
    state.operand_stack.append(Operation(number_1, number_2, operation))


def reset_state(state):
    state.expression_building = False
    state.close_parenthesis = 0
    state.open_parenthesis = 0
    state.expression = []
    state.expect_operand = False


def expression_building(value, state):
    if value == '(':
        state.open_parenthesis += 1
    elif value == ')':
        state.close_parenthesis += 1
    if state.open_parenthesis == state.close_parenthesis:
        expression = Calculator(''.join(state.expression))
        state.operand_stack.append(expression)
        reset_state(state)
        return
    state.expression.append(value)


def get_priority_of_operation(operation):
    priority_of_operation = [['**'], ['*', '/'], ['+', '-']]
    for i, operations in enumerate(priority_of_operation):
        if operation in operations:
            return i + 1
    raise ValueError(f"Неподдерживаемая операция {operation}")


def expression_conversion(expr):
    expr = list(expr)
    expect_operand = True
    operand = ''
    result = []
    while expr:
        value = expr.pop(0)
        if value in [' ']:
            pass
        elif value in [')', '(']:
            result.append(value)
        elif expect_operand:
            operand += value
            if not is_number(value) and value:
                raise ValueError(f"Некорректное значение {value}")
            if not(expr and is_number(expr[0])):
                result.append(operand)
                operand = ''
                expect_operand = False
        else:
            if value == '*' and expr and expr[0] == '*':
                value += expr.pop(0)
                result.append(value)
            else:
                result.append(value)
            expect_operand = True
    return result


assert Calculator("( 8 * 2 + 4 * 7 ) + ( 3 * 8 + 8 )").compute() == 76
assert Calculator("(1 + 1) ** 6").compute() == 64
assert Calculator("6 + ( 4 * ( 5 + 3 ) / ( 2 ** 4 ) * 7 )").compute() == 20
assert Calculator("6+(4*(5+3)/(2**4)*7)").compute() == 20
assert Calculator("20 * 25").compute() == 500
assert Calculator("30*((5+6)*10)").compute() == 3300