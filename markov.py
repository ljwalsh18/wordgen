import string
import random
import itertools
import bisect

def readFile(path): # from 15-112 course notes (CMU)
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents): # from 15-112 course notes (CMU)
    with open(path, "wt") as f:
        f.write(contents)

def createDict(training, charDict=dict(), order=1):
    wordList = []
    training = training.replace('\n', ' ')
    training = training.replace('\t', ' ')
    exclude = set(string.punctuation + string.digits)
    for word in training.split(' '):
        word = ''.join(ch for ch in word if ch not in exclude)
        word = word.strip()
        word = word.lower()
        if len(word) < 2:
            continue
        wordList.append(word)
    for word in wordList:
        for chIndex in range(len(word)-order):
            ch = word[chIndex]
            nextChs = word[chIndex+1:chIndex+1+order]
            if ch not in charDict:
                charDict[ch] = dict()
            otherChDict = charDict[ch]
            if nextChs in otherChDict:
                otherChDict[nextChs] += 1
            else:
                otherChDict[nextChs] = 1
    writeFile('charDict.txt', str(charDict))
    return charDict

def getNextLetter(charDict, first):
    choices = list(charDict[first].keys())
    weights = list(charDict[first].values())
    cumdist = list(itertools.accumulate(weights))
    x = random.random() * cumdist[-1]
    nextLetter = choices[bisect.bisect(cumdist, x)]
    return nextLetter

def makeWord(charDict, length=7, first=None, letterList=None):
    if letterList == None:
        letterList = []
    if first == None:
        first = random.choice(list(charDict.keys()))
    if length == 0 or first[-1] not in charDict:
        return letterList
    else:
        nextLetter = getNextLetter(charDict, first[-1])
        letterList.append(nextLetter)
        return makeWord(charDict, length-1, nextLetter, letterList)

#make sure user-submitted training data is diverse enough:
def isVerified(data):
    wordList = []
    data = data.replace('\n', ' ')
    data = data.replace('\t', ' ')
    exclude = set(string.punctuation + string.digits)
    for word in data.split(' '):
        word = ''.join(ch for ch in word if ch not in exclude)
        word = word.strip()
        word = word.lower()
        if len(word) < 2:
            continue
        wordList.append(word)
    if len(wordList) < 3:
        return 'not enough words'
    for word in wordList: # make sure one word isn't super frequent
        if wordList.count(word) > len(wordList)//2:
            return 'use more unique words'
    return True

def addTraining(newData, fileName='training.txt'):
    charDict = eval(readFile('charDict.txt'))
    currentData = readFile(fileName)
    if not isVerified(newData):
        return
    writeFile(fileName, currentData + '\n' + newData)
    updatedDict = createDict(newData, charDict)
    writeFile('charDict.txt', str(updatedDict))

def start(): # clear charDict.txt before doing this
    training = readFile('training.txt')
    charDict = createDict(training)
    return refreshWord()

def refreshWord():
    global LETTERLIST
    charDict = eval(readFile('charDict.txt'))
    LETTERLIST = makeWord(charDict)
    word = ''
    for letter in LETTERLIST:
        word += letter
    print(word)
    return word

def humanInput(vote): # vote is bool
    global LETTERLIST
    charDict = eval(readFile('charDict.txt'))
    if vote: # upvote
        scalar = 1.5
    else: # downvote
        scalar = 0.75
    for i in range(len(LETTERLIST)-1):
        letter = LETTERLIST[i]
        upcoming = LETTERLIST[i+1]
        letterDict = charDict[letter]
        print(letterDict[upcoming], end=' -> ')
        letterDict[upcoming] *= scalar
        print(letterDict[upcoming])
        if letterDict[upcoming] < 0:
            letterDict[upcoming] = 0
    writeFile('charDict.txt', str(charDict))


from tkinter import *

def tkNewWord():
    word.set(refreshWord())
    return

def tkAddTraining():
    tkNewTraining = trainingText.get("1.0",END)
    print(tkNewTraining)
    trainingText.delete('1.0', END)
    if tkNewTraining != '':
        addTraining(tkNewTraining)
        print('added')
    return

def tkVote(state):
    humanInput(state)
    tkNewWord()
    return

firstWord = start()
master = Tk()
word = StringVar()
word.set(firstWord)

wordLabel = Label(master, textvariable=word, anchor=W)
wordLabel.grid(row=0, column=0, columnspan=2)

newWordButton = Button(master, text='New Word', command=tkNewWord)
newWordButton.grid(row=1, column=0, columnspan=2)

upvote = Button(master, text='I like this', command=lambda: tkVote(True))
upvote.grid(row=2, column=0)
dnvote = Button(master, text='I hate this', command=lambda: tkVote(False))
dnvote.grid(row=2, column=1)

trainingText = Text(master, height=10)
trainingText.grid(row=3, column=0, columnspan=2)

trainingEnter = Button(master, text='Sumbit Training Data', command=tkAddTraining)
trainingEnter.grid(row=4, column=0, columnspan=2)

mainloop()
