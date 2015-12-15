-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
--Drops DB to clean up previous instances
DROP DATABASE IF EXISTS tournament; 
--Creates the DB
CREATE DATABASE tournament; 
--Connects to DB so tables are created within the DB
\c tournament 
-- Makes the player table
CREATE TABLE player( 
	id serial PRIMARY KEY,
	name varchar(50)
	);
-- Makes the match table, if implementing multiple tournaments, must add tournament_id	
CREATE TABLE match( 
	id serial PRIMARY KEY,
	winner_id int,
	loser_id int 
	);
--- View to tally up wins per player
CREATE VIEW winner AS 
SELECT winner_id, COUNT(*) AS wins
FROM match 
GROUP BY winner_id
ORDER BY wins;
--- View to tally up losses per player
CREATE VIEW loser AS 
SELECT loser_id, COUNT(*) AS losses
FROM match
GROUP BY loser_id;
---Joins the winner & loser views with the players table to get standings
---This one got a little messy since it was reporting nulls and not 0's. Is there a better way to make 0 default instead of null?  I know I can do it for columns.  Suppose I might be able to make it default for COUNT(*) columns?
---would love to know if there's a simpler way to do this.  this project feels pretty hacked together. 
CREATE VIEW standings AS
SELECT player.id, player.name,
CASE WHEN (winner.wins ISNULL) THEN 0 ELSE winner.wins END AS totalwins, 
CASE WHEN (loser.losses ISNULL) AND (winner.wins ISNULL) THEN 0 ELSE 
	CASE WHEN loser.losses ISNULL THEN winner.wins
		 WHEN winner.wins ISNULL THEN loser.losses
		 ELSE winner.wins+loser.losses
		 END
	END AS totalmatches
FROM player
LEFT JOIN loser
ON player.id=loser.loser_id
LEFT JOIN winner
ON player.id=winner.winner_id
ORDER BY totalwins DESC;

-- Makes a table to assign id's to specific tournaments
---CREATE TABLE tournaments( 
	---id serial PRIMARY KEY,
	---tournament_name varchar(50),
	---tournament_date date
---);
