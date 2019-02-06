import sys    #For sending the files using console
import re     #For regular expressions
import itertools

inputData = []              # A user given transaction-input 2-d list
allItems = {}                  # A dictionary comprising of all the items in the transaction
phi = 0                     # Support Difference Constraint
mis = {}                    # A dictionary containg the item as key and its MIS as value
cannotBeTogether = []     # A user given set,stored as 2-d list that comprises of the set of items that cannot be together
mustHave = []              # A user given set,stored as 2-d list that comprises of the set of items that can be together
newF = []

#Method to obtain input transaction details from "input-data.txt"
#Parameters: the file name
def getInputData(inputTransaction):
    global inputData,allItems
    file = open(inputTransaction, "r")   #Opening the input.txt file in READ mode only

    for line in file:
        # traversing through each line in the input file and finding all those lines which contain one or more digits from 0 - 9
        transaction = re.findall(r"\d+", line)
        transaction = [int(t) for t in transaction]  # Parsing the string values to int type
        inputData += [transaction]              #Appending each list with []
        allItems = set().union(allItems, transaction)

    file.close()
    return inputData, allItems

#Method to obtain various parameter details from "parameter-file.txt"
#Parameters: the file name
def getParameterData(parameterFile):
    global phi, mis, cannotBeTogether, mustHave

    file = open(parameterFile, "r")            #Opening the parameter.txt file in READ mode only

    for line in file:                          #Iterating through all the lines in the file

        if line[:3] == "MIS":                        #Comparing if the first three letters of the first item is 'MIS'
            element = re.match(r"MIS\((\d+)\)\s=\s(.*)", line)       #Matching with the regular expression MIS (digits from 0-9)space=space{matching all the characters}
            #element = re.search('\S*\((\d*)\)\D*(\d\.?\d*)', line)
            mis[int(element.group(1))] = float(element.group(2))

        if line[:3] == "SDC":                     #Comparing if the first three letters of the first item is 'SDC'
            element = re.match(r"SDC\s=\s(.*)", line)   #Matching with the regular expression  'SDC space=space {matching all the characters}'
            phi = float(element.group(1))

        if line[:18] == "cannot_be_together":      #Comparing if the first 18 letters of the first item is 'cannot_be_together'
            values = re.findall("{(\d+(,*\s*\d+)*)}", line)
            for value in values:
                allItems = re.findall(r"\d+", value[0])             #matching with the regex - one or more digits
                allItems = [int(i) for i in allItems]              # Parsing the string values to int type
                cannotBeTogether.append(allItems)

        if line[:9] == "must-have":             #Comparing if the first 9 letters of the first item is 'must-have'
            allItems = re.findall(r"\d+", line)    #matching with the regex - one or more digits
            allItems = [int(i) for i in allItems]     # Parsing the string values to int type
            for i in allItems:
                mustHave.append([i])

    file.close()
    return phi, mis, cannotBeTogether, mustHave


# A method to determine the Count (number of occurances) of an element in the input transaction
#Parameters: the input transaction file, individual item that are a part of the transaction
def getCount(inputData, itemgroup):
    count = 0
    itemValue = set(itemgroup)                  #storing the individual item
    for i in range(len(inputData)):

        if set(inputData[i]) & itemValue == itemValue:    #To verify if the if the individual item is present in the input transaction or not
            count += 1
    return count


# A method to calculate the Support of each item in the transaction
# Parameters:  the input transaction file, individual item that are a part of the transaction
def getSupport(inputData, itemgroup):
    return float(getCount(inputData, itemgroup)) / len(inputData)



# Level 2 candidate-gen function
# Parameters: L, sdc
#In this method, followed the notations and exact logic step-by-step as per the prescribed textbook
def level2_candidate_gen(L, phi):
    global inputData,mis
    C2 = []  # initialize the set of candidates
    numberOfTransactions = len(inputData)

    till = len(L) - 1
    for i in range(0, till):
        item = L[i]
        # Check to see if the support of current element is greater than or equal to the MIS of the first element
        #if (freq(inputData, [l]) / float(numberOfTransactions)) >= mis[l]:
        if (getSupport(inputData,[item])) >= mis[item]:
            for j in range(i + 1, len(L)):
                h = L[j]

                #if (freq(inputData, [h]) / float(numberOfTransactions)) >= mis[l]:
                if ((getSupport(inputData,[h])) >= mis[item]) and ((abs(getSupport(inputData, [h]) - getSupport(inputData, [item]))) <= phi):
                        C2.append([item, h])  # insert the candidate [l, h] into C2

    return C2


# Candidate-gen function
#Parameters: (F-1), sdc
# In this method, followed the notations and exact logic step-by-step as per the prescribed textbook
def MScandidate_gen(oldF, phi):
    c = []
    Ck = []  # initialize the set of candidates
    latestElement = []
    global inputData
    n = len(oldF)
    for index in range( n):
        f1 = oldF[index]                 #The first set of the candidates is sorted

        for indexJ in range(index+1,n):
            f2 = oldF[indexJ]
            # find all pairs of frequent itemsets that differ only in the last item
            #Joining
            if (f1[:- 1] == f2[:- 1]) :
                if mis[f1[-1]] <= mis[f2[-1]] and (abs(getSupport(inputData, [f1[-1]]) - getSupport(inputData, [f2[-1]]))) <= phi:
                    temp = [i for i in f1]
                    temp.append(f2[-1])
                    c.append(temp)

    #Pruning: for each (k-1) subset 'subSet' of c, if s is not in oldF, c is deleted from Ck
    for eachItem in list(c):
        subSet = [list(i) for i in itertools.combinations(eachItem,len(c[0])-1)]  # a (k-1)-subset of c
        for eachC in subSet:
            if eachItem[0] in eachC or mis[eachItem[1]] == mis[eachItem[0]]:
                for olditem in oldF:
                    if olditem == eachC:
                        flag = True
                        break
                    else: flag = False
                if not flag:
                    c.remove(eachItem)
                    break
            else :
                break

    return c

def MSApriori(inputData, allItems, mis, phi):

    F = [[]] * (len(mis) + 1)
    C = [[]] * (len(mis) + 1)
    count = {}
    tailCount = {}
    numberOfTransactions = len(inputData)  # number of transactions

    # Sorting the item set by their MIS
    M = sorted(mis, key=mis.__getitem__)

    # Init pass
    L = [M[0]]

    for j in range(1, len(M)):
        if (getSupport(inputData,[M[j]])) >= mis[M[0]]:
            L.append(M[j])
            count[tuple([M[j]])] = getCount(inputData, [M[j]])

    # F1
    F[1] = []
    for item in L:
        if (getSupport(inputData,[item])) >= mis[item]:
            F[1].append(item)
            count[tuple([item])] = getCount(inputData, [item])

    #Generation of further candidates
    k = 2
    while len(F[k-1]) != 0:
        F[k] = []

        if k == 2:
            C[2] = level2_candidate_gen(L, phi)
            for c in C[2]:
                d = tuple(sorted(c, key=lambda i: mis[i]))
                count[d] = 0
                tailCount[d] = 0
        if k > 2:
            C[k] = MScandidate_gen(F[k - 1], phi)
            for c in C[k]:
                d = tuple(sorted(c, key=lambda i: mis[i]))
                count[d] = 0
                tailCount[d] = 0

        for t in inputData:
            for c in C[k]:
                if set(c).issubset(set(t)):
                    if (count.get(tuple(c)) == None):
                        count[tuple(c)] = 1
                    else:
                        count[tuple(c)] = count.get(tuple(c)) + 1

                if (set(c[1:]).issubset(set(t))):
                    if (tailCount.get(tuple(c)) == None):
                        tailCount[tuple(c)] = 1
                    else:
                        tailCount[tuple(c)] = tailCount.get(tuple(c)) + 1

        for c in C[k]:
            d = tuple(sorted(c, key=lambda i: mis[i]))
            if count[d]/numberOfTransactions >= mis[c[0]]:
                F[k].append(c)

        k += 1

    # Remove duplications
    result = []
    for i in range(len(F)):
        for f in F[i]:
            if f not in result:
                if isinstance(f, int):
                    result.append([f])
                else:
                    result.append(f)

    return result, count, tailCount


# Apply constraints: cannot_be_together and must_have

def apply_constraints(F, cannotBeTogether, mustHave):
    idx = 0
    while idx < len(F):
        f = F[idx]
        flag = False

        for c in cannotBeTogether:
            if flag:
                break
            if set(c).issubset(f):
                F.remove(f)
                flag = True
                idx -= 1
        flag = False

        if not mustHave:
            flag = True
        for m in mustHave:
            if len(set(f) & set(m)) > 0:
                flag = True
                break

        # Group doesn't contain any mustHave
        if not flag:
            F.remove(f)
            idx -= 1

        idx += 1
    return F

#This is the main method, from which function calls to various user-defined methods are made.
def __main__(argv):
    # Data preprocessing step that involves fetching the data from the given txt files and cleaning:
    global inputData,allItems
    global phi, mis, cannotBeTogether, mustHave

    inputTransaction = argv[1]
    parameterFile = argv[2]
    outputFile = argv[3]

    inputData, allItems = getInputData(inputTransaction)

    phi, mis, cannotBeTogether, mustHave = getParameterData(parameterFile)

    # Run
    F, count, tailCount = MSApriori(inputData, allItems, mis, phi)

    # Constraints
    F = apply_constraints(F, cannotBeTogether, mustHave)

    # To generate a dictionary from F to be able to print output in the desired format
    F_dict = {}
    for f in F:
        if len(f) not in F_dict.keys():
            F_dict[len(f)] = []
        F_dict[len(f)].append(f)

    # Writing output
    output = ""
    f_out = open(outputFile, "w")

    for i in range(len(mis)):
        if i in F_dict.keys():
            output += "Frequent " + str(i) + "-itemsets\n\n"

            for f in F_dict[i]:
                d = tuple(sorted(f, key=lambda i: mis[i]))
                output += "    " + str(count[d]) + " : " + "{" + ", ".join(map(str, f)) + "}\n"
                if i > 1:
                    output += "Tailcount = " + str(tailCount[d]) + "\n"

            output += "\n    Total number of frequent " + str(i) + "-itemsets = " + str(len(F_dict[i])) + "\n\n\n"

    f_out.write(output)
    f_out.close()

if __name__ == '__main__':
    if(len(sys.argv) != 4):
        print("Please give all the three reqired files: #1 Input/Transaction file, #2 Parameter file, #3 Output file ")
        print( "number of files given are:",len(sys.argv))
        sys.exit(2)

    __main__(sys.argv)
