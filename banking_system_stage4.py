# banking system stage # 4

import random
import sqlite3

conn = sqlite3.connect('card.s3db') # single file database creation

cur = conn.cursor() # we're using this object's method 'execute' to perform queries

my_table_string = 'CREATE TABLE IF NOT EXISTS card (`id` INTEGER, `number` TEXT, `pin` TEXT, balance INTEGER DEFAULT 0);'

cur.execute(my_table_string)

conn.commit()

random.seed()

card_to_check = list() # Global variable. We're using it for the purpose of temporarily storing the account no. and the pin no. for the card to check. This list will count as a static property when switching to Object Oriented approach

account_to_transfer = 0

possible_options = ("1", "2", "0")

possible_balance_options = ("1", "2", "3", "4", "5", "0") # Global variable. It will count as a static property when switching to Object Oriented approach

# account_balance = 0 # Global variable. It will count as a static property when switching to Object Oriented approach

CREATE = True # Global variable. We're using it for diverting the execution flow to the "create" or "log into" or "exit" branch. This variable will amount to a static property when switching to Object Oriented approach

LOGIN = False # Global variable. See the explanation above

BALANCE = False # Global variable. See the explanation above

ADD = False # Global variable. See the explanation above

CHK_TRANSFER = False # Global variable. See the explanation above

# Auxiliary & printing functions

def get_user_input():
    return input().strip()

def print_exit_statement():
        print("\nBye!")
		
def print_first_menu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
	
def login_successfully_message():
    print("\nYou have successfully logged in!")
    
def logout_successfully_message():
    print("\nYou have successfully logged out!\n")
	
def print_balance_menu():
    print("\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit")

# CREATE True functions  

def Luhn_generator():
    '''
    It generates the pin no. and an associated, Luhn compliant, card number
    '''
    pin = ''
    for num in range (4):
        pin += str(random.randint(0, 9)) # this is the pin no.
        
    account_no = str(400000) # first 6 digits are constant
    last_digits = list() # a container for the remaining 10 digits
    original_digits = '' # The string corresponding to the digits' number
 
    digit_sum = 8
    for digit in range(9): # implementing the Luhn algorithm
        current_digit = random.randint(0, 9)
        last_digits.append(current_digit)
        original_digits += str(current_digit)
        
    for index in range(len(last_digits)):
        if index % 2 == 0:
            last_digits[index] *= 2
            if last_digits[index] > 9:
                last_digits[index] -= 9
        digit_sum += last_digits[index]
    
    check_digit = 0
    for chk in range(10):
        if (chk + digit_sum) % 10 == 0:
            check_digit = chk
            break
    original_digits += str(check_digit)
    
    account_no += original_digits
    
    return (account_no, pin)

def card_exists(card_number):
    placeholder = (card_number, )
    unique_check = "SELECT * FROM card WHERE number = ?"
    cur.execute(unique_check, placeholder)
    return cur.fetchone()    
    

def card_generator(card_data):
    temp_res1 = card_exists(card_data[0])
    
    if temp_res1 is None: # if this number hasn't been previously assigned
        no_pin = (card_data[0], card_data[1])
        insert_unique = "INSERT INTO card (number, pin) VALUES(?, ?)"
        cur.execute(insert_unique, no_pin)
        conn.commit()
        print(str.format("\nYour card has been created\nYour card number:\n{}\nYour card PIN:\n{}\n", card_data[0], card_data[1]))
        return True
    else:
        return False
       
# LOGIN True functions

def print_login_menu():
    if len(card_to_check) == 0:
        print("\nEnter your card number:")
    else:
        print("Enter your PIN:")

def login_checker(account, pin):
    # Data from table 'card' used here
    check_login_query = "SELECT number, pin FROM card WHERE number = ? AND pin = ?"
    placeholder = (account, pin)
    cur.execute(check_login_query, placeholder)
    temp_res = cur.fetchall()
    if len(temp_res) == 1:
        login_successfully_message()
        return True
    else:
        print("\nWrong card number or PIN!\n")  
        
# BALANCE True functions

def get_balance(account_number):
    # Data from table 'card' MUST be used here
    placeholder = (account_number,)
    balance_query = "SELECT balance FROM card WHERE number = ?"
    cur.execute(balance_query, placeholder)
    return cur.fetchone()[0] # this is the balance
    

def display_balance():
    temp_res3 = get_balance(card_to_check[0])
    print(str.format("\nBalance: {}", temp_res3))

def Luhn_checker(digit_string):
    digit_list = list(digit_string)
    if len(digit_list) != 16:
        return False
    try:
        for index in range(len(digit_list)):
            digit_list[index] = int(digit_list[index])
    except:
        return False
    
    # Luhn checker starts here
    digit_sum = digit_list[-1]
    for index in range(len(digit_list) - 1):
        if index % 2 == 0:
            digit_list[index] *= 2
            if digit_list[index] > 9:
                digit_list[index] -= 9
        digit_sum += digit_list[index]
    
    if digit_sum % 10 == 0:
        return True
    else:
        return False
		
