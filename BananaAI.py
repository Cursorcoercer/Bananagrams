
class AIBoard:

    def __init__(self, dictionary):
        self.dictionary = dictionary
        self.lets = []
        self.pending = []  # Stores letters that are in lets, but not in grid.
        self.grid = []
        self.blank = ' '
        self.wordIndex = []  # Stores (word, start, verticality, dependecy).
        self.center = (0, 0)

    def extend(self, array, amount):
        # This will extend or reduce an array in place.
        # Amount is how much to extend or reduce, it should be a tuple
        # with integers indicating (top, bottom, left, right).
        # A positive amount extends, negative reduces.
        for f in range(amount[0]):
            array.insert(0, list(len(array[0]) * self.blank))
        for f in range(amount[1]):
            array.append(list(len(array[0]) * self.blank))
        for f in range(amount[2]):
            for g in array:
                g.insert(0, self.blank)
        for f in range(amount[3]):
            for g in array:
                g.append(self.blank)
        for f in range(-amount[0]):
            del array[0]
        for f in range(-amount[1]):
            del array[-1]
        for f in range(-amount[2]):
            for g in array:
                del g[0]
        for f in range(-amount[3]):
            for g in array:
                del g[-1]

    def crop(self, tocrop):
        # eliminate surrounding whitespace on self.grid
        # tocrop is amount expected to be cropped
        # tocrop should be a tuple (top, bottom, left, right)
        # accounting for tocrop, wordIndex will be updated accordingly
        cropped = [0, 0, 0, 0]
        while all(f == self.blank for f in self.grid[0]):
            cropped[0] += 1
            del self.grid[0]
        while all(f == self.blank for f in self.grid[-1]):
            cropped[1] += 1
            del self.grid[-1]
        while all(f[0] == self.blank for f in self.grid):
            cropped[2] += 1
            for g in self.grid:
                del g[0]
        while all(f[-1] == self.blank for f in self.grid):
            cropped[3] += 1
            for g in self.grid:
                del g[-1]
        if cropped[0] != tocrop or cropped[2] != tocrop:
            for h in self.wordIndex:
                h[1] = (h[1][0] + tocrop - cropped[2], h[1][1] + tocrop - cropped[0])
        return cropped

    def check(self, array, word, coords, vertical):
        # This returns True if word can be legally set where it is.
        # The coords are of the word's start, isvertical needs to be 0 or 1.
        for f in range(max(len(word) * vertical, 1)):
            line = ''.join(array[coords[1] + f])
            string = line.split(self.blank)[line[:coords[0]].count(self.blank)]
            if len(string) > 1 and string not in self.dictionary:
                return False
        for f in range(max(len(word) * (1 - vertical), 1)):
            line = ''.join(array[g][coords[0] + f] for g in range(len(array)))
            string = line.split(self.blank)[line[:coords[1]].count(self.blank)]
            if len(string) > 1 and string not in self.dictionary:
                return False
        return True

    def find(self, words, letters, lettersdown, mustuse):
        # This finds all words in words whose letters are contained in letters,
        # allowing for one extra letter, as that letter may be on the board,
        # these extra letters are kept track of in the list mustuse.
        valid = []
        for f in words:
            if len(f) > len(letters) + 1:
                continue
            temp = list(letters)
            extra = ''
            for g in f:
                try:
                    temp.remove(g)
                except ValueError:
                    if not extra and g in lettersdown:
                        extra = g
                    else:
                        break
            else:
                valid.append(f)
                mustuse.append(extra)
        return valid

    def wordsort(self, word):
        # This is the specialty sorting method for words.
        # The speed of the entire program rests heavily on this.
        freq = 'zjqxkwvfybhmpgudclotnrasie'
        tier = 4 * [7] + 4 * [4] + 4 * [3] + 5 * [2] + 9 * [1]
        return (-sum(tier[freq.index(f)] for f in word), -len(word))

    def lift(self, array, windex):
        # This lifts the word described by windex out of array.
        if len(windex[0]) == 1:
            array[windex[1][1]][windex[1][0]] = self.blank
        elif windex[2] == 0:
            for f in range(len(windex[0])):
                if f != windex[3]:
                    array[windex[1][1]][windex[1][0] + f] = self.blank
        elif windex[2] == 1:
            for f in range(len(windex[0])):
                if f != windex[3]:
                    array[windex[1][1] + f][windex[1][0]] = self.blank

    def makegrid(self, words, grd, letters, used, windex):
        # A recursive function for creating word grids.
        # The function places a valid word in the grid and then calls itself.
        if not letters:
            # All letters have been placed the grid has been successfully made.
            self.wordIndex = windex
            self.grid = grd
            return True
        mustuse = []
        foundwords = self.find(words, letters, used, mustuse)  # remains sorted
        for f in foundwords:
            if (not set(letters).issubset(
                    set(''.join(foundwords[foundwords.index(f):])))):
                # A quick check to make sure that the words remaining in
                # foundwords contain the right letters to complete the grid.
                return False
            if not used:
                newgrid = [list(f)]
                newletters = list(letters)
                for g in f:
                    newletters.remove(g)
                newused = list(f)
                newwindex = [[f, (0, 0), 0, None]]
                if self.makegrid(foundwords, newgrid, newletters, newused, newwindex):
                    return True
            else:
                m = mustuse[foundwords.index(f)]
                for g in range(len(f)):
                    if f[g] not in used or (m and f[g] != m):
                        continue
                    spots = []
                    # Now it finds all coords of letters on the grid that are
                    # the same as f[g].
                    for y in range(len(grd)):
                        spots += [(x, y) for x in range(len(grd[y])) if grd[y][x] == f[g]]
                    for h in spots:
                        # Here it attempts to place the word at spot h.
                        newgrid = [list(i) for i in grd]
                        self.extend(newgrid, (1, 1, 1, 1))
                        if self.blank == newgrid[h[1] + 1][h[0] + 2] == newgrid[h[1] + 1][h[0]]:
                            vr = 0
                            hr = 1
                        elif self.blank == newgrid[h[1] + 2][h[0] + 1] == newgrid[h[1]][h[0] + 1]:
                            vr = 1
                            hr = 0
                        else:
                            continue
                        stickout = max(g - h[vr], 0)  # The amount that word sticks out into up/left grid extension
                        if vr:
                            toextend = (stickout - 1, max(len(f) - g - len(newgrid) + 2 + h[1], 0) - 1, -1, -1)
                        else:
                            toextend = (-1, -1, stickout - 1, max(len(f) - g - len(newgrid[0]) + 2 + h[0], 0) - 1)
                        self.extend(newgrid, toextend)
                        coords = (
                            h[0] + hr * (stickout - g), h[1] + vr * (stickout - g))  # The coords of word start (x, y)
                        # Now we place word on the newgrid, or go onto the next spot if it doesn't fit
                        for p in range(len(f)):
                            if newgrid[coords[1] + vr * p][coords[0] + hr * p] == self.blank or p == g:
                                newgrid[coords[1] + vr * p][coords[0] + hr * p] = f[p]
                            else:
                                break
                        else:
                            if self.check(newgrid, f, coords, vr):
                                newletters = list(letters)
                                newused = list(used)
                                for i in range(len(f)):
                                    if i != g:
                                        newletters.remove(f[i])
                                        newused.append(f[i])
                                newwindex = [list(i) for i in windex] + [
                                    [f, (h[0] - (hr * g), h[1] - (vr * g)), vr, g]]
                                for ch in newwindex:
                                    ch[1] = (ch[1][0] + hr * stickout, ch[1][1] + vr * stickout)
                                if self.makegrid(foundwords, newgrid, newletters, newused, newwindex):
                                    return True
        return False  # This will back us down one recursion.

    def add(self, new):
        # This handles adding letter(s) to self.grid.
        if not self.lets:
            print('You must make a grid before you can add to it')
            return False
        self.lets = self.lets + list(new)
        if not self.grid:
            if self.makegrid(self.dictionary, [], list(self.lets), [], []):
                return True
            else:
                print('Again, no solutions were found')
                return False
        toadd = list(new) + list(self.pending)
        if len(toadd) == 1:
            if self.singleadd(toadd[0]):
                return True
        if self.multipleadd(toadd):
            return True
        else:
            self.pending = toadd
            print('Could not add letter(s)')
            return False

    def singleadd(self, new):
        # This attempts to quickly add a single letter by checking all open
        # spots on the board.
        grd = [list(i) for i in self.grid]
        self.extend(grd, (2, 2, 2, 2))
        for f in range(1, len(grd) - 1):
            for g in range(1, len(grd[f]) - 1):
                if grd[f][g] == self.blank and any((grd[f + h[0]][g + h[1]] != self.blank) for
                                                   h in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    grd[f][g] = new
                    if self.check(grd, new, (g, f), 0):
                        self.grid = grd
                        am = self.crop(2)
                        self.wordIndex.append([new, (g - am[2], f - am[0]),
                                               None, None])
                        return True
                    else:
                        grd[f][g] = self.blank

    def multipleadd(self, new):
        # This adds multiple letters by using the makegrid() function, then
        # remove a word and try again until it works.
        grd = [list(i) for i in self.grid]
        usd = list(self.lets)
        for f in new:
            usd.remove(f)
        lts = list(new)
        for f in range(len(self.wordIndex)):
            w = self.wordIndex[-f - 1]
            self.lift(grd, w)
            for g in range(len(w[0])):
                if g != w[3]:
                    usd.remove(w[0][g])
                    lts.append(w[0][g])
            if self.makegrid(self.dictionary, grd, lts, usd, self.wordIndex[:-f - 1]):
                self.crop(0)
                return True
        return False

    def display(self):
        # This prints the board out.
        print()
        for f in self.grid:
            print(''.join(f))
        print()
