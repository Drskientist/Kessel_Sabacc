from os import system
from sys import exit
from time import sleep


class UserInterface:

    def wait(self, time: int) -> None:
        sleep(time)

    def clr(self) -> None:
        system('cls')
    
    def exit(self) -> None:
        self.clr()
        exit()

    def errorMsg(self, _txt: str = 'Bad Computer Stuff', _delay: int | float = 3) -> None:
        self.clr()
        print(f'!!!   {_txt.upper()}   !!!')
        sleep(_delay)
    
    def title(self, txt: str, _buffer: int = None, _doClr: bool = True) -> None:
        if _doClr is True:
            self.clr()
        top: str = '___'
        bottom: str = '|__'
        for i, char in enumerate(list(txt)):
            if char == ' ':
                bottom += '_'
            else:
                bottom += char.upper()
            top += '_'
        if _doClr is True:
            self.clr()
        print(f'\n{top}___')
        print(f'{bottom}__|')
        if _buffer is not None:
            for i in range(_buffer):
                print('')
        else:
            print('')

    def selection(self, options: list, _txt: str = None, _data: str = None, _buffer: int = None, _doClr: bool = True,
                  _doTitle: bool = True) -> int:
        while True:
            if _doTitle is True and _txt is not None:
                self.title(_txt, _buffer, _doClr)
            if _data is not None:
                print(_data)
            for i, opt in enumerate(options):
                print(f'{i+1}] {opt}')
            print('')
            try:
                path = int(input('>>>'))
                if 0 < path < len(options)+1:
                    return path
                else:
                    raise ValueError
            except ValueError:
                self.errorMsg()
    
    def userInput(self, data: str, rtnType: str or int or float = str, _titleTxt: str = None, _buffer: int = None,
                  _doClr: bool = True, _inputIcon: str = '>>>') -> str or int or float:
        while True:
            if _titleTxt is not None:
                self.title(_titleTxt, _buffer, _doClr)
            elif _doClr is True and _titleTxt is None:
                self.clr()
            print(f'{data}\n')
            try:
                x = input(_inputIcon)
                for i in range(2):
                    if isinstance(x, rtnType):
                        return x
                    else:
                        if isinstance(rtnType, int):
                            x = int(x)
                        else:
                            x = float(x)
            except ValueError:
                self.errorMsg()

    def getBool(self, data: str, _titleTxt: str = None, _buffer: int = None, _doClr: bool = True) -> bool:
        while True:
            if _titleTxt is not None:
                self.title(_titleTxt, _buffer, _doClr)
            print(f'{data}\n\n1] Yes\n2] No\n')
            try:
                x = int(input('>>>'))
                if 0 < x < 3:
                    if x == 1:
                        return True
                    else:
                        return False
                else:
                    raise ValueError
            except ValueError:
                self.errorMsg()

if __name__ == '__main__':
    ui = UserInterface()
    while True:
        x = ui.selection('debug userinterface', ['Debug Error Message', 'Debug User Input', 'Exit'])
        if x == 1:
            ui.errorMsg()
        elif x == 2:
            while True:
                y = ui.selection('debug user input', ['Test String Return', 'Test Integer Return', 'Test Float Return', 'Return to Menu'])
                if y == 1:
                    z = ui.userInput('Type Any String Below', str())
                elif y == 2:
                    z = ui.userInput('Type Any Integer Below', int())
                elif y == 3:
                    z = ui.userInput('Type Any Float Below', float())
                else:
                    break
                print(f'{z}')
                input('PETC')
        else:
            ui.clr()
            exit()