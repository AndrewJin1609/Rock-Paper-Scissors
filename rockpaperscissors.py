import microbit # Do not change these to star imports, the test code needs them
import utime    # like this to work properly!
import radio

# Global constants
ROCK = microbit.Image('00000:09990:09990:09990:00000')
PAPER = microbit.Image('99999:90009:90009:90009:99999')
SCISSORS = microbit.Image('99009:99090:00900:99090:99009')
RPS = (b'R', b'P', b'S')
radio_address = b'0000' # Default value and needs to be changed in the main function
MYID = b'2f' 

def choose_opponent():
    """
    Returns the opponent id from button presses

    Returns
    -------
    byte string:
       A two-character byte string representing the opponent ID

    Notes
    -------
    Button A is used to increment a digit of the ID
    Button B is used to 'lock in' the digit and move on
    """

    # This function is complete.

    # Initialization
    num = [0]*2
    idx = 0
    
    # Main loop over digits
    while idx < len(num):
        microbit.sleep(100)
        # Display only the last character of the hex representation (skip the 0x part)
        microbit.display.show(hex(num[idx])[-1], wait=False)
        # The button increments the digit mod 16, to make sure it's a single hex digit
        if microbit.button_a.was_pressed():
            num[idx] = (num[idx] + 1)%16
        # Show a different character ('X') to indicate a selection
        if microbit.button_b.was_pressed():
            microbit.display.show('X')
            idx += 1
    microbit.display.clear()
    
    # Make sure we return a byte string, rather than a standard string.
    return bytes(''.join(hex(n)[-1] for n in num), 'UTF-8')


def create_address(player_id, opp_id):
    """
    Returns a byte string in the representing the communication address.

    Parameters:
        player_id (byte_string): A two-character byte string representing the player ID
        opp_id (byte_string): A two-character byte string representing the opponent ID

    Returns:
        (byte string): A 4 character byte string representing the address.
                       The string should be concatenated such that the player with the
                       larger ID comes second.
    """

    # Decoding to string datatype
    player_s = str(player_id, 'UTF-8')
    opp_s = str(opp_id, 'UTF-8')
    
    # Deciding string concatenation order based on hex value
    if int(player_s, 16) > int(opp_s, 16):
        string = opp_s + player_s
    else:
        string = player_s + opp_s

    # Encoding to bytes datatype
    return bytes(string, "UTF-8")
    

def choose_play():
    """
    Returns the play selected from button presses

    Returns:
       (byte string): A single-character byte string representing a move, as given in
                      the RPS list at the top of the file.

    Notes:
       Button A is used to cycle between R (rock), P (paper), and S (scissors).
       Button B is used to confirm the selection.
    """

    # Initialisation
    num = 1
    play = ''
    
    # Creating event loop
    while True:
        microbit.sleep(100)

        # Selection process
        if microbit.button_a.was_pressed():
            num += 1

            # Creating an infinite loop of 0, 1, and 2
            selection = num % 3

            # Starting loop from 'Rock'
            if selection == 2:
                microbit.display.show('R')
                play = 'R'
            elif selection == 0:
                microbit.display.show('P')
                play = 'P'
            else:
                microbit.display.show('S')
                play = 'S'

        # Confirming selection process
        if microbit.button_b.was_pressed():

            # Flashing choice on microbit 2 times, then clear
            for i in range(2):
                microbit.display.clear()
                microbit.sleep(300)
                microbit.display.show(play)
                microbit.sleep(300)

            microbit.display.clear()

            # Exiting loop
            break
            
    return bytes(play, 'UTF-8')


def send_choice(play, round_number):
    """
    Sends a message via the radio.

    Parameters:
       play (byte string): One of b'R', b'P', or b'S'.
       round_number (int): The round that is being played.

    Returns:
       (int): Time that the message was sent.
    """

    # Formatting message and sending
    message = play + bytes(str(round_number), 'UTF-8')
    radio.send_bytes(message)

    # Returning time
    return utime.ticks_ms()


def send_acknowledgement(round_number):
    """
    Sends an acknowledgement message.

    Parameters:
        round_number (int): The round that is being played.
    """

    # Formatting message and sending
    message = b'X' + bytes(str(round_number), 'UTF-8')
    radio.send_bytes(message)


def parse_message(round_number):
    """
    Receive and parse the next valid message

    Parameters:
        round_number (int): The round that is being played.

    Returns:
        (bytes): The contents of the message, if it is valid
        None: If the message is invalid or does not need further processing

    Notes:
        This function sends an acknowledgement using send_acknowledgement() if
        the message is valid and contains a play (R, P, or S), using the round
        number from the message.
    """

    # Receiving message
    message = radio.receive_bytes()

    # Checking if message is of the correct format
    if message == None or len(message) != 2 or message[1:2] != bytes(str(round_number), 'UTF-8'):
        return None

    # Responding and returning play value if needed
    if message[0:1] in RPS:
        send_acknowledgement(round_number)
        return message
    elif message[0:1] == b'X':
        return message
    else:
        return None


def resolve(my, opp):
    # """ Returns the outcome of a rock-paper-scissors match
    # Also displays the result
    #
    # Parameters
    # ----------
    # my  : bytes
    #     The choice of rock/paper/scissors that this micro:bit made
    # opp : bytes
    #     The choice of rock/paper/scissors that the opponent micro:bit made
    #
    # Returns
    # -------
    # int :
    #     Numerical value for the player as listed below
    #      0: Loss/Draw
    #     +1: Win
    # int opp_score :
    #     Numerical value for the opponent as listed below
    #      0: Loss/Draw
    #     +1: Win
    #
    # Notes
    # -----
    # Input parameters should be one of b'R', b'P', b'S'
    #
    # Examples
    # --------
    # solve(b'R', b'P') returns 0 (Loss)
    # solve(b'R', b'S') returns 1 (Win)
    # solve(b'R', b'R') returns 0 (Draw)
    #
    # """
    #
    # This function is complete.

    # Use fancy list indexing tricks to resolve the match
    diff = RPS.index(my) - RPS.index(opp)
    result = [0, 1, 0][diff]
    opp_score = [0,0,1][diff]
    # Display a cute picture to show what happened
    faces = [microbit.Image.ASLEEP, microbit.Image.HAPPY, microbit.Image.SAD]
    microbit.display.show(faces[diff])
    # Leave the picture up for long enough to see it
    microbit.sleep(1000)
    return result, opp_score
    

def display_score(my_score,opp_score,round_number, times=3):
    # """ Flashes the score on the display
    #
    # Parameters
    # ----------
    # my_score : int
    #     The current player score
    # opp_score : int
    #     The current opponent score
    # round_number : int
    #     The current round number
    # times : int
    #     Number of times to flash
    #
    # Returns
    # -------
    # None
    #
    # Notes
    # -----
    # Decides if the game is won or lost or drawn.
    # Resolves the game when one player is deemed a winner or loser.
    # Resets the microbit after the game is complete.
    #
    # This function is complete.
    screen_off = microbit.Image(':'.join(['0'*5]*5))
    microbit.display.show([screen_off, str(my_score)]*times)
    if round_number == 2:
        if my_score == 2:
            for n in range(times):
                microbit.display.scroll("You win!!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        elif opp_score == 2:
            for n in range(times):
                microbit.display.scroll("You Lose!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        else:
            pass
    elif round_number == 3:
        if my_score > opp_score:
            for n in range(times):
                microbit.display.scroll("You win!!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        elif opp_score > my_score:
            for n in range(times):
                microbit.display.scroll("You Lose!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()
        elif (opp_score == my_score):
            for n in range(times):
                microbit.display.scroll("You drew!")
                microbit.display.show(screen_off)
                microbit.sleep(333)
                microbit.reset()


def main():
    """ 
    Main control loop.
    """
    # Selecting opponent
    opponent_id = choose_opponent()

    # Establishing radio address
    radio_address = create_address(MYID, opponent_id)
    decimal_number = int.from_bytes(radio_address, 'little')
    
    # Setting up the radio for moderate range
    radio.config(power=6, address = decimal_number)
    radio.on()
    
    # Initialising score and round number
    your_score = 0
    opp_score = 0
    round_number = 1
    
    # Run a best of 3 long RPS contest
    while True:
        microbit.display.scroll("Round: " + str(round_number),delay=40,monospace=True)
        microbit.display.scroll("Your Score: " + str(your_score),delay=40,monospace=True)
        
        # Obtain and send a play
        choice = choose_play()
        send_time = send_choice(choice, round_number)
        
        # Passive waiting display
        microbit.display.show(microbit.Image.ALL_CLOCKS, wait=False, loop=True)
        acknowledged, resolved = (False, False)
        
        while not (acknowledged and resolved):
            
            # Obtaining opponent message from radio
            message = parse_message(round_number)

            # Filtering messages so that only one play and one acknowledgement is processed per round
            if message:
                action = message[0:1]
                
                # If action is a play
                if action in RPS and resolved == False:
                
                    # Resolving round
                    my_result, opp_result = resolve(choice, message[0:1])
                    resolved = True
    
                    # Updating and displaying score
                    your_score += my_result
                    opp_score += opp_result
                    display_score(your_score, opp_score, round_number, times=3)

                # If action is an acknowledgement
                elif action == b'X' and acknowledged == False:
                    acknowledged = True 
                    
            # Resends message if not acknowledged and time has passed
            if acknowledged == False:
                current_time = utime.ticks_ms()
                if utime.ticks_diff(current_time, send_time) > 2000:
                    send_time = send_choice(choice, round_number)
                       
        # Updating round number
        round_number += 1

# Do not modify the below code, this makes sure your program runs properly!
if __name__ == "__main__":
    main()