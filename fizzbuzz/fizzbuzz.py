# Just a slightly overengineered version of FizzBuzz, 
# with the ability to easily add more checkers and substitution words.

from typing import Callable

class NumberChecker:
    """
    A class that checks if a number satisfies a certain condition, and returns
    a substitution word if it does.
    
    Attributes:
		subsitutionWord (str): The word to substitute if the condition is 
        	satisfied.
		checkerFunction (Callable[[int], bool]): A function that takes an 
        	integer and returns a boolean indicating whether the condition is 
            satisfied.

	Methods:
		check(number: int) -> str: Checks if the number satisfies the condition
			and returns the substitution word if it does, or an empty string if 
            it doesn't.
	"""			

    def __init__(
            self, 
            subsitutionWord: str, 
            checkerFunction: Callable[[int], bool]
        ) -> None:
        self.subsitutionWord = subsitutionWord
        self.checkerFunction = checkerFunction

    def check(self, number: int) -> str:
        """
        Checks if the number satisfies the condition and returns the 
        substitutionword if it does, or an empty string if it doesn't.
        
        Arguments:
			number (int): The number to check.
        
        Returns:
        	str: The substitution word if the condition is satisfied, or an 
            	empty string if it isn't.
        """
        if self.checkerFunction(number):
            return self.subsitutionWord
        else:
            return ""


class CheckerList:
    """
    A class that holds a list of NumberCheckers and checks a number against 
    all of them,concatenating the substitution words of all the checkers that 
    are satisfied.
    
    Attributes:
		checkers (list[NumberChecker]): A list of NumberCheckers to check 
        	against.
    
    Methods:
		checkAll(number: int) -> str: Checks the number against all the 
			NumberCheckers in the list and concatenates the substitution words 
            of all the checkers that are satisfied. If no checkers are 
            satisfied, it returns the number as a string.
	"""
    checkers: list[NumberChecker] = list()

    def __init__(self, checkers: list[NumberChecker]) -> None:
        self.checkers = checkers

    def checkAll(self, number: int) -> str:
        """
        Checks the number against all the NumberCheckers in the list and 
		concatenates the substitution words of all the checkers that are
        satisfied. If no checkers are satisfied, it returns the number as a
        string.
        
        Arguments:
			number (int): The number to check against the list of 
            	NumberCheckers.
            
		Returns:
        	str: The concatenated substitution words of all the checkers that 
            	are satisfied, or the number as a string if no checkers are 
                satisfied.
        """
        
        output = ""

        for checker in self.checkers:
            output += checker.check(number)

        return output or str(number)


def main():
    checkerList = CheckerList(
        [
            NumberChecker("Fizz", lambda n: n % 3 == 0),
            NumberChecker("Buzz", lambda n: n % 5 == 0),
            NumberChecker("Bizz", lambda n: n % 7 == 0)
        ]
    )

    for n in range(1, 101):
        output = checkerList.checkAll(n)
        print(output)


if __name__ == "__main__":
    main()