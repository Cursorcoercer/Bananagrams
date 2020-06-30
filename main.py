from BananaAI import AIBoard

# We start by opening and formatting the scrabble dictionary file.
file = open("scrabble_dictionary.txt")
allwords = file.read().split('\n')
file.close()
allwords = [f.lower() for f in allwords]
easymode = True
if easymode:
    # Filter down word list to common words
    file = open("words_by_commonality.txt")
    laymans = set(file.read().split('\n')[:])  # 80,000 words
    file.close()
    allwords = list(set(allwords) & laymans)
##allwords = [f for f in allwords if len(f) >= 3]  # Optional minimum word length restriction
alphabet = "abcdefghijklmnopqrstuvwxyz"


def main():
    # main method for using the AI as a utility
    split = AIBoard(allwords)
    inp = input('Enter your bananagram letters:\n')
    split.lets = [f.lower() for f in inp if f.lower() in alphabet]
    allwords.sort(key=split.wordsort)
    if split.makegrid(allwords, [], list(split.lets), [], []):
        split.display()
    else:
        print('No solutions were found')
    while 1:
        inp = input('Enter letters to be added to board:\n')
        inp = ''.join(f.lower() for f in inp if f.lower() in alphabet)
        if not inp:
            continue
        if split.add(inp):
            split.display()


def solo():
    # have the AI play through all the tiles in the bag by itself
    import random
    tiles = {'a': 13, 'b': 3, 'c': 3, 'd': 6, 'e': 18, 'f': 3, 'g': 4, 'h': 3,
             'i': 12, 'j': 2, 'k': 2, 'l': 5, 'm': 3, 'n': 8, 'o': 11, 'p': 3, 'q': 2,
             'r': 9, 's': 6, 't': 9, 'u': 6, 'v': 3, 'w': 3, 'x': 2, 'y': 3, 'z': 2}
    bag = []
    for f in tiles:
        bag += list(tiles[f] * f)
    split = AIBoard(allwords)
    random.shuffle(bag)
    allwords.sort(key=split.wordsort)
    draw = 21
    split.lets = bag[:draw]
    if split.makegrid(allwords, [], list(split.lets), [], []):
        split.display()
    else:
        print('Failed')
        return None
    for f in range(len(bag[draw:])):
        if split.add(bag[draw:][f]):
            split.display()
            print(f + draw + 1)
        else:
            print('Failed')
            return None
    print('\nFinished')


if __name__ == '__main__':
    solo()
