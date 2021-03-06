# -----------------------------------------------------------------------------
# This program simulate a simple first order resolution process
#
#
# -----------------------------------------------------------------------------

#define a class to Node to help manipulate trees
class Node:
    def __init__(self,type,children=None,leaf=None):
         self.type = type
         if children:
              self.children = children
         else:
              self.children = [ ]
         self.leaf = leaf

#This function will find the 'implies' in a tree for a logic sentence in order to remove them. The pointer to the 'implies' and the layer regarding the tree which the 'implies' is in will be recorded.
def FindImplies(Tree):
    global ImpliesPosition, layer
    layer += 1
    if Tree.leaf == '=>':
        ImpliesPosition.append([Tree, layer])
    if type(Tree.children) is list and len(Tree.children) == 2:
        FindImplies(Tree.children[0])
        FindImplies(Tree.children[1])
    elif Tree.children != []:
        FindImplies(Tree.children)

#This function will apply no to a subsentence as the result of remove 'implies'. Generally, universial quantifier will be changed to existential quantifier, 'and' to 'or' and vice versa. Atomic sentences will be applied on a not function.
def ApplyNot(SubTree):
    if 'Exist' in SubTree.leaf:
        SubTree.leaf = SubTree.leaf.replace('Exist', 'ForAll')
    elif 'ForAll' in SubTree.leaf:
        SubTree.leaf = SubTree.leaf.replace('ForAll', 'Exist')
    elif SubTree.leaf == '&':
        SubTree.leaf = '|'
    elif SubTree.leaf == '|':
        SubTree.leaf = '&'
    elif 'not' in SubTree.leaf:
        SubTree.leaf = SubTree.leaf.replace('not(', '').replace(')', '')+')'
    else:
        SubTree.leaf = 'not(' + SubTree.leaf +')'    
    if type(SubTree.children) is list and len(SubTree.children) == 2:
        ApplyNot(SubTree.children[0])
        ApplyNot(SubTree.children[1])
    elif SubTree.children != []:
        ApplyNot(SubTree.children)

#This function find all the variables which is defined by quantifiers in a sentence. This will help the variable standardization process later.
def FindOVariables(Tree):
    global OldVariables
    if 'Exist' in Tree.leaf or 'ForAll' in Tree.leaf:
        OldVariables.append(Tree.leaf.replace('Exist{', '').replace('ForAll{', '').replace('}', '').split(',')[0])
    if type(Tree.children) is list and len(Tree.children) == 2:
        FindOVariables(Tree.children[0])
        FindOVariables(Tree.children[1])
    elif Tree.children != []:
        FindOVariables(Tree.children)

#The following two functions will finish the variable standardization process by assign quantifiers new variables in a reserved variable list. After that, all the variables within the scope of this quantifier should be changed by the ReplaceVariables function.
def AssignNewQuantifiers(Tree):
    global Variables, AssignOrder
    if 'Exist' in Tree.leaf:
        OVarlist = Tree.leaf.replace('Exist{', '').replace('}', '').split(',')
        for i in range(len(OVarlist)):
	    if i == 0:
                NVarlist = Variables[AssignOrder]
	    else:
    		NVarlist = NVarlist + ',' + Variables[AssignOrder]
	    AssignOrder += 1
        Tree.leaf = 'Exist{' + NVarlist + '}'
        for i in range(len(OVarlist)):
            ReplaceVariables(Tree, OVarlist[i], NVarlist.split(',')[i])
    if 'ForAll' in Tree.leaf:
        OVarlist = Tree.leaf.replace('ForAll{', '').replace('}', '').split(',')
        for i in range(len(OVarlist)):
	    if i == 0:
                NVarlist = Variables[AssignOrder]
	    else:
    		NVarlist = NVarlist + ',' + Variables[AssignOrder]
	    AssignOrder += 1
        Tree.leaf = 'ForAll{' + NVarlist + '}'
        for i in range(len(OVarlist)):
            ReplaceVariables(Tree, OVarlist[i], NVarlist.split(',')[i])
    if type(Tree.children) is list and len(Tree.children) == 2:
        AssignNewQuantifiers(Tree.children[0])
        AssignNewQuantifiers(Tree.children[1])
    elif Tree.children != []:
        AssignNewQuantifiers(Tree.children)

