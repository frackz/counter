import os.path, sys, requests
from threading import Thread
from time import sleep
from json import load

user = '' # Your user id, this will get your mee6 xp and level
guild = '' # The guild of operations
channel = '' # The channel of operations
timeout = 15 # How much slowmode is there (if any? i would still recommond some)
notu_timeout = 3 # How much it will add to the timeout if the latest message isn't from you
typing_timeout = 8 # How much timeout for every type request
mee6_limit = 200 # The limit of users it will find (if big server then more)
default_headers = {
    "Authorization": "yo token"
} # Headers / token to your account

messages_url = f'https://discord.com/api/v8/channels/{channel}/messages'
typing_url = f'https://discord.com/api/v9/channels/{channel}/typing'
mee6_url = f'https://mee6.xyz/api/plugins/levels/leaderboard/742017923794731028?limit={mee6_limit}'

levels = load(open('levels.json'))

def sendMessage(message):
    return requests.post(messages_url, headers = default_headers, data = { "content": message })

def getLatestMessage():
    request = requests.get(messages_url, headers = default_headers)
    if request.status_code == 200:
        messages = request.json()
        message = messages[0]
        author = message["author"]["id"]
        if author != user:
            sleep(notu_timeout) 
        return messages[0]["content"]
    return False

def getLeaderboard():
    request = requests.get(mee6_url)
    if request.status_code == 200:
        latest = False

        leaderboard = request.json()["players"]
        amount = 0
        for x in leaderboard:
            amount += 1
            if x["id"] == user:
                x["rank"] = amount
                return x, latest["xp"] - x['xp']
            latest = x

def calculateNeededXP(level, xp):
    nextLevel = str(level + 1)
    return levels[nextLevel], levels[nextLevel] - xp

def typing():
    requests.post(typing_url, headers=default_headers)

    sleep(typing_timeout)
    return typing()

def start():
    Thread(target=typing, daemon=True).start()

    while True:
        latestMessage = getLatestMessage()
        if latestMessage == False:
            return print("Failed to get latest message")
            
        latest = int(latestMessage) + 1 # Calculate the latest message plus 1
        newMessage = sendMessage(str(latest)) # Send the message
        leaderboard, nextUser = getLeaderboard() # Get user on the leaderboard, and the person next to the user

        level = leaderboard["level"]
        xp = leaderboard["xp"]
        rank = leaderboard["rank"]

        newRank, neededRank = calculateNeededXP(level, xp) # Calculate needed xp for new rank

        print("Sent {} and recieved {}, xp, level & rank {}/{} - {} (level: {} & rank: {}), and user {}xp".format(
            str(latest),
            str(newMessage.status_code),
            str(xp),
            str(newRank),
            str(neededRank),
            str(level),
            str(rank),
            str(nextUser)
        ))

        sleep(timeout)

if __name__ == '__main__':
    start()