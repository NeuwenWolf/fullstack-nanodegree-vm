#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
db = psycopg2.connect("dbname=tournament")
c = db.cursor()
def connect():
    """ to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament;") 
    """Already done"""


def deleteMatches():
    """Remove all the match records from the database."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("DELETE FROM match;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("DELETE FROM player;")
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("SELECT COUNT(*) FROM player;")
    results=c.fetchone()
   
    return results[0]
    db.close()
    


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("INSERT INTO player (name) VALUES(%s);", (name,))
    
    db.commit()
    db.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    """Returns a list of tuples with id name and wins"""
    c.execute("SELECT * FROM standings;")
    Results=c.fetchall()
    return Results
    db.close()

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("INSERT INTO match (winner_id, loser_id) VALUES(%s,%s);", (winner,loser))
    db.commit()
    db.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    db = psycopg2.connect("dbname=tournament")
    c = db.cursor()
    c.execute("SELECT * FROM standings;")
    """standings returns a list of tuples with id, name, wins, totalmatches.
    Need to extract just name and wins and concatenate them together into a list of tuples"""
    data = c.fetchall()
    """gets the length of the list so I can iterate over it """
    length=len(data)
    i=0
    Result=[]
    """This loop grabs the appropriate element of the list,
    and then grabs the first two elements of that tuple and splices them together in a new list.
    this new list then gets returned"""
    while i<length:
        a=data[i][0:2]
        i+= 1
        b=data[i][0:2]
        i+= 1
        Result.append(a+b)
    return Result  
    db.close()


