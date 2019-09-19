import csv
import random


def getEquation():
    response = input("Enter equation (ex: Y, Z, ... = /[(A+B)*/C] ): ")

    # check to make sure the user enters the correct number of [] and/or ()
    # assumme user is incompetent
    responseValid = False

    while (not responseValid):
        errors = 0
        if (response.count('[') != response.count(']')):
            print("Scope Error: You missed a closing ']'")
            response = input("Try inputting the equation again: ")
            errors += 1
        if (response.count('(') != response.count(')')):
            print("Scope Error: You missed a closing ')'")
            response = input("Try inputting the equation again: ")
            errors += 1
        if (response.count('=') == 0):
            print("Input Error: You must add the output(s)")
            response = input("Try inputting the equation again: ")
            errors += 1
        if (errors == 0):
            responseValid = True

        # TODO: Add more error detection

    return (response)


def getActivationLevel(eachInput):
    response = input("Is {} Active High? (yes/no): ".format(eachInput))
    responseValid = False
    activeHigh = True
    while (not responseValid):
        if (response == "yes"):
            responseValid = True
        elif (response == 'y'):
            responseValid = True
        elif (response == "no"):
            responseValid = True
            activeHigh = False
        elif (response == 'n'):
            responseValid = True
            activeHigh = False
        else:
            response = input(
                "\nPlease enter yes or no to whether {} is Active High: ".format(eachInput))
    if (activeHigh):
        return 'H'
    else:
        return 'L'


def getOutput(inputs, equation, rowCount):
    executableEquation = "".join(equation)

    for eachInputIndex in range(len(inputs)):
        executableEquation = executableEquation.replace(
            inputs[eachInputIndex], rowCount[eachInputIndex])

    state = eval(executableEquation)

    if (state):
        return 1
    else:
        return 0


def tablePrettyString(table):
    return('\n'.join(['\t'.join([str(cell) for cell in row])
                      for row in table]))


def writeTableToCSV(table, mode, randomInt):

    with open('truthTables_{}.csv'.format(randomInt), mode, newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(table)


def generateTruthTable(equationString):
    equation = []
    inputs = []
    outputs = []
    for eachChar in equationString:
            # eachChar is an input
        if (eachChar.isalpha()):
            # char is either input or output
            charIndex = equationString.find(eachChar)
            equalsIndex = equationString.find('=')
            if (charIndex < equalsIndex):
                outputs.append(eachChar.upper())
            else:
                inputs.append(eachChar.upper())
                equation.append(eachChar.upper())
        # eachChar is a NOT
        elif (eachChar == '/'):
            equation.append(" not ")  # bitwise NOT
        # eachChar is a [ or (
        elif (eachChar == '[' or eachChar == '('):
            equation.append("(")
        # eachChar is a ] or )
        elif (eachChar == ']' or eachChar == ')'):
            equation.append(")")
        # eachChar is a +
        elif (eachChar == '+'):
            equation.append(" or ")  # bitwise OR
        # eachChar is a *
        elif (eachChar == '*'):
            equation.append(" and ")  # bitwise AND

    # inputsActivationLevels = {}
    uniqueInputs = list(set(inputs))
    uniqueInputs.sort()
    numberOfInputs = len(uniqueInputs)
    numberOfRows = 2**(numberOfInputs)  # 2^(inputs)
    truthTable = []
    truthTable.append(uniqueInputs + outputs)

    for eachRowIndex in range(numberOfRows):
        # creates counting order of inputs
        binaryRepresentation = str(bin(eachRowIndex))[2:]

        # must pad more 0's to the left of the MSB

        lengthDifference = numberOfInputs - len(binaryRepresentation)
        binaryRepresentation = binaryRepresentation.zfill(
            len(binaryRepresentation) + lengthDifference)

        rowCount = list(binaryRepresentation)  # 0001, 0010, 0011, etc.
        # get output using equation for all outputs
        output = getOutput(uniqueInputs, equation, rowCount)
        # make column header for each output
        for eachOutput in outputs:
            rowCount.append(output)

        truthTable.append(rowCount)

    return (equation, uniqueInputs, outputs, truthTable)


def generateVoltageTable(equation, uniqueInputs, outputs, truthTable):

    voltageTable = []

    # 1) get the activation levels for all the inputs and outputs
    # **************************************************
    outputsAL = {}
    uniqueInputsAL = {}

    for eachOutput in outputs:
        activationLevel = getActivationLevel(eachOutput)
        outputsAL.update({eachOutput: activationLevel})

    for eachInput in uniqueInputs:
        activationLevel = getActivationLevel(eachInput)
        uniqueInputsAL.update({eachInput: activationLevel})
    # **************************************************

    #  2) format the voltage table header
    # **************************************************

    voltageTableHeader = []
    for eachHeaderChar in truthTable[0]:
        if (eachHeaderChar in uniqueInputs):
            voltageTableHeader.append("{}{}".format(
                eachHeaderChar, "_" + uniqueInputsAL[eachHeaderChar]))
        else:
            voltageTableHeader.append("{}{}".format(
                eachHeaderChar, "_" + outputsAL[eachHeaderChar]))
    voltageTable.append(voltageTableHeader)
    # **************************************************

    # 3) format each row in voltage table in counting order and determine output of voltage table based on activation levels
    # **************************************************

    for eachRow in truthTable[1:]:
        # print(eachRow)

        voltageTableRow = []
        trueVoltageState = []
        # the count of the row in the truth table, ex: 000, 001, 010, etc.
        inputRow = eachRow[:-1]

        for eachRowIndex, eachUniqueInput in enumerate(uniqueInputs):

            truthTableCount = int(inputRow[eachRowIndex])

            # place H or L on each row in voltage table in counting order
            if (truthTableCount == 1):
                voltageTableRow.append('H')
            else:
                voltageTableRow.append('L')

            # setup trueVoltageState to compute output of voltage tabled based on activation levels
            if (truthTableCount == 1 and uniqueInputsAL[eachUniqueInput] == 'H'):
                trueVoltageState.append('1')
            elif (truthTableCount == 1 and uniqueInputsAL[eachUniqueInput] == 'L'):
                trueVoltageState.append('0')
            elif (truthTableCount == 0 and uniqueInputsAL[eachUniqueInput] == 'L'):
                trueVoltageState.append('1')
            elif (truthTableCount == 0 and uniqueInputsAL[eachUniqueInput] == 'H'):
                trueVoltageState.append('0')

        # Output of the voltage table WITHOUT the activation level of the outputs taking into consideration

        tentativeOutput = getOutput(
            uniqueInputs, equation, trueVoltageState)

        # Output of the votlage table WITH the activation levels taken into consideration
        for eachOutput in outputs:
            if (outputsAL[eachOutput] == 'H' and tentativeOutput == 1):
                voltageTableRow.append('H')
            elif (outputsAL[eachOutput] == 'H' and tentativeOutput == 0):
                voltageTableRow.append('L')
            elif (outputsAL[eachOutput] == 'L' and tentativeOutput == 0):
                voltageTableRow.append('H')
            elif (outputsAL[eachOutput] == 'L' and tentativeOutput == 1):
                voltageTableRow.append('L')

        voltageTable.append(voltageTableRow)

    return voltageTable


    # **************************************************
equation = getEquation()
equation, uniqueInputs, outputs, truthTable = generateTruthTable(equation)


voltageTable = generateVoltageTable(
    equation, uniqueInputs, outputs, truthTable)

randomInt = random.randint(1, 100)//2
writeTableToCSV(truthTable, 'w', randomInt)
writeTableToCSV(voltageTable, 'a', randomInt)