def close_account():
    delete_query = "DELETE FROM card WHERE number = ?"
    placeholder = (card_to_check[0],) # because we're only allowed to close the account we're logged in
    cur.execute(delete_query, placeholder)
    conn.commit()

# ADD True

def add_income(amount):
    current_balance = get_balance(card_to_check[0])
    current_balance += int(amount)
    update_balance = "UPDATE card SET balance = ? WHERE number = ?"
    cur.execute(update_balance, (current_balance, card_to_check[0]))
    conn.commit()
    print("Income was added!")
    print_balance_menu()

# CHK_TRANSFER True

def check_transfer_acc(card_number):
    # print("You've just entered card number " + str(card_number))
    global CHK_TRANSFER
    global BALANCE
    CHK_TRANSFER = False
    BALANCE = True    
    if card_number == card_to_check[0]:
        print("You can't transfer money to the same account!")
        print_balance_menu()
    elif not Luhn_checker(card_number):
        print("Probably you made a mistake in the card number. Please try again!")
        print_balance_menu()
    elif card_exists(card_number) is None:
        print("Such a card does not exist.")
        print_balance_menu()
    else:
        BALANCE = False
        global account_to_transfer
        account_to_transfer = card_number
        print("Enter how much money you want to transfer:")

# All state constants on False

def perform_transfer(amount):
    current_balance_grantor = get_balance(card_to_check[0])
    if current_balance_grantor < int(amount):
        print("Not enough money!")
    else:
        current_balance_receiver = get_balance(account_to_transfer)
        placeholder1 = (current_balance_grantor - int(amount), card_to_check[0])
        placeholder2 = (current_balance_receiver + int(amount), account_to_transfer)
        update_query = "UPDATE card SET balance = ? WHERE number = ?"
        cur.execute(update_query, placeholder1)
        conn.commit()
        cur.execute(update_query, placeholder2)
        conn.commit()
        print("Success!")
        
    
#-------------------------------------------------------------------------------------------------------------------------------
#End of function definitions section; start of the function calls section

print_first_menu() # first call; first user input; default state is CREATE = True

while(True):
    usr_inp = get_user_input()
    
    if CREATE:
        if usr_inp in possible_options:
            if usr_inp == "1":
                while(not card_generator(Luhn_generator())):
                    pass
                print_first_menu()
            elif usr_inp == "2":
                cur.execute("SELECT * FROM card") # check if any cards have already been created
                temp_res2 = cur.fetchall()
                if 0 != len(temp_res2): # SELECT query returns a list of tuples, if list is empty, then there's no card created
                    CREATE = False
                    LOGIN = True
                    
                    print_login_menu()
                else:
                    print("\nNo account created yet!")
                    print_first_menu()
            else:
                print_exit_statement()
                exit()
        else:
            print("\nInvalid option")
            print_first_menu()
            
    elif LOGIN:  
        card_to_check.append(usr_inp) # account no. comes first, pin comes afterwards
        if len(card_to_check) != 2:
            print_login_menu()
        else:
            login_result = login_checker(card_to_check[0], card_to_check[1])
            
            if login_result:
                
                LOGIN = False
                BALANCE = True
                print_balance_menu()
            else:
                CREATE = True
                LOGIN = False
                
                card_to_check.clear() # Because we may want to try a new login
                print_first_menu()  
            
    elif BALANCE:
        if usr_inp in possible_balance_options:
            if usr_inp == "1":
                display_balance() 
                print_balance_menu()
            elif usr_inp == "2":
                BALANCE = False
                ADD = True
                print("\nEnter income:")
            elif usr_inp == "3":
                print("\nTransfer\nEnter card number:")   
                BALANCE = False
                CHK_TRANSFER = True
            elif usr_inp == "4":
                close_account()
                print("\nThe account has been closed!\n")  
                CREATE = True
                BALANCE = False # Leaving this branch and returning to the first menu
                card_to_check.clear() # Because the account no longer exists
                print_first_menu()
            elif usr_inp == "5":
                CREATE = True
                BALANCE = False # Leaving this branch and returning to the first menu
                card_to_check.clear() # Because we're logging out
                logout_successfully_message()
                print_first_menu()
            else: # exit branch
                print_exit_statement()
                exit()                 
        else:
            print("\nInvalid option!")
            print_balance_menu()
    
    elif ADD:
        add_income(usr_inp)
        BALANCE = True
        ADD = False
        
    elif CHK_TRANSFER:
        check_transfer_acc(usr_inp)
    
    else:
        perform_transfer(usr_inp)
        BALANCE = True
        print_balance_menu()
              