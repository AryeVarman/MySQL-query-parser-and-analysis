import expressionClasses
import fileClasses
import time
import random
import os

GLOBAL_R_ATTR_DICT = dict()
GLOBAL_S_ATTR_DICT = dict()

def menu():
    string = "Please choose the number of the rule to perform from the following:\n"
    string += "1) 4\n"
    string += "2) 4A\n"
    string += "3) 5A\n"
    string += "4) 6\n"
    string += "5) 6A\n"
    string += "6) 11B\n"
    string += "Enter 1-6\n"
    return string

def partOne(queryStr):
    print("\nPart One\n========")
    time.sleep(2)

    SQLQuery = expressionClasses.convertSQLQueryToAlgebraicExpression(queryStr)

    print("\nThe algebraic expression of the query is:\n" + SQLQuery.toString() + '\n')

    Continue = True
    ruleChosen = ""

    while Continue:
        print(menu())
        choice = str(input())

        if choice == '1':
            SQLQuery.rule4()
            ruleChosen = 'rule 4: "Sigma[P1 AND P2](R) = Sigma[P1]( Sigma[P2](R) )"'
            Continue = False
            valid = True

        elif choice == '2':
            SQLQuery.rule4A()
            ruleChosen = 'rule 4A: "Sigma[P1]( Sigma[P2](R) ) = Sigma[P2]( Sigma[P1](R) )"'
            Continue = False
            valid = True

        elif choice == '3':
            SQLQuery.rule5A()
            ruleChosen = 'rule 5A: "Pi[X]( Sigma[p](R) ) = Sigma[p]( Pi[X](R) )"'
            Continue = False
            valid = True

        elif choice == '4':
            SQLQuery.rule6()
            ruleChosen = 'rule 6: "Sigma[P]( Cartesian(R,S) ) = Cartesian( Sigma[P](R) ,S)"'
            Continue = False
            valid = True

        elif choice == '5':
            SQLQuery.rule6A()
            ruleChosen = '"rule 6A: Sigma[P]( Cartesian(R,S) ) = Cartesian(R ,Sigma[P](S) )"'
            Continue = False
            valid = True

        elif choice == '6':
            SQLQuery.rule11B()
            ruleChosen = '"rule 11B: Sigma[P]( Cartesian(R,S) ) = NJOIN(R,S)"'
            Continue = False
            valid = True

        else:
            print("illegal option, please choose a valid rule\n")
            valid = False

        if valid:
            print("After rule " + ruleChosen + " the algebraic expression is:\n")
            print(SQLQuery.toString() + '\n')
            print("End of part One\n===============\n\n")
            time.sleep(2)
    return

def partTwo(queryStr):
    SQL1 = expressionClasses.convertSQLQueryToAlgebraicExpression(queryStr)
    SQL2 = expressionClasses.convertSQLQueryToAlgebraicExpression(queryStr)
    SQL3 = expressionClasses.convertSQLQueryToAlgebraicExpression(queryStr)
    SQL4 = expressionClasses.convertSQLQueryToAlgebraicExpression(queryStr)

    print("\nPart Two\n========")
    time.sleep(2)

    print("\nLogical Query Plan 1\n====================")
    time.sleep(1)
    doTenRandomRules(SQL1)

    print("\nLogical Query Plan 2\n====================")
    time.sleep(1)
    doTenRandomRules(SQL2)

    print("\nLogical Query Plan 3\n====================")
    time.sleep(1)
    doTenRandomRules(SQL3)

    print("\nLogical Query Plan 4\n====================")
    time.sleep(1)
    doTenRandomRules(SQL4)

    print("\nThe 4 Logical Query Plans are:\n====================================================================")
    printQueryPlans(SQL1, SQL2, SQL3, SQL4)
    print("====================================================================\nEnd of part two\n")
    time.sleep(2)
    return [SQL1, SQL2, SQL3, SQL4]


def doTenRandomRules(SQL):
    print("SQL query is:")
    print(SQL.toString())

    for i in range(10):
        num = random.randint(1,6)

        if num == 1:
            SQL.rule4()
            print("\nAfter rule 4 query is:")
            print(SQL.toString())

        elif num == 2:
            SQL.rule4A()
            print("\nAfter rule 4A query is:")
            print(SQL.toString())

        elif num == 3:
            SQL.rule5A()
            print("\nAfter rule 5A query is:")
            print(SQL.toString())

        elif num == 4:
            SQL.rule6()
            print("\nAfter rule 6 query is:")
            print(SQL.toString())

        elif num == 5:
            SQL.rule6A()
            print("\nAfter rule 6A query is:")
            print(SQL.toString())

        elif num == 6:
            SQL.rule11B()
            print("\nAfter rule 11B query is:")
            print(SQL.toString())
    return


def printQueryAnalys(sqlOutputArray):
    queryNum = 1
    for outputArray in sqlOutputArray:
        print("\nLogical Query Plan " + str(queryNum) + "\n====================")
        for output in outputArray:
             print(output.toString())
        queryNum += 1


def partThree(logicalQueryPlanList):
    print("\nPart Three\n========")
    schemeFromFileArray1 = fileClasses.initiateSchemeFromFile()
    schemeFromFileArray2 = fileClasses.initiateSchemeFromFile()
    schemeFromFileArray3 = fileClasses.initiateSchemeFromFile()
    schemeFromFileArray4 = fileClasses.initiateSchemeFromFile()

    output1 = logicalQueryPlanList[0].queryAnalysis(logicalQueryPlanList[0], schemeFromFileArray1[0], schemeFromFileArray1[1])
    output2 = logicalQueryPlanList[1].queryAnalysis(logicalQueryPlanList[1], schemeFromFileArray2[0], schemeFromFileArray2[1])
    output3 = logicalQueryPlanList[2].queryAnalysis(logicalQueryPlanList[2], schemeFromFileArray3[0], schemeFromFileArray3[1])
    output4 = logicalQueryPlanList[3].queryAnalysis(logicalQueryPlanList[3], schemeFromFileArray4[0], schemeFromFileArray4[1])

    printQueryAnalys([output1,output2,output3,output4])


def printQueryPlans(SQL1, SQL2, SQL3, SQL4):
    print(SQL1.toString())
    print(SQL2.toString())
    print(SQL3.toString())
    print(SQL4.toString())
    return


if __name__ == '__main__':
    print("Please enter a valid SQL query:")
    queryStr = input()

    partOne(queryStr)
    fourSQL = partTwo(queryStr)
    partThree(fourSQL)

    os.system("PAUSE")
    # SELECT R.D , S.E FROM R,S WHERE (R.D=9 AND S.E = R.E) AND (R.A = 7 AND R.B = R.E);