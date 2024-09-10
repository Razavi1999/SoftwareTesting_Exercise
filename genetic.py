import ast
import sys
import inspect
import astor
import random
import math
import matplotlib.pyplot as plt

from analysis_instrumented import analysis
from name_instrumented import testfunc3params_instrumente
from testfunc_instrumented import testfunc_instrumented

distances_true = {}
distances_false = {}
best_of_generations = []


def update_maps(condition_num, d_true, d_false):
    global distances_true, distances_false

    if condition_num in distances_true.keys():
        distances_true[condition_num] = min(
            distances_true[condition_num], d_true)
    else:
        distances_true[condition_num] = d_true

    if condition_num in distances_false.keys():
        distances_false[condition_num] = min(
            distances_false[condition_num], d_false)
    else:
        distances_false[condition_num] = d_false


def evaluate_condition(num, op, lhs, rhs):
    distance_true = 0
    distance_false = 0

    if isinstance(lhs, str):
        lhs = ord(lhs)
    if isinstance(rhs, str):
        rhs = ord(rhs)

    if op == "Eq":
        if lhs == rhs:
            distance_false = 1
        else:
            distance_true = abs(lhs - rhs)


    elif op == "NotEq":
        if lhs != rhs:
            distance_false = abs(lhs - rhs)
        else:
            distance_true = 1

    elif op == "Lt":
        if lhs < rhs:
            distance_false = rhs - lhs
        else:
            distance_true = lhs - rhs + 1

    elif op == "LtE":
        if lhs <= rhs:
            distance_false = rhs - lhs + 1
        else:
            distance_true = lhs - rhs

    elif op == "Gt":
        if lhs > rhs:
            distance_false = lhs - rhs
        else:
            distance_true = rhs - lhs + 1

    elif op == "GtE":
        if lhs >= rhs:
            distance_false = lhs - rhs + 1
        else:
            distance_true = rhs - lhs

    elif op == "In":
        minimum = sys.maxsize
        for elem in rhs.keys():
            distance = abs(lhs - ord(elem))
            if distance < minimum:
                minimum = distance

        distance_true = minimum
        if distance_true == 0:
            distance_false = 1

    update_maps(num, distance_true, distance_false)

    if distance_true == 0:
        return True
    else:
        return False


class BranchTransformer(ast.NodeTransformer):
    branch_num = 0

    def visit_FunctionDef(self, node):
        node.name = node.name + "_instrumented"
        return self.generic_visit(node)

    def visit_Compare(self, node):
        if node.ops[0] in [ast.Is, ast.IsNot, ast.In, ast.NotIn]:
            return node

        self.branch_num += 1
        return ast.Call(func=ast.Name("evaluate_condition", ast.Load()),
                        args=[ast.Num(self.branch_num), ast.Str(node.ops[0].__class__.__name__), node.left,
                              node.comparators[0]], keywords=[], starargs=None, kwargs=None)


def save_as_instrumented_python(instrumented, name):
    file = open("{}_instrumented.py".format(name), "w")
    file.write("{}".format(instrumented))
    file.close()


def instrument_extraction(func):
    source = inspect.getsource(func)
    node = ast.parse(source)
    BranchTransformer().visit(node)
    node = ast.fix_missing_locations(node)
    save_as_instrumented_python(astor.to_source(node), "name")


def create_instrumented_function(func):
    source = inspect.getsource(func)
    node = ast.parse(source)
    node = BranchTransformer().visit(node)
    node = ast.fix_missing_locations(node)
    current_module = sys.modules[__name__]
    code = compile(node, filename="<ast>", mode="exec")
    exec(code, current_module.__dict__)


def normalize(x):
    return x / (1.0 + x)


def get_fitness_nParameters(parameters, branches):
    global distances_true, distances_false
    distances_true = {}
    distances_false = {}

    try:
        # here should be changed
        testfunc3params_instrumente(parameters)

    except BaseException:
        pass

    fitness = 0.0
    for branch in branches:
        if branch in distances_true:
            fitness += normalize(distances_true[branch])
        else:
            fitness += 1.0

    return fitness


def get_fitness(x, y):
    # Reset any distance values from previous executions
    global distances_true, distances_false
    distances_true = {}
    distances_false = {}
    # Run the function under test
    try:
        testfunc_instrumented(x, y)
    except BaseException:
        pass
    # Sum up branch distances
    fitness = 0.0
    for branch in [1, 2, 3, 4, 5]:
        if branch in distances_true:
            fitness += normalize(distances_true[branch])
        else:
            fitness += 1.0

    for branch in []:
        if branch in distances_false:
            fitness += normalize(distances_false[branch])
        else:
            fitness += 1.0

    return fitness


##########################################################
################ GENETIC ALGORITHM #######################
##########################################################
def create_population(size, minn, maxx):
    return [[random.uniform(minn, maxx), random.uniform(minn, maxx)] for i in range(size)]


def create_population2(size, minn, maxx, nparams):
    return [[random.uniform(minn, maxx) for item in range(nparams)] for j in range(size)]


def evaluate_population(population , branches):
    fitness = [get_fitness_nParameters(item , branches) for item in population]
    return list(zip(population, fitness))


def selection(evaluated_population, tournament_size):
    competition = random.sample(evaluated_population, tournament_size)
    winner = min(competition, key=lambda item: item[1])
    return winner[:]


def crossover(parent1, parent2):
    pos = random.randint(1, len(parent1))
    offspring1 = parent1[:pos] + parent2[pos:]
    offspring2 = parent2[:pos] + parent1[pos:]
    return offspring1, offspring2


def mutate(chromosome, minn, maxx):
    mutated = chromosome[:]
    P = 1.0 / len(mutated)
    for pos in range(len(mutated)):
        if random.random() < P:
            mutated[pos] = random.uniform(minn, maxx)
    return mutated


def genetic_algorithm(npop, ngen, minn, maxx, nparams , branches ):
    generation = 0
    population = create_population2(npop, minn, maxx, nparams)
    print(population)
    fitness = evaluate_population(population , branches)
    best = min(fitness, key=lambda item: item[1])
    best_individual = best[0]
    best_fitness = best[1]
    print("Best fitness of initial population: {a} - {b} ".format(a=best_individual, b=best_fitness))

    while generation < ngen:
        new_population = []
        while len(new_population) < len(population):
            # Selection
            offspring1 = selection(fitness, 10)
            offspring2 = selection(fitness, 10)
            # Crossover
            offspring1 = offspring1[0]
            offspring2 = offspring2[0]
            if random.random() < 0.7:
                (offspring1, offspring2) = crossover(offspring1, offspring2)
            # Mutation
            offspring1 = mutate(offspring1, minn, maxx)
            offspring2 = mutate(offspring2, minn, maxx)

            new_population.append(offspring1)
            new_population.append(offspring2)

        generation += 1
        population = new_population
        fitness = evaluate_population(population , branches)
        print(fitness)
        for i in fitness:
            if i[1] == 0:
                best_of_generations.append(i[0])

        best = min(fitness, key=lambda item: item[1])
        best_individual = best[0]
        best_fitness = best[1]
        # best_of_generations.append(best[0])

        print("Best fitness at generation {a}: {b} - {c}".format(a=generation, b=best_individual, c=best_fitness))
    print("Best individual: {a}, fitness {b}".format(a=best_individual, b=best_fitness))


##############################################################################
##############################################################################
def testfunc(x, y):
    if x >= 0 and y >= 0:
        if y * y >= x * 10 and y <= math.sin(math.radians(x * 30)) * 25:
            if y >= math.cos(math.radians(x * 40)) * 15:
                print('oooookk')


def testfunc2(x, y):
    return x > y


def testfunc3params(param1, param2, param3):
    if param1 >= param2:
        if param2 >= param3:
            return True

    else:
        return False


def testfunc4params(param1, param2, param3, param4):
    return param1 >= param2 >= param3 >= param4


instrument_extraction(testfunc3params)
create_instrumented_function(testfunc3params)

parameters, branches = analysis("/home/mahdi/PycharmProjects/pythonProject/name_instrumented.py")

a = get_fitness(20, 19)
b = distances_true
c = distances_false

genetic_algorithm(npop=40, ngen=15000, minn=-100, maxx=100, nparams=len(parameters), branches=branches)
x = []
y = []
print("best of all generations:", best_of_generations)
for i in best_of_generations:
    x.append(i[0])
    y.append(i[1])

plt.plot(x, y, 'bo')

plt.show()
