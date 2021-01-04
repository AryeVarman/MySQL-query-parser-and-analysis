import math

FILE_NAME = "statistics.txt"

class SchemeNum:
    def __init__(self,number):
        self.number = number


class ElementForOutput(object):
    name = None
    value = None

    def __init__(self,name,value):
        self.name = name
        self.value = value

    def toString(self):
        return self.name + "=" + str(self.value) + " "


class OutputFormat(object):
    operatorName = None
    before = list()       # list of ElementForOutput
    after = list()        # list of ElementForOutput


    def __init__(self,before,after):
        self.before = before
        self.after = after

    def setOutputFormat(self, schemeR, schemeS):
        elementForOutputRlines = ElementForOutput("n_" + schemeR.name, schemeR.numberOfLines)
        elementForOutputRsize = ElementForOutput("R_" + schemeR.name, schemeR.sizeOfLine)
        if schemeS.valid:
            elementForOutputSlines = ElementForOutput("n_" + schemeS.name, schemeS.numberOfLines)
            elementForOutputSsize = ElementForOutput("R_" + schemeS.name, schemeS.sizeOfLine)
            return [elementForOutputRlines, elementForOutputSlines, elementForOutputRsize, elementForOutputSsize]

        return [elementForOutputRlines, elementForOutputRsize]

    def toString(self):
        str = ""
        str += self.operatorName + "\n"
        str += "\t" + "input:"
        for input in self.before:
            str += input.toString()
        str += "\n"
        str += "\t" + "output:"
        for output in self.after:
            str += output.toString()
        str += "\n"

        return str


class AttrFile(object):
    name = None
    size = None
    amount = None

    def __init__(self, name, size):
        self.name = name
        self.size = size

class SchemeFromFile(object):
    name = None
    attrDict = dict()         # dictionary of [attr name : AttrFile]
    sizeOfLine = None         # the number of bytes for one line in the table
    numberOfLines = None
    valid = True

    def __init__(self,dict):
        self.attrDict = dict

    def initiateAttrDict(self, name):
        if name == "R":
            return { "R.A" : AttrFile("A",4),"R.B" : AttrFile("B",4),"R.C" : AttrFile("C",4),"R.D" : AttrFile("D",4),"R.E" : AttrFile("E",4) }
        if name == "S":
            return { "S.D" : AttrFile("D",4),"S.E" : AttrFile("E",4),"S.F" : AttrFile("F",4),"S.H" : AttrFile("H",4),"S.I" : AttrFile("I",4) }

    def makeCartesianAnalysis(self, schemeR, schemeS, schemeNum):
        self.name = "Scheme" + str(schemeNum)
        self.sizeOfLine = schemeR.sizeOfLine + schemeS.sizeOfLine
        self.numberOfLines = schemeR.numberOfLines * schemeS.numberOfLines

        for key in schemeS.attrDict:
            schemeR.attrDict[key] = schemeS.attrDict[key]

        self.attrDict = schemeR.attrDict

        schemeS.valid = False

        return


    def makeNJoinAnalysis(self, schemeR, schemeS, schemeNum):
        self.name = "Scheme" + str(schemeNum)
        percentageR_D = 1 / max(schemeR.attrDict["R.D"].amount, schemeS.attrDict["S.D"].amount)
        percentageR_E = 1 / max(schemeR.attrDict["R.E"].amount, schemeS.attrDict["S.E"].amount)


        Requals = percentageR_D * percentageR_E

        self.numberOfLines = math.ceil(schemeS.numberOfLines * schemeR.numberOfLines * Requals)

        for key in schemeS.attrDict:
            if "R." + key[2] not in schemeR.attrDict:
                schemeR.attrDict[key] = math.ceil(schemeS.attrDict[key].amount * Requals)
            else:
                schemeR.attrDict["R."+key[2]].amount = math.ceil(schemeR.attrDict["R."+key[2]].amount * Requals)

        self.attrDict = schemeR.attrDict

        self.sizeOfLine = len(self.attrDict) * 4

        schemeS.valid = False

        return


    def makePiAnalysis(self, schemeR, schemeS, pi, schemeNum):
        self.name = "Scheme" + str(schemeNum)
        self.numberOfLines = schemeR.numberOfLines

        newDict = dict()

        for key in schemeR.attrDict:
            for piNode in pi.colList:
                if key == piNode.tableName + "." + piNode.colName:
                    newDict[key] = schemeR.attrDict[key]

        self.attrDict = newDict
        self.sizeOfLine = len(self.attrDict) * 4

        return


def readSchemeFromFile(file):
    scheme = SchemeFromFile(dict())
    schemeNameStr = file.readline()
    scheme.name = schemeNameStr[len(schemeNameStr)-2]
    scheme.attrDict = scheme.initiateAttrDict(scheme.name)
    file.readline()
    numOfLinesStr = file.readline()
    numOfLinesStr = numOfLinesStr.partition("=")[2].strip()
    scheme.numberOfLines = int(numOfLinesStr)
    scheme.sizeOfLine = 20

    for i in range(0,5):
        attrInfoStr = file.readline()
        attrName = attrInfoStr[2]
        attrAmountInScheme = attrInfoStr.partition("=")[2].strip()
        scheme.attrDict[scheme.name + "." + attrName].amount = int(attrAmountInScheme)

    return scheme


def initiateSchemeFromFile():
    file = open(FILE_NAME, "r")
    schemeOneFromFile = readSchemeFromFile(file)
    file.readline()     # read empty line
    schemeTwoFromFile = readSchemeFromFile(file)

    return [schemeOneFromFile,schemeTwoFromFile]