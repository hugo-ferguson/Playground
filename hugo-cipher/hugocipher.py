def cipher_word(word: str) -> str:
    """
    Cipher a single word using the Hugo-Cipher.

    Arguments:
        word (str): The input word to convert into the cipher.

    Returns:
        string: The ciphered word.
    """
    VOWELS = ['a', 'e', 'i', 'o', 'u']
    cipher = ''

    # Strip spaces from the word.
    for char in word.strip():
        # Add the current character to the cipher output.
        cipher += char

        # If the current character is a vowel, reverse the ciphered text
        # up to this point and add it to the ciphered text.
        if char in VOWELS:
            # Slices the string.
            # Reverses the text from the start to the current position - 1.
            cipher += cipher[-2::-1]

    return cipher


def cipher_sentence(sentence: str) -> str:
    """
    Cipher an entire sentence using the Hugo-Cipher.
    Applies the cipher to each word in the sentence and returns the entire
        sentence with each word ciphered.

    Arguments:
        sentence (str): The input sentence to convert into the cipher.

    Returns:
        string: The ciphered sentence.
    """
    # Split the sentence into words.
    words = sentence.split(' ')
    cipher = ''

    # Cipher each word.
    for word in words:
        cipher += cipher_word(word) + ' '

    # Remove the trailing space.
    return cipher.rstrip()


def main() -> None:
    input_text = input('Input: ')
    print(cipher_sentence(input_text))


if __name__ == "__main__":
    main()
