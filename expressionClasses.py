import collections
import math

from fileClasses import OutputFormat, SchemeNum

FROM = "FROM"
WHERE = "WHERE"
SELECT = "SELECT"
DISTINCT = "DISTINCT"

OR = "OR"
AND = "AND"

isDISTINCT = False

R_Attr = ['A', 'B', 'C', 'D', 'E']
S_Attr = ['D', 'E', 'F', 'H', 'I']

GLOBAL_R_ATTR_DICT = dict()
GLOBAL_S_ATTR_DICT = dict()

# node in the sigma tree expression
class SigmaTreeNode(object):

    def __init__(self, data=None):
        self.data = data
        self.left = None
        self.right = None

    def toString(self, str):
        str += "("
        if self.left is None and self.right is None:
            str += self.data + ")"
            return str

        if self.left is not None:
            str = self.left.toString(str)

        str += self.data

        if self.right is not None:
            str = self.right.toString(str)

        str += ")"
        return str

# the tree that represent the sigma expression
class SigmaTree(object):

    def __init__(self, root=None):
        if root is None:
            self.root = SigmaTreeNode()
        else:
            self.root = root

    def toString(self):
        if self.root is not None:
            return self.root.toString("")

# node in the query expression tree
class ExpressionTreeNode(object):

    def __init__(self, data=None):
        self.data = data
        self.children = collections.deque()

    def toString(self):
        if len(self.children) == 0:
            return self.data.toString()

        str = "("

        for node in self.children:
            str += node.toString() + ","

        str += ")"
        str = self.data.toString() + str
        return str

# query expression tree
class ExpressionTree(object):

    def __init__(self, root=None):
        if root is None:
            self.root = ExpressionTreeNode()
        else:
            self.root = root

    def toString(self):
        if self.root is not None:
            str = self.root.toString()
            str = str.replace(",)", ")")
            str = str.replace("()", "")
            return str

class ProbElement:

    def __init__(self, cond, num):
        self.cond = cond
        self.num = num

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def calaulateProb(simpleCondition, scheme):
    rightSide = simpleCondition.partition("=")[2].strip()
    leftSide = simpleCondition.partition("=")[0].strip()
    if is_number(leftSide) and is_number(rightSide):
        if leftSide == rightSide:
            prob = 1
        else: prob = 0
    elif is_number(leftSide) or is_number(rightSide):
        if is_number(leftSide):
            prob = 1 / scheme.attrDict[rightSide].amount
        else: prob = 1 / scheme.attrDict[leftSide].amount
    else:
        if rightSide == leftSide:
            prob = 1
        else:
            prob = 1 / max(scheme.attrDict[rightSide].amount, scheme.attrDict[leftSide].amount)

    probElement = ProbElement(simpleCondition, prob)
    return probElement


def analysSigmaTreeRec(root, scheme, leftVal, rightVal, probElement):
    if root.left is None and root.right is None:
        return calaulateProb(root.data,scheme)

    if root.left is not None:
        leftVal = analysSigmaTreeRec(root.left, scheme, leftVal, rightVal, probElement)
    if root.right is not None:
        rightVal = analysSigmaTreeRec(root.right, scheme, leftVal, rightVal, probElement)

    if root.data == AND and  leftVal != rightVal:
        return ProbElement(leftVal.cond + " AND " + rightVal.cond, leftVal.num * rightVal.num)

    if root.data == OR and  leftVal != rightVal:
        return ProbElement(leftVal.cond + " OR " + rightVal.cond, leftVal.num + rightVal.num)

    if  leftVal == rightVal:
        return ProbElement(leftVal.cond, leftVal.num)


def analysSpesificSigmaTree(root, scheme, schemeNum):
    scheme.name = "Scheme" + str(schemeNum)
    probElement = analysSigmaTreeRec(root, scheme, "", "", ProbElement("", ""))

    scheme.numberOfLines = math.ceil(probElement.num * scheme.numberOfLines)

    return


