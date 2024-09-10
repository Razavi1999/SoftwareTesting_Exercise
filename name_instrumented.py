from genetic import evaluate_condition


def testfunc3params_instrumente(**args):
    if evaluate_condition(1, 'GtE', args[0], args[1]):
        if evaluate_condition(2, 'GtE', args[1], args[2]):
            return True
    else:
        return False