def ReplaceVariables(SubTree, OVar, NVar):
    if '(' in SubTree.leaf and '{' not in SubTree.leaf:
        j = SubTree.leaf.count('(')
        OVarlist = SubTree.leaf.split('(', 1)[1].replace(')', '').split(',')
        for i in range(len(OVarlist)):
            if OVarlist[i] == OVar:
		OVarlist[i] = NVar
        for i in range(len(OVarlist)):
            if i == 0:
                NVarlist = OVarlist[i]
	    else:
                NVarlist = NVarlist + ',' + OVarlist[i]
	SubTree.leaf = SubTree.leaf.split('(', 1)[0] + '(' + NVarlist + ')'*j
    if type(SubTree.children) is list and len(SubTree.children) == 2:
        ReplaceVariables(SubTree.children[0], OVar, NVar)
        ReplaceVariables(SubTree.children[1], OVar, NVar)
    elif SubTree.children != []:
        ReplaceVariables(SubTree.children, OVar, NVar)

#This function will replace variables referred by existential quantifier by Skolem functions. General rules is described in the corresponding part in the main function.
def AssignSkolemFunctions(Tree, UniversialVar):
    global FunctionAssignOrder, SkolemFunctions
    if 'ForAll' in Tree.leaf:
	NUniversialVar = Tree.leaf.replace('ForAll{', '').replace('}', '').split(',')
	for i in range(len(NUniversialVar)):
	    UniversialVar.append(NUniversialVar[i])
    if 'Exist' in Tree.leaf:
        OVarlist = Tree.leaf.replace('Exist{', '').replace('}', '').split(',')
	UniversialVarStr = ''
	for i in range(len(UniversialVar)):
	    if i == 0:
    		UniversialVarStr = UniversialVar[i]
	    else:
		UniversialVarStr = ',' + UniversialVar[i] 
        if len(UniversialVar) != 0:
	    for i in range(len(OVarlist)):
	        if i == 0:
                    NVarlist = SkolemFunctions[FunctionAssignOrder] + '(' + UniversialVarStr +')'
	        else:
    		    NVarlist = NVarlist + ',' + SkolemFunctions[FunctionAssignOrder] + '(' + UniversialVarStr + ')'
	        FunctionAssignOrder += 1
	else:
	    for i in range(len(OVarlist)):
	        if i == 0:
                    NVarlist = SkolemFunctions[FunctionAssignOrder] + '(' + OVarlist[i] + ')'
	        else:
    		    NVarlist = NVarlist + ',' + SkolemFunctions[FunctionAssignOrder] + '(' + OVarlist[i] + ')'
	        FunctionAssignOrder += 1
        Tree.leaf = 'Exist{' + NVarlist + '}'
        for i in range(len(OVarlist)):
            ReplaceVariables(Tree, OVarlist[i], NVarlist.split(',')[i])
    if type(Tree.children) is list and len(Tree.children) == 2:
        AssignSkolemFunctions(Tree.children[0], UniversialVar)
        AssignSkolemFunctions(Tree.children[1], UniversialVar)
    elif Tree.children != []:
        AssignSkolemFunctions(Tree.children, UniversialVar)

#This function will remove all the Quantifiers and return a new tree with all the quantifiers pruned.
def RemoveQuantifiers(Tree):
    if Tree == []:
        return []
    if type(Tree.children) is list and len(Tree.children) == 2:
        NNode = Node(Tree.type, [RemoveQuantifiers(Tree.children[0]), RemoveQuantifiers(Tree.children[1])], Tree.leaf)
	return NNode
    elif 'Exist' not in Tree.leaf and 'ForAll' not in Tree.leaf:
        NNode = Node(Tree.type, RemoveQuantifiers(Tree.children), Tree.leaf)
	return NNode
    else:
        return RemoveQuantifiers(Tree.children)

#This function will locate all the 'or's in the tree. The pointers and the layer of the 'or's in the tree will be recorded.
def FindOrs(Tree):
    global OrsPosition, layer
    layer += 1
    if Tree.leaf == '|':
        OrsPosition.append([Tree, layer])
    if type(Tree.children) is list and len(Tree.children) == 2:
        FindOrs(Tree.children[0])
        FindOrs(Tree.children[1])
    elif Tree.children != []:
        FindOrs(Tree.children)

#This function will distribute 'or' and 'and' to form a CNF sentence. General rules are described in the corresponding part in the main function
def DistributeOrAnd(SubTree):
    if SubTree != []:
        if SubTree.children[0].leaf == '&':
            SubTree.leaf = '&'
	    SubTree.children[1] = Node('OR', [SubTree.children[0].children[1], SubTree.children[1]], '|')
            SubTree.children[0].leaf = '|'
	    SubTree.children[0].children[1] = SubTree.children[1].children[1]
            DistributeOrAnd(SubTree.children[0])
        if SubTree.children[1].leaf == '&':
            SubTree.leaf = '&'
	    SubTree.children[0] = Node('OR', [SubTree.children[0], SubTree.children[1].children[0]], '|')
            SubTree.children[1].leaf = '|'
	    SubTree.children[1].children[0] = SubTree.children[0].children[0]
            DistributeOrAnd(SubTree.children[1])
    
# The following two functions will store all the sentence in the knowledge base into a 2D list with the first dimension indentifies different clauses.
def SeparateClauses(Tree):
    global NumberofClauses, SentenceArray
    if Tree.leaf == '|' or Tree.type == 'ATOMICSENTENCE':
        NumberofClauses += 1
        SentenceArray.append([])
        AddNewClause(Tree)
    else:
	SeparateClauses(Tree.children[0])
	SeparateClauses(Tree.children[1])

def AddNewClause(SubTree):
    global SentenceArray
    if SubTree.type == 'ATOMICSENTENCE':
        SentenceArray[NumberofClauses].append(SubTree.leaf)
    else:
        AddNewClause(SubTree.children[0])
	AddNewClause(SubTree.children[1])

#This function tells whether two liters are Unifierable according to the definition.
def Unifierable(Liter1, Liter2):
    if Liter1.leaf == 'not':
        predicate1 = Liter1.children[0].leaf
	Liter1 = Liter1.children[0]
    else:
        predicate1 = Liter1.leaf
    if Liter2.leaf == 'not':
        predicate2 = Liter2.children[0].leaf
        Liter2 = Liter2.children[0]
    else:
        predicate2 = Liter2.leaf
    if predicate1 == predicate2:
        for i in range(len(Liter1.children)):
	    if Liter1.children[i].type != 'VARIABLES' and Liter2.children[i].type != 'VARIABLES' and Liter1.children[i].leaf != Liter2.children[i].leaf:
		return False
	return True
    else:
        return False

#This is the function to realize resolution. Resolution starts between previous clauses and new clauses and then among new clauses.
def Resolution(SentenceArray, NewSentence):
    NSentence, HaveNew = [[]], 0
    for i in range(1, len(SentenceArray)):
	for j in range(1, len(NewSentence)):
	    for m in range(len(SentenceArray[i])-1):
		for n in range(len(NewSentence[j])-1):
		    Comp = Compare(SentenceArray, NewSentence, i, j, m, n)
		    if Comp[0] == True and Comp[1] == []:
			return Comp
		    elif Comp[0] == True and Comp[1] != []:
			HaveNew = 1
			NSentence.append(Comp[1])
		    elif Comp[0] == False and Comp[1] != []:
			return [False, []]
    for i in range(1, len(NewSentence)):
	for j in range(i+1, len(NewSentence)):
	    for m in range(len(NewSentence[i])-1):
		for n in range(len(NewSentence[j])-1):
		    Comp = Compare(NewSentence, NewSentence, i, j, m, n)
		    if Comp[0] == True and Comp[1] == []:
			return Comp
		    elif Comp[0] == True and Comp[1] != []:
			HaveNew = 1
			NSentence.append(Comp[1])
		    elif Comp[0] == False and Comp[1] != []:
			return [False, []]
    if HaveNew == 0:
	return [False, []]
    else:
	return [True, NSentence]

#The following functions compare the two liters that are unifierable to decide whether a resolution occurs or a conclusion can be drawn.
def Compare(SenArrayA, SenArrayB, i, j, m, n):
    Liter1 = AtomicSentenceParser.atomicparse(SenArrayA[i][m])
    Liter2 = AtomicSentenceParser.atomicparse(SenArrayB[j][n])
    if Unifierable(Liter1, Liter2):
	return Unify(SenArrayA[i], SenArrayB[j], m, n)
    else:
	return [False, []]

def SearchVar(Tree):
    OVari = []
    if Tree.type == 'VARIABLES':
	OVari.append(Tree.leaf)
    for i in range(len(Tree.children)):
	if Tree.children != []:
	    OVari.append(SearchVar(Tree.children[i]))
    return OVari

def NewOVariables(SenArray):
    OVari = []
    for i in range(len(SenArray)):
	OVari.append(SearchVar(SenArray[i]))
    return OVari