def analysSigmaTree(sigma, schemeR, schemeS, rightChild, number):

    outputFormat = OutputFormat(list(), list())
    inputList = outputFormat.setOutputFormat(schemeR, schemeS)
    outputFormat.before = inputList

    if sigma.haveRowInTheEnd:
        outputFormat.operatorName = sigma.toString()
        if sigma.rowInTheEnd == "R":
            analysSpesificSigmaTree(sigma.conditionTree.root, schemeR, number)

        if sigma.rowInTheEnd == "S":
            analysSpesificSigmaTree(sigma.conditionTree.root, schemeS, number)

    elif rightChild:
        outputFormat.operatorName = sigma.toString() + "(S)"
        analysSpesificSigmaTree(sigma.conditionTree.root, schemeS, number)
    else:
        outputFormat.operatorName = sigma.toString() + "(R)"
        analysSpesificSigmaTree(sigma.conditionTree.root, schemeR, number)

    return outputFormat


# the query expression class (main class of project)
class AlgebraicExpression(object):

    def __init__(self, expressionArray):
        self.expressionTree = ExpressionTree()

        pi = ExpressionTreeNode(expressionArray[0])
        sigma = ExpressionTreeNode(expressionArray[1])
        cartesian = ExpressionTreeNode(expressionArray[2])

        if len(cartesian.data.tableList) > 1:
            for table in cartesian.data.tableList:
                node = ExpressionTreeNode(Table(table))
                cartesian.children.append(node)
            sigma.children.append(cartesian)
        else:
            sigma.data.haveRowInTheEnd = True
            sigma.data.rowInTheEnd = cartesian.data.tableList[0]

        self.expressionTree.root = pi
        pi.children.append(sigma)

    def toString(self):
        if self.expressionTree is not None:
            return self.expressionTree.toString()

    # Sigma[P1 AND P2](R) = Sigma[P1]( Sigma[P2](R) )
    def rule4(self):
        return self.__rule4(self.expressionTree.root, None, True)

    # recursive function of rule 4
    def __rule4(self, root, father, notFound):
        if root is None:
            return

        if isinstance(root.data, Sigma):
            if root.data.conditionTree.root.data == AND:
                sigmaOne = ExpressionTreeNode(Sigma(SigmaTree(root.data.conditionTree.root.left)))
                sigmaTwo = ExpressionTreeNode(Sigma(SigmaTree(root.data.conditionTree.root.right)))
                sigmaTwo.children = root.children
                sigmaOne.children.append(sigmaTwo)

                if root.data.haveRowInTheEnd:
                    sigmaTwo.data.haveRowInTheEnd = True
                    sigmaTwo.data.rowInTheEnd = root.data.rowInTheEnd

                if father is not None:
                    indexOfRoot = father.children.index(root, 0, len(father.children))
                    father.children.remove(root)
                    father.children.insert(indexOfRoot, sigmaOne) # maybe change to father.children[indexOfRoot] = sigmaOne
                else:
                    root = sigmaOne

                notFound = False

        if notFound:
            for i in range(0, len(root.children)):
                if notFound:
                    self.__rule4(root.children[i], root, notFound)
        return

    # Sigma[P1]( Sigma[P2](R) ) = Sigma[P2]( Sigma[P1](R) )
    def rule4A(self):
        return self.__rule4A(self.expressionTree.root, None, False)

    # recursive function of rule 4A
    def __rule4A(self, root, father, swapped):
        if root is None:
            return

        if swapped and (not isinstance(root.data, Sigma)):
            return

        if father is not None:
            if isinstance(root.data, Sigma) and isinstance(father.data, Sigma):
                if root.data.haveRowInTheEnd:
                    root.data.haveRowInTheEnd = False
                    father.data.haveRowInTheEnd = True
                    father.data.rowInTheEnd = root.data.rowInTheEnd

                temp = root.data
                root.data = father.data
                father.data = temp

                swapped = True

        for i in range(0, len(root.children)):
            self.__rule4A(root.children[i], root, swapped)
        return

# Pi[X]( Sigma[p](R) ) = Sigma[p]( Pi[X](R) )
    def rule5A(self):
        return self.__rule5A(self.expressionTree.root, False)

    def __rule5A(self, root, swapped):
        if root is None:
            return

        if isinstance(root.data, Pi):
            for i in range(0, len(root.children)):
                if isinstance(root.children[i].data, Sigma):
                    tableAttrArray = set()
                    self.__getAttrOfTable(root, tableAttrArray)

                    if self.__isPiAttrLegalForTable(root.data, tableAttrArray) and self.__isPredicateAttrIncludedInPiAttr(root.data,root.children[i].data ):

                        if root.children[i].data.haveRowInTheEnd:
                            root.children[i].data.haveRowInTheEnd = False
                            root.data.haveRowInTheEnd = True
                            root.data.rowInTheEnd = root.children[i].data.rowInTheEnd
                        temp = root.data
                        root.data = root.children[i].data
                        root.children[i].data = temp
                        swapped = True
                        self.__rule5A(root.children[i], swapped)
        elif swapped:
            return

        else:
            for i in range(0, len(root.children)):
                self.__rule5A(root.children[i], swapped)
        return

    # Sigma[P]( Cartesian(R,S) ) = Cartesian( Sigma[P](R) ,S)
    def rule6(self):
        return self.__rule6(self.expressionTree.root, None, True)

    # recursive function of rule 6
    def __rule6(self, root, father, notFound):
        if root is None:
            return

        if isinstance(root.data, Sigma):
            sigma = root.data
            for i in range(0, len(root.children) and notFound):
                if isinstance(root.children[i].data, Cartesian) or isinstance(root.children[i].data, NJoin):
                    cartesianOrNjoinNode = root.children[i]
                    if isinstance(cartesianOrNjoinNode.children[0].data, Table):
                        if sigma.haveOnlyPredicatesFromSpecificTable(sigma.conditionTree.root,
                                                                     cartesianOrNjoinNode.children[0].data.table):
                            sigma.haveRowInTheEnd = True
                            sigma.rowInTheEnd = cartesianOrNjoinNode.children[0].data.table
                            cartesianOrNjoinNode.children[0].data = sigma
                            if father is not None:
                                father.children.remove(root)
                                father.children.append(cartesianOrNjoinNode)
                            else:
                                root = cartesianOrNjoinNode
                            notFound = False

        for i in range(0, len(root.children) and notFound):
            self.__rule6(root.children[i], root, notFound)
        return

    # Sigma[P]( Cartesian(R,S) ) = Cartesian(R ,Sigma[P](S) )
    def rule6A(self):
        return self.__rule6A(self.expressionTree.root, None, True)

    # recursive function of rule 6A
    def __rule6A(self, root, father, notFound):
        if root is None:
            return

        if isinstance(root.data, Sigma):
            sigma = root.data
            for i in range(0, len(root.children) and notFound):
                if isinstance(root.children[i].data, Cartesian) or isinstance(root.children[i].data, NJoin):
                    cartesianOrNjoinNode = root.children[i]
                    if isinstance(cartesianOrNjoinNode.children[len(cartesianOrNjoinNode.children) - 1].data, Table):
                        if sigma.haveOnlyPredicatesFromSpecificTable(sigma.conditionTree.root,
                                                                     cartesianOrNjoinNode.children[len(
                                                                       cartesianOrNjoinNode.children) - 1].data.table):
                            sigma.haveRowInTheEnd = True
                            sigma.rowInTheEnd = cartesianOrNjoinNode.children[
                                len(cartesianOrNjoinNode.children) - 1].data.table
                            cartesianOrNjoinNode.children[len(cartesianOrNjoinNode.children) - 1].data = sigma
                            if father is not None:
                                father.children.remove(root)
                                father.children.append(cartesianOrNjoinNode)
                            else:
                                root = cartesianOrNjoinNode
                            notFound = False

        for i in range(0, len(root.children) and notFound):
            self.__rule6A(root.children[i], root, notFound)
        return

    # Sigma[P]( Cartesian(R,S) ) = NJOIN(R,S)
    def rule11B(self):
        return self.__rule11B(self.expressionTree.root, None)

    def __rule11B(self, root, father):
        if root is None:
            return

        if isinstance(root.data, Sigma):
            for i in range(0, len(root.children)):
                if isinstance(root.children[i].data, Cartesian):

                    if self.__isSigmaGoodForNJoin(root.data.conditionTree.root) and \
                            self.__isCartesianOfTwoTables(root.children[i].data):
                        njoin = NJoin()
                        root.children[i].data = njoin

                        if father is None:
                            self.expressionTree.root = root.children[i]
                        else:
                            njoinNode = root.children[i]
                            indexOfRoot = father.children.index(root, 0, len(father.children))
                            father.children.remove(root)
                            father.children.insert(indexOfRoot, njoinNode)
                        return

        for i in range(0, len(root.children)):
            self.__rule11B(root.children[i], root)
        return

    def __isSigmaGoodForNJoin(self, root):
        if root is not None:
            if root.data == AND:
                if root.left is not None and root.right is not None:
                    answerArray1 = self.__checkConditionForNJoin(root.left)
                    answerArray2 = self.__checkConditionForNJoin(root.right)

                    if answerArray1[0] is True and answerArray2[0] is True:
                        if (answerArray1[1] == 'D' and answerArray2[1] == 'E') or \
                                (answerArray1[1] == 'E' and answerArray2[1] == 'D'):
                            return True
        return False

    def __isCartesianOfTwoTables(self, cartesian):
        RHasBeenSeen = False
        SHasBeenSeen = False

        for table in cartesian.tableList:
            if table == 'R':
                RHasBeenSeen = True
            if table == 'S':
                SHasBeenSeen = True

            if RHasBeenSeen and SHasBeenSeen:
                return True
        return False

    def queryAnalysis(self, logicalQueryPlan, schemeR, schemeS):
        global GLOBAL_R_ATTR_DICT
        global GLOBAL_S_ATTR_DICT
        GLOBAL_R_ATTR_DICT = schemeR.attrDict
        GLOBAL_S_ATTR_DICT = schemeS.attrDict

        num = SchemeNum(1)
        outputArray = self.queryAnalysisRec(logicalQueryPlan.expressionTree.root, schemeR, schemeS, list(), num, False)

        return outputArray

    def queryAnalysisRec(self, root, schemeR, schemeS, outputArray, outputNum, rightChild):
        if len(root.children) == 0:
            if isinstance(root.data, Table):
                return outputArray

            elif isinstance(root.data, Sigma):
                outputFormat = analysSigmaTree(root.data,schemeR, schemeS, rightChild, outputNum.number)
                outputList = outputFormat.setOutputFormat(schemeR, schemeS)
                outputFormat.after = outputList
                outputArray.append(outputFormat)
                outputNum.number += 1
                return outputArray

            else:
                outputFormat = OutputFormat(list(), list())
                outputFormat.operatorName = root.data.toString()
                inputList = outputFormat.setOutputFormat(schemeR, schemeS)
                outputFormat.before = inputList

                schemeR.makePiAnalysis(schemeR, schemeS, root.data, outputNum.number)

                outputList = outputFormat.setOutputFormat(schemeR, schemeS)
                outputFormat.after = outputList
                outputArray.append(outputFormat)
                outputNum.number += 1


        else:
            if len(root.children) >= 1:
                outputArray = self.queryAnalysisRec(root.children[0], schemeR, schemeS, outputArray, outputNum, False)
            if len(root.children) == 2:
                outputArray = self.queryAnalysisRec(root.children[1], schemeR, schemeS, outputArray, outputNum, True)

            outputFormat = OutputFormat(list(), list())
            outputFormat.operatorName = root.data.toString()
            inputList = outputFormat.setOutputFormat(schemeR, schemeS)
            outputFormat.before = inputList

            if isinstance(root.data, Sigma):
                outputFormat = analysSigmaTree(root.data, schemeR, schemeS, rightChild, outputNum.number)

            if isinstance(root.data, Pi):
                schemeR.makePiAnalysis(schemeR, schemeS, root.data, outputNum.number)

            if isinstance(root.data, Cartesian):
                schemeR.makeCartesianAnalysis(schemeR, schemeS, outputNum.number)

            if isinstance(root.data, NJoin):
                schemeR.makeNJoinAnalysis(schemeR, schemeS, outputNum.number)


            outputList = outputFormat.setOutputFormat(schemeR, schemeS)
            outputFormat.after = outputList
            outputArray.append(outputFormat)
            outputNum.number += 1

        return outputArray


    def __checkConditionForNJoin(self, conditionNode):
        if conditionNode.left is None and conditionNode.right is None:
            if conditionNode.data == "S.D=R.D" or conditionNode.data == "R.D=S.D":
                return [True, 'D']
            if conditionNode.data == "S.E=R.E" or conditionNode.data == "R.E=S.E":
                return [True, 'E']
        return [False]

    def __getAttrOfTable(self, root, listOfAttr):
        if len(root.children) == 0:

            if isinstance(root.data, Table):
                self.__addAttrToList(listOfAttr, root.data.table)

            if isinstance(root.data, Sigma) and root.data.haveRowInTheEnd:
                self.__addAttrToList(listOfAttr, root.data.rowInTheEnd)

            if isinstance(root.data, Pi) and root.data.haveRowInTheEnd:
                self.__addAttrToList(listOfAttr, root.data.rowInTheEnd)

            return

        for i in range(0, len(root.children)):
            self.__getAttrOfTable(root.children[i], listOfAttr)

        return

    def __addAttrToList(self, list, table):
        if table == 'R':
            for x in R_Attr:
                list.add(x)

        if table == 'S':
            for x in S_Attr:
                list.add(x)
        return

    def __isPiAttrLegalForTable(self, pi, tableAttrArray):
        listOfPiAttr = set()

        for piNode in pi.colList:
            listOfPiAttr.add(piNode.colName)

        for piAttr in listOfPiAttr:
            if not piAttr in tableAttrArray:
                return False

        return True

    def __isPredicateAttrIncludedInPiAttr(self, pi, sigma):
        listOfPiAttr = set()
        listOfPredicateAttr = set()

        for piNode in pi.colList:
            listOfPiAttr.add(piNode.toString())

        self.__getAttrOfPredicate(listOfPredicateAttr, sigma.conditionTree.root)

        for predicateAttr in listOfPredicateAttr:
            if not predicateAttr in listOfPiAttr:
                return False

        return True

    def __getAttrOfPredicate(self,listOfPredicateAttr, root):

        if root.left is None and root.right is None:
            condLeftStr = root.data.partition('=')[0]
            condRightStr = root.data.partition('=')[2]
            if condLeftStr[0] == 'R' or condLeftStr[0] == 'S':
                listOfPredicateAttr.add(condLeftStr)

            if condRightStr[0] == 'R' or condRightStr[0] == 'S':
                listOfPredicateAttr.add(condRightStr)


        if root.left is not None:
            self.__getAttrOfPredicate(listOfPredicateAttr, root.left)

        if root.right is not None:
            self.__getAttrOfPredicate(listOfPredicateAttr, root.right)

        return




class Sigma(object):
    haveRowInTheEnd = False
    rowInTheEnd = None

    def __init__(self, conditionTree):
        self.conditionTree = conditionTree

    def toString(self):
        str = self.conditionTree.toString()
        str = str[1:len(str) - 1]
        str = "SIGMA[" + str + "]"
        if self.haveRowInTheEnd:
            str += "(" + self.rowInTheEnd + ")"
        return str

    def haveOnlyPredicatesFromSpecificTable(self, root, table):
        if root.left is None and root.right is None:
            firstTable = -1
            secondTable = -1

            if root.data[0] == 'R' or root.data[0] == 'S':
                firstTable = root.data[0]

            indexOfOperator = root.data.find('=')

            if root.data[indexOfOperator + 1] == 'R' or root.data[indexOfOperator + 1] == 'S':
                secondTable = root.data[indexOfOperator + 1]

            if (firstTable == table and secondTable == table) or (firstTable == table and secondTable == -1)\
                    or (firstTable == -1 and secondTable == table):
                return True
            else:
                return False

        leftSide = True
        rightSide = True

        if root.left is not None:
            leftSide = self.haveOnlyPredicatesFromSpecificTable(root.left, table)

        if root.right is not None:
            rightSide = self.haveOnlyPredicatesFromSpecificTable(root.right, table)

        return leftSide and rightSide

class Cartesian(object):
    tableList = collections.deque()

    def __init__(self,list):
        self.tableList = list

    def convertArrayToList(self, strArray):
        for str in strArray:
            self.tableList.append(str)

    def toString(self):
        return "CARTESIAN"

class NJoin(object):
    def toString(self):
        return "NJoin"

class PiNode(object):
    tableName = None
    colName = None

    def __init__(self, tableName, colName):
        self.tableName = tableName
        self.colName = colName

    def toString(self):
        return self.tableName + "." + self.colName

class Pi(object):
    colList = collections.deque()
    haveRowInTheEnd = False
    rowInTheEnd = None

    def __init__(self,list):
        self.colList = list

    def convertArrayToList(self, strArray):
        for str in strArray:
            piNode = PiNode(str[0], str[2])
            self.colList.append(piNode)

    def toString(self):
        str = "PI["
        for element in self.colList:
            str += element.tableName + "." + element.colName + ","
        str = str[0:len(str) - 1]
        str = str.__add__("]")
        if self.haveRowInTheEnd:
            str += "(" + self.rowInTheEnd + ")"
        return str

class Table(object):
    def __init__(self, table):
        self.table = table

    def toString(self):
        return self.table

# divide query to the 3 parts and return them in an array
def queryDivider(strQuery):
    strQuery = strQuery.strip()
    strPartitionList = strQuery.partition(FROM)
    strSelectBlock = strPartitionList[0].strip()
    strPartitionList = (strPartitionList[1] + strPartitionList[2]).partition(WHERE)
    strFromBlock = strPartitionList[0].strip()
    strWhereBlock = (strPartitionList[1] + strPartitionList[2]).strip()

    return [strSelectBlock, strFromBlock, strWhereBlock]

