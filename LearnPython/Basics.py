#Variables denoted as Var
Char = 'A' #A char only has one symbol/character in ''
Str = "ABC123$%^" #A String denoted as "str" contains multiple symbols/character in ""
Int = 10 #An integer dentoed as "int" contains a whole number 
Float = 1.7 #A float contains a number containing a decimal
Bool = True #A boolean variable denoted as bool is a variable that is either true or false

#Lists
List = [1, 2, 3, 4] #Also a variable. Data structure that stores multiple data points can get bigger. Can store numbers and letter in the same list.
List.append(5) #Putting .append on the end of the list varibale name will add whatever is inside of the () to the end of the list.
List.insert(0,0) #Putting .insert on the end of the list variable name will insert the number in the second position(x) (y,x) into the corrisponding place of the first position(y). So it would put X into place y and push everything else down. Or in this case it would put 0 into the first place and move 1 to 2 and 2 to 3 all the way down. 0 is the first position and 1 is the second position so on and so forth.
List.pop () #Putting .pop on the end of the list variable name will remove the last item from the list
VarName = List.pop() #This will take the last item off the list and then "VarName" would become that item
List.remove(2) #This would take out the 2 in the list. If there were 2 2's in the list it would search linearly and take out the first instance aka take out the first 2 it comes across and leaves the others.

print(f"Length: {len(List)}") 
#f indicates that you have some form of code or variabe that has an output inside of brackets it looks for the bracket and executes the code inside of the brackets then it adds that to the string that gets printed.
#len takes the length of the list and returns the length and it gets put where the {} is it will just have the number so it would print Length: 6 if the length of the list was 6

#loops
for i in List:
    print(i)
#The i will go down the list and take the place of each data point and then preform the code below. If the list was [1, 2, 3] i would become 1 and then it would print 1 then i would become 2 and then it would print to same thing with 3.
for _ in range(5):
    print("hellobitch")
#Used _ because I don't care about that variable. This will do the code below for that range so since the range is five and it says to print hellobitch ubnder it it will print hello bitch 5 times.
for e in range(4,7):
    print(e)
#e in this case does the same thing as i above but in the case of this range it will take the place off the first number in the range and all the nexts ones until it reaches the last number in the range and it will not preform the function for the last number in the range.

while(Bool): #While whatever is inside () is true the code below is run. Once the statement inside the () is false it moves to the next lines and skips the stuff inside the while loop.
    print(Int)
    #you could put other stuff here
    if Int == 0:
        Bool = False
    elif Int ==5:
        print("We're Half Way There")
        Int -= 1
    else:
        Int -= 1
# == logical equivilave is this equal to that. != is this something other than that. -= subtracts one. += adds one. *= will multiple this by that. /= will divide this by that. % will divide this by that and then give the remander so if its Bac%2 and Bac=13 it will divide 13 by 2 and spit out 1 good to know if something is odd.

if Int == 1 and len(List) >5: #Both of these condition must be met in order for this to run
    print ("Yippie")
if Int == 1 or Char is 'A': #If either of these conditions are met it will run. For a variable that isn't a number use is and is not instead of == and !=
    print ("welp")
if 1 in List: #In looks to see if something is in a variable
    pass #Ignore this the computer does. Ill come later basically