#If a resolution occurs, this function combines two clauses to get the new resolved clause.
def Unify(SenArrayA, SenArrayB, m, n):
    global Firstiteration
    SenB, SenA, NSenStr= [], [], []
    for i in range(len(SenArrayA)-1):
	Sentree = AtomicSentenceParser.atomicparse(SenArrayA[i])
	SenA.append(Sentree)
    for i in range(len(SenArrayB)-1):
	Sentree = AtomicSentenceParser.atomicparse(SenArrayB[i])
	SenB.append(Sentree)
    if len(SenArrayA) == 2 and len(SenArrayB) == 2:
	if SenA[m].leaf != SenB[n].leaf:
            return [True, []]
	else:
            if Firstiteration == True: 
	        return [False, [False]]
    if SenA[m].leaf == SenB[n].leaf:
	return [False, []]
    OVariA = NewOVariables(SenA)
    OVariB = NewOVariables(SenB)
    Variables = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v']    
    for i in range(len(OVariA)):
        if OVariA[i] in Variables:
            Variables.remove(OVariA[i])
    for i in range(len(OVariB)):
	NewChangeVariables(SenB, OVariB[i], Variables[i])
    NSenA, NSenB = SenA[m], SenB[n]
    if SenA[m].leaf == 'not':
	NSenA = SenA[m].children[0]
    if SenB[n].leaf == 'not':
	NSenB = SenB[n].children[0]
    for i in range(len(NSenA.children)):
	if NSenB.children[i].type == 'VARIABLES':
	    NewChangeVariables(SenB, NSenB.children[i].leaf, NSenA.children[i])
	elif NSenA.children[i].type == 'VARIABLES':
	    NewChangeVariables(SenA, NSenA.children[i].leaf, NSenB.children[i])
    for i in range(len(SenA)):
	if i != m:
            NSenStr.append(TreetoStr(SenA[i]))
    for i in range(len(SenB)):
	if i != n:
	    NSenStr.append(TreetoStr(SenB[i]))
    return [True, NSenStr]

def TreetoStr(Tree):
    if Tree.type == 'PAREN':
	for i in range(len(Tree.children)):
	    if i == 0:
	        NStr = TreetoStr(Tree.children[i])
	    else:
		NStr = NStr + ',' + TreetoStr(Tree.children[i])
        return Tree.leaf + '(' + NStr + ')'
    if Tree.type == 'CONSTANTS' or Tree.type == 'VARIABLES':
	return Tree.leaf

def NewChangeVariables(SenArray, OVar, NVar):
    for i in range(len(SenArray)):
        NewReplaceVariables(SenArray[i], OVar, NVar)

def NewReplaceVariables(Tree, OVar, NVar):
    if Tree.type == 'VARIABLES' and Tree.leaf == OVar:
        if isinstance(NVar, str):
	    Tree.leaf = NVar
	else:
	    Tree.type, Tree.children, Tree.leaf = NVar.type, NVar.children, NVar.leaf
    for i in range(len(Tree.children)):
	if Tree.children != []:
            NewReplaceVariables(Tree.children[i], OVar, NVar)

#The following two function find whether two liters in a clause can be factored according to the rules and factor them.
def Factoring(Clause):
    i = 0
    while i <= len(Clause)-2:
	j = i+1
	while j <= len(Clause)-2:
            FactorPara = Factorable(Clause[i], Clause[j])
	    if FactorPara[0] == True:
		if FactorPara[1] == 1:
		    Clause.pop(j)
		else:
		    Clause.pop(i)
	    j += 1
        i+= 1
    return Clause

def Factorable(Liter1, Liter2):
    Abetter, Bbetter = 0, 0
    SenA = AtomicSentenceParser.atomicparse(Liter1)
    SenB = AtomicSentenceParser.atomicparse(Liter2)
    if SenA.leaf == SenB.leaf and SenA.leaf != 'not':
	for i in range(len(SenA.children)):
            if SenA.children[i].type == 'VARIABLES':
                Abetter = 1
	    elif SenB.children[i].type == 'VARIABLES':
		Bbetter = 1
	    elif SenA.children[i].leaf != SenB.children[i].leaf:
		Abtter, Bbetter = 1, 1
        if Abtter == 1 and Bbetter == 1:
	    return False, 1, 1
	else:
	    return True, 1-Bbetter, Bbetter
    else:
        return False, 1, 1

#This part parse the input sentences of a knowledge base into trees

Onetime = True
while Onetime:
    try:
        s = raw_input('Please ask a question about KB > ')   # use input() on Python 3
    except EOFError:
        print
        break

    try:
        Complete = raw_input("Do you need complete resolution? ('Y' or 'N') > ")   # use input() on Python 3
    except EOFError:
        print
        break

    import SentenceParser
    file = open('KB_Enemy.txt', 'r')
    data = file.read()
    file.close()
    data = data.split('\n')
    data.remove('')
    data.append(s)
    NumberofClauses = 0
    SentenceArray = [[]]
    for j in range(len(data)):
        SingleSentence = data[j]
        tree = SentenceParser.parse(SingleSentence)

#This part find the position of implies '=>' in every sentence and sort them according to the depth in the tree. Then remove them according to the rule 'A => B' equals 'not(A) | B'
        layer = 0
        ImpliesPosition = [[tree, -1]]
        FindImplies(tree)
        ImpliesPosition.sort(key = lambda x: int(x[1]), reverse = True)
        for i in range(len(ImpliesPosition)-1):
            ImpliesPosition[i][0].leaf = '|'
            ApplyNot(ImpliesPosition[i][0].children[0])

#Reverse the query
        if j == len(data) - 1:
	    ApplyNot(tree)

#This part apply variable standardization to each sentence to reduce confusion before we drop the quantifiers. Every quantifier is in charge of all the variables to the right of it in its group.
        Variables = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v']
        OldVariables = []
        FindOVariables(tree)
#All the old variables are picked out and abondoned. Later they will be replaced by new variables. This is a simple way to avoid conflict when we replace them.
        for i in range(len(OldVariables)):
            if OldVariables[i] in Variables:
                Variables.remove(OldVariables[i])
        AssignOrder = 0
        AssignNewQuantifiers(tree)

#This part apply skolemization to existial quantifiers. The rule is that the arguments of the Skolem function are all the universally quantified variables in whose scope the existential quantifier appears.
        SkolemFunctions = ['Fa', 'Ga', 'Ha', 'Ia', 'Ja', 'Ka'] 
        FunctionAssignOrder = 0
        UniversialVar = []
        AssignSkolemFunctions(tree, UniversialVar)

#This part will remove all the quantifiers by making a copy of the original tree ignoring all the quantifiers.
        NewTree = RemoveQuantifiers(tree)
        tree = NewTree

#This part will distribute the 'or' and 'and' function to form a CNF. General rule is like '(A and B) or C' results in '(A or C) and (B or C)'. My strategy is to find all the 'or's and move them to the bottom of the tree until there is no 'and' blow it, starting from the 'or' with the maximum depth.
        layer = 0
        OrsPosition = [[tree, -1]]
        FindOrs(tree)
        OrsPosition.sort(key = lambda x: int(x[1]), reverse = True)
        for i in range(len(OrsPosition)-1):
            DistributeOrAnd(OrsPosition[i][0])

#This part will separate each clauses in CNF and store them in a 2D list. The first dimension of the list indicates different clauses. Single Elements are all atomic sentences. For example, if the sentence is [A or B] & [C or D or E], SentenceArray = [[A, B], [C, D, E]].
        SeparateClauses(tree)
    
    import AtomicSentenceParser
   
#This part add the length of each element of SentenceArray to the end of each element of it and then sort it according to the length of each clause to make sure that resolution has a order from shorter clauses to longer clauses.
    for i in range(len(SentenceArray)):
        SentenceArray[i].append(len(SentenceArray[i]))

#If Complete is N, the first resolution will only be carried out between the KB and the query. No resolution between KB clauses.
    if Complete == 'Y' or Complete == 'y':
	NewSentence = SentenceArray
        SentenceArray = []
    else:
	NewSentence = [[],SentenceArray[-1]]
	SentenceArray.pop()

    SentenceArray.sort(key = lambda x: int(x[-1]))

#Apply factoring to KB and the query
    for i in range(1,len(SentenceArray)):
	SentenceArray[i] = Factoring(SentenceArray[i])

#Resolution starts here
    NoStop, Result = True, False
    j = 0
    Firstiteration = True
    while NoStop:
	j += 1 
	Substitute = NewSentence
	print j
        NoStop, NewSentence = Resolution(SentenceArray, NewSentence)
	for i in range(1, len(NewSentence)):
	    NewSentence[i] = Factoring(NewSentence[i])
	for i in range(len(NewSentence)):
	    NewSentence[i].append(len(NewSentence[i]))
        for i in range(1,len(Substitute)):
            SentenceArray.append(Substitute[i])
        if NoStop == True and NewSentence == []:
	    NoStop, Result = False, True
	Firstiteration = False
    print Result

    Onetime = False
    


			 