def removeSpacesFromEachElementInStrArray(stringArr):
    for i in range(0, len(stringArr)):
        stringArr[i] = stringArr[i].strip()
    return stringArr

def checkIfDISTINCT(strDistinct):
    return strDistinct == DISTINCT

def extractAttributes(strSelectBlock):
    strSelectBlockListDivided = strSelectBlock.split()

    if checkIfDISTINCT(strSelectBlockListDivided[1]):
        global isDISTINCT
        isDISTINCT = True
        strSelectBlock = strSelectBlock.partition(DISTINCT)[2].strip()
    else:
        strSelectBlock = strSelectBlock.partition(SELECT)[2].strip()

    strSelectBlock = strSelectBlock.split(",")
    strSelectBlock = removeSpacesFromEachElementInStrArray(strSelectBlock)

    return strSelectBlock

def extractTables(strFromBlock):
    strFromBlock = strFromBlock.partition(FROM)[2].strip()
    strFromBlock = strFromBlock.split(',')
    strFromBlock = removeSpacesFromEachElementInStrArray(strFromBlock)

    return strFromBlock

def divideSimpleCondition(simpleConditionStr):
    if "<=" in simpleConditionStr:
        return simpleConditionStr.partition("<=")

    if "<>" in simpleConditionStr:
        return simpleConditionStr.partition("<>")

    if ">=" in simpleConditionStr:
        return simpleConditionStr.partition(">=")

    if "<" in simpleConditionStr:
        return simpleConditionStr.partition("<")

    if ">" in simpleConditionStr:
        return simpleConditionStr.partition(">")

    if "=" in simpleConditionStr:
        return simpleConditionStr.partition("=")

    return None

def isConstant(constStr):
    if AND in constStr or OR in constStr:
        return False

    return True

def isSimpleCondition(simpleConditionStr):
    global INT_IN_USE
    global STRING_IN_USE
    INT_IN_USE = False
    STRING_IN_USE = False

    simpleConditionParts = divideSimpleCondition(simpleConditionStr)

    if simpleConditionParts is None:
        return False

    if simpleConditionParts[0].strip() == '' or simpleConditionParts[2].strip() == '':
        return False

    if (simpleConditionStr[0] == "(" and simpleConditionStr[len(simpleConditionStr) - 1] != ")") or (
            simpleConditionStr[0] != "(" and simpleConditionStr[len(simpleConditionStr) - 1] == ")"):
        return False

    return isConstant(simpleConditionParts[0]) and isConstant(simpleConditionParts[2])

def isWrapByBrackets(conditionStr):
    conditionStr = conditionStr.strip()
    if conditionStr[0] != '(':
        return False

    strSize = len(conditionStr)
    bracketsCount = 0
    indexOfEndOfBrackets = 0

    for i in range(0, strSize):
        if conditionStr[i] == '(':
            bracketsCount += 1
        if conditionStr[i] == ')':
            bracketsCount -= 1
        if bracketsCount == 0:
            indexOfEndOfBrackets = i
            break

    if indexOfEndOfBrackets == (strSize - 1):
        return True

    return False

def simpleCondition(conditionStr):
    return not (("AND" in conditionStr) or ("OR" in conditionStr) or isWrapByBrackets(conditionStr))

def buildTwoPartsConditionArr(conditionWordsArr, indexOfDivider):
    if indexOfDivider == 0 or indexOfDivider == len(conditionWordsArr) - 1:
        return False

    firstPart = ""
    secondPart = ""

    for i in range(0, indexOfDivider):
        firstPart += conditionWordsArr[i] + " "

    for i in range(indexOfDivider + 1, len(conditionWordsArr)):
        secondPart += conditionWordsArr[i] + " "

    return [firstPart, secondPart]


def isCondition(root, conditionStr):
    conditionStr = conditionStr.strip()

    if isWrapByBrackets(conditionStr):
        conditionStr = conditionStr[1:len(conditionStr) - 1]

    if simpleCondition(conditionStr):  # checks if there is no 'OR' or 'AND in the condition
        if isSimpleCondition(conditionStr):
            root.data = conditionStr.replace(" ", "")
            return True
        else:
            return False

    root.left = SigmaTreeNode()
    root.right = SigmaTreeNode()

    conditionWordsArr = conditionStr.split()

    for i in range(0, len(conditionWordsArr)):
        if conditionWordsArr[i] == AND or conditionWordsArr[i] == OR:
            conditionTwoParts = buildTwoPartsConditionArr(conditionWordsArr, i)

            if isCondition(root.left, conditionTwoParts[0]) and isCondition(root.right, conditionTwoParts[1]):
                root.data = conditionWordsArr[i]
                return True

    return False

def buildConditionsTree(strWhereBlock):
    strWhereBlock = strWhereBlock.partition(WHERE)[2].strip()

    tree = SigmaTree()
    isCondition(tree.root, strWhereBlock)

    return tree

def convertSQLQueryToAlgebraicExpression(sqlString):
    sqlString = sqlString.strip()
    if sqlString[len(sqlString) - 1] == ";":
        sqlString = sqlString[0:len(sqlString) - 1]

    sqlParts = queryDivider(sqlString)

    strSelectBlock = sqlParts[0]
    strFromBlock = sqlParts[1]
    strWhereBlock = sqlParts[2]

    pi = Pi(collections.deque())
    cartesian = Cartesian(collections.deque())

    strSelectBlock = extractAttributes(strSelectBlock)
    pi.convertArrayToList(strSelectBlock)

    strFromBlock = extractTables(strFromBlock)
    cartesian.convertArrayToList(strFromBlock)

    sigma = Sigma(buildConditionsTree(strWhereBlock))

    return AlgebraicExpression([pi, sigma, cartesian])
