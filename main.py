from sys import argv
from time import sleep

from Menu_MakerV2 import UserInterface
from Sabacc import Sabacc, Player


def _do_ai_action(sabacc: Sabacc, player: Player) -> True or False or None:
    data = [sabacc.discard_pile['sand'][0], sabacc.discard_pile['blood'][0]]
    hand_change = None
    match player.do_round(data):  # player.do_round = AI brain | Needs discard pile data to work
        case [0]: # Stand
            return False
        case [1, 0]: # Draw from the random Sand deck
            player.discard = sabacc.deck['sand'][0]
            hand_change = 'sand'
        case [1, 1]: # Draw from the random Blood deck
            player.discard = sabacc.deck['blood'][0]
            hand_change = 'blood'
        case [2, 0]: # Draw from the Sand discard pile
            player.discard = sabacc.discard_pile['sand'][0]
            hand_change = 'sand'
        case [2, 1]: # Draw from the Blood discard pile
            player.discard = sabacc.discard_pile['blood'][0]
            hand_change = 'blood'
        case [3]: # Forfeit
            print('AI FORFEIT')
            sabacc.player_list.remove(player)
            return True
    match player.confirm_choice(hand_change): # confirm which card the AI wants to keep
        case 1: # Discard currently held card
            sabacc.do_discard(player, hand_change, False)
        case 2: # Discard last pulled card
            sabacc.do_discard(player, hand_change)

def _CLI_draw_card(sabacc: Sabacc, plr: Player) -> bool:
        fam = ui.selection(['Last Discarded Sand Card',
                            'Random Sand Card',
                            'Random Blood Card',
                            'Last Discarded Blood Card',
                            'Change Choice'],
                           _data='Which Family and Stack?', _doTitle=False, _doClr=False, _buffer=1)
        if 0 < fam < 3:
            deck_id = 'sand'
        elif 2 < fam < 5:
            deck_id = 'blood'
        else:
            return False
        if fam == 2 or fam == 3:
            plr.discard = sabacc.deck[deck_id].popleft()
        else:
            plr.discard = sabacc.discard_pile[deck_id].popleft()
        plr.round_bet += 1
        discard = ui.selection([f'{plr.discard} | Drawn Card',
                                f'{plr.hand[deck_id]} | Current Card'],
                               _data='Which would you like to discard?', _doClr=False, _doTitle=False)
        if discard == 1:
            discard = True
        else:
            discard = False
        sabacc.do_discard(plr, deck_id, discard)
        return True

def _test_game_loop(sabacc: Sabacc, _simulate: bool = False) -> Player or str:
    while len(sabacc.player_list) > 1:
        # Initialize Round and Display Round Number
        sabacc.init_round()
        ui.clr()
        sabacc.round_data['number'] += 1
        plr_list = sabacc.player_list
        print(f'\n\n|||   ROUND {sabacc.round_data['number']}   |||')
        sleep(1)
        for turn in range(3): # Loop for the 3 turns
            for player in plr_list:
                opts = ['Stand', 'Forfeit']
                if player.tokens > 0:
                    opts.insert(1, 'Draw')
                if _simulate is False: # If the game is not being simulated
                    if player.is_ai is False:
                        if player.find_new_name is True:
                            player.name = ui.userInput('Name Yourself!', _doClr=False)
                            player.find_new_name = False
                        while True: # Mistake Loop
                            ui.clr()
                            print(f'|   PLAYER: {player.name}\n|   Tokens: {player.tokens - player.round_bet}/{sabacc.tokens}\n|   Turn {turn + 1}/3\n|')
                            print(f'|   DISCARD   |   SAND   |   BLOOD   |   DISCARD')
                            print(f'|      {sabacc.discard_pile['sand'][0]}      |    X     |    X      |      {sabacc.discard_pile['blood'][0]}')
                            print(f'|\n|      HAND   \n|   {player.hand['sand']}   |   {player.hand['blood']}\n   SAND    BLOOD\n')
                            choice = ui.selection(opts, _doTitle=False, _doClr=False) # Get user input as choice
                            if choice == 2 and len(opts) == 2: # Correcting for different opt sizes
                                choice += 1
                            match choice:
                                case 1: # Chose to Stand
                                    if ui.getBool('Are you Sure?', _doClr=False) is False:
                                        continue
                                    else:
                                        break
                                case 2: # Chose to Draw
                                    if _CLI_draw_card(sabacc, player) is False:
                                        continue
                                    else:
                                        break
                                case 3: # Choose to Forfeit
                                    confirm = ui.userInput('ARE YOU SURE YOU WANT TO FORFEIT?\n'
                                                           'TYPE "YES" TO CONFIRM, TYPE ANYTHING ELSE TO CANCEL')
                                    if confirm == 'yes' or confirm == 'Yes' or confirm == 'YES':
                                        sabacc.player_list.remove(player)
                                        break
                                    else:
                                        continue
                    elif player.is_ai is True:
                        match _do_ai_action(sabacc, player):
                            case False:
                                continue
                            case True:
                                break
                            case None:
                                pass
                    else:
                        break
                elif _simulate is True:
                    match _do_ai_action(sabacc, player):
                        case False:
                            continue
                        case True:
                            break
                        case None:
                            pass
                else:
                    return 'INVALID _simulate VALUE'
        round_winner = sabacc.eval_hands() # Evaluates current game-state and returns who's winning
        ui.clr()
        for player in sabacc.player_list: # Loop to decide who gets taxed and for how much
            player.eval_hand() # Player class looks at their hand and updates all relevant data
            if player != round_winner:
                if player.hand_rating == 0 or player.hand_rating == 3:
                    tax = 1
                elif player.hand_rating == 1:
                    tax = player.difference
                elif player.hand_rating == 2:
                    if (player.difference - 1) == 0:
                        tax = 1
                    else:
                        tax = player.difference - 1
                else:
                    tax = player.difference
            else:
                tax = player.round_bet
            # Displays results and deducts tokens appropriately
            print(f'|  Player: {player.name}')
            print(f'|  Hand: {player.hand['sand']} | {player.hand['blood']} | {player.hand_type}\n|')
            if player == round_winner:
                print(f'|   You Win {tax} Tokens back and avoid Taxes!')
                print(f'|   Tokens: {player.tokens}/{sabacc.tokens}\n|')
                player.tokens += tax
            else:
                print(f'|   You Lose {player.round_bet} Tokens to Betting and {tax} Tokens to Taxes')
                deduction, pre_deduction = player.round_bet + tax, player.tokens
                if player.tokens <= deduction:
                    player.tokens = 0
                else:
                    player.tokens -= deduction
                print(f'|   Tokens: {pre_deduction} -> {player.tokens}/{sabacc.tokens}\n|')
            if player.tokens == 0: # Checks if a player lost
                sabacc.player_list.remove(player) # removes player from list
                print('You Lost!\n|')
        input('PETC')
    if len(sabacc.player_list) == 1: # Checks if there is only 1 player left
        return sabacc.player_list[0]
    else:
        return 'DRAW'

if __name__ == '__main__':
    _do_CLI = False
    for i, arg in enumerate(argv): # Check system args to see what mode to run in, currently only CLI works
        if arg == '-m':
            if argv[i+1] == 'cli':
                _do_CLI = True
    if _do_CLI is True:
        ui = UserInterface()
        temp_tokens, temp_AIs = 6, 3 # Default tokens and number of AIs
        while _do_CLI:
            match ui.selection(['Play', 'Settings', 'Quit'], 'kessel sabacc'): # CLI Main Menu
                case 1: # Play Game
                    while _do_CLI:
                        game = Sabacc(temp_tokens, temp_AIs+1, _do_single_player=True)
                        winner = _test_game_loop(game)
                        if isinstance(winner, Player) is True:
                            winner = winner.name
                        if ui.getBool('Play Again?', f'{winner} wins') is False:
                            break
                case 2: # Setting Menu
                    tkns, ais = temp_tokens, temp_AIs
                    test = ui.selection([f'Change Tokens: {tkns}',
                                           f'Change AI Amount: {ais}',
                                           f'Back to Menu'], 'settings')
                    match test:
                        case 1:
                            tkns = ui.userInput('How many Tokens? 4-12', int, _doClr=False)
                        case 2:
                            ais = ui.userInput('How many AIs? 1-3', int, _doClr=False)
                        case 3:
                            break
                    if tkns != temp_tokens and 3 < tkns < 13:
                        temp_tokens = tkns
                    if ais != temp_AIs and 0 < ais < 4:
                        temp_AIs = ais
                case 3: # Quit
                    ui.exit()
    else:
        UserInterface().exit()