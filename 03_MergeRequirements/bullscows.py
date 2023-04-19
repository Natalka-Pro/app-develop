from collections import Counter
import random
import argparse
import urllib.request

def bullscows(guess: str, secret: str) -> tuple[int, int]:

    """Возвращает количество «быков» и «коров» из guess в secret"""

    bulls = [g == s for g, s in zip(guess, secret)] 
    bulls = sum(bulls)
    
    cows = Counter(guess) & Counter(secret) # пересечение
    cows = sum(cows.values())
    
    return bulls, cows


def ask(prompt: str, valid: list[str] = None) -> str:
    guess = input(prompt)

    if valid is not None:
        while guess not in valid:

            if ":(" in guess:
                raise TypeError("Он не знает :(")
                
            
            print("Такого слова нет :(")
            guess = input(prompt)

    return guess


def inform(format_string: str, bulls: int, cows: int) -> None:
    print(eval(f"format_string.format(bulls, cows)"))


def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    secret = random.choice(words)
    print("Слово загадано, ваши предположения? :)")
    guess = ""
    try_count = 0
    
    while secret != guess:

        try:
            guess = ask("Введите слово: ", words)
        except TypeError:
            print(f"Эх, загаданное слово: {secret}")
            break

        try_count += 1
        
        bulls, cows = bullscows(guess, secret)
        inform("Быки: {}, Коровы: {}", bulls, cows)

    print(f"Kоличество попыток: {try_count}")


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("dictionary", 
                    help="file name or URL", 
                    type=str)
    
    parser.add_argument("length", 
                    help="length of the words used (by default 5)", 
                    nargs='?', 
                    default=5, 
                    type=int)
    
    args = parser.parse_args()


    if ":" not in args.dictionary:		# дан файл 
        with open(args.dictionary) as file:
            words = file.read()
            words = words.split()
            words = [i for i in words if len(i) == args.length]
    else:								# URL
        words = urllib.request.urlopen(args.dictionary).read()
        words = words.decode().split()
        words = [i for i in words if len(i) == args.length]
    
    # print(f"$$$ {type(words)}")
    # print(words[:10], words[-10:])

    # print(f"!!! {args.dictionary} {args.length}")
    if len(words) == 0:
        raise TypeError(f"There are no words of length {args.length} in the dictionary!!!")

    gameplay(ask, inform, words)



if __name__ == "__main__":
    main()


# python -m bullscows Russian-Nouns.txt 3 
# python -m bullscows google-10000-english.txt 3 
# python -m bullscows five-letter-english.txt 5

# python -m bullscows https://raw.githubusercontent.com/Harrix/Russian-Nouns/main/dist/russian_nouns.txt 3
# python -m bullscows https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt 3
# python -m bullscows https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt 5
