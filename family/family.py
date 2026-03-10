def get_family(n: int) -> None:
    """
    Prints the family members of a person n generations away from them.
    
    Args:		
    	n (int): The number of generations away from the person.
        
	Returns:
		None
	"""
    if verify_input(n):
        n = int(n)
        #proportion = 1/2 ** n
        output = '1/' + str(2**n) + ':\n'

        # Thresholds of n at which ancestor types occur
        you_threshold = 0
        parent_child_threshold = 1
        sibling_threshold = 1
        uncle_nibling_threshold = 2
        cousin_threshold = 3

        # Add you if n is threshold
        if n == you_threshold:
            output += 'you\n'

        # Calculate the parents and children
        # and their great/grand prefixes for n
        if n >= parent_child_threshold:
            # _parents
            output += ' '.join(['great'] * (n - 2))
            if n >= 2: output += ' grand'
            output += 'parent\n'

            # _children
            output += ' '.join(['great'] * (n - 2))
            if n >= 2: output += ' grand'
            output += 'child\n'

        # Add siblings if n is threshold
        if n == sibling_threshold:
            output += 'sibling'

        # Calculate the uncles/aunts and niblings
        # and their great prefixes
        if n >= uncle_nibling_threshold:
            # _uncles
            output += ' '.join(['great'] * (n - 2))
            output += ' uncle/aunt\n'

            # _niblings
            output += ' '.join(['great'] * (n - 2))
            output += ' nibling\n'

        # Calculate cousins and their prefixes
        # and removednesses
        if n >= cousin_threshold:
            cousin = 1
            removal = n - 3

            while removal > -1:
                output += str(cousin) + ' cousin '
                if removal > 0:
                    output += str(removal) + ' removed\n'
                cousin += 1
                removal -= 2
        
        # Capitalise first letter of each line
        output_lines = output.split('\n')
        for line in output_lines:

            line = line.lstrip().capitalize()
            print(line)


# Verify input
def verify_input(n: int) -> bool:
    """
    Verifies that n is a positive integer.
    
    Args:		
		n (int): The number of generations away from the person.
        
	Returns:
		bool: True if n is a positive integer, False otherwise.
	"""
    try:
        if not float(n).is_integer():
            raise ValueError('n must be an integer.')
        elif int(n) < 0:
            raise ValueError('n must be greater than 0.')
    except ValueError as error:
        print(error)
        return False

    return True


def main():
    n = int(input('Enter n: '))
    get_family(n)


if __name__ == "__main__":
    main()