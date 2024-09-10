def write_to_file(path, replacement, parameters):
    write_text = replacement

    new_parameters = {}
    counter = 0
    for each in parameters:
        new_parameters[each] = 'args[' + str(counter) + ']'
        counter = counter + 1

    print(new_parameters)

    with open(path, 'r') as data_file:
        for line in data_file:
            data = line.split()

            if not line.__contains__("def "):
                for each in line.split(' '):
                    # print(f'each : {each}')
                    for item in new_parameters.keys():
                        flag = False

                        if each.__contains__(item):
                            flag = True

                            if each.__contains__(','):
                                write_text += new_parameters[item] + ','

                            elif each.__contains__('):'):
                                write_text += new_parameters[item] + '):\n'

                            else:
                                write_text += new_parameters[item] + ' '

                            break

                    if not flag:
                        write_text += each + ' '


    #print(write_text)

    with open(path, 'r+') as write_file:
        write_file.truncate(0)

    with open(path, 'r+') as f:
        f.write(write_text)


def analysis(path):
    branches = []
    parameters = []

    branch_count = 0
    param_count = 0

    with open(path, 'r') as data_file:
        for line in data_file:
            # f = data_file.readline()
            data = line.split()

            if data.__contains__("def"):
                replacement = "def "
                # print(data)

                for each in data[1:]:
                    openBrakets = each.find("(")
                    closeBrakets = each.find(")")
                    comma = each.find(',')

                    # print(each)
                    # print(f'openBrakets : {openBrakets}  , closeBrakets : {closeBrakets} , comma : {comma}')

                    if openBrakets > 0 and closeBrakets < 0 and comma > 0:
                        first = openBrakets + 1
                        parameters.append(each[openBrakets + 1: comma])
                        param_count = param_count + 1
                        replacement += each[0: openBrakets - 1]
                        replacement += "(**args):  \n"
                        # print(f'replacement : {replacement}')

                    elif openBrakets < 0 and closeBrakets < 0 and comma > 0:
                        parameters.append(each[0: comma])
                        param_count = param_count + 1

                    elif openBrakets < 0 and closeBrakets > 0 and comma < 0:
                        second = closeBrakets - 1
                        parameters.append(each[0: closeBrakets])
                        param_count = param_count + 1

            for each in data:
                # print(each)
                if each.__contains__("evaluate_condition"):
                    branch_count = branch_count + 1
                    branches.append(branch_count)

    write_to_file(path, replacement, parameters)
    return parameters, branches
