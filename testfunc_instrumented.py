import math



def testfunc_instrumented(x, y):
    if evaluate_condition(1, 'GtE', x, 0) and evaluate_condition(2, 'GtE', y, 0):
        if evaluate_condition(3, 'GtE', y * y, x * 10) and evaluate_condition(4, 'LtE', y, math.sin(math.radians(x * 30)) * 25):
            if evaluate_condition(5, 'GtE', y, math.cos(math.radians(x * 40)) * 15):
                print('Ok')
