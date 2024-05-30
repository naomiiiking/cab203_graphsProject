import graphs
import digraphs
import csv

def gamesOK(games):
   # Create a set of verticies (player names by creating a union of each player in each game reuslting in all unqiue names)
   playerNames = {player for game in games for player in game}
   
   # Check if games set is semmetrical and undirected 
   if all( (v, u) in games for (u,v) in games) == False:
      # Create a new set of reversed tuples for every tuple (game) in the games set if it does not already exists
      symmetricPairs = {(b, a) for (a, b) in games}
      # Add the symmetric pairs to test games with an update to avoid duplicates
      games.update(symmetricPairs)
   
   # Create a list of all the neigbourhoods (players versing eachother) 
   neighbourhoods = [graphs.N(playerNames, games, player) for player in playerNames]
   # Union to get a set of unique neighbourhoods -> distinct players
   uniqueNeighbourhoods = set().union(*neighbourhoods)
   # Check that all the distinct pairs in uniqueNeighbourhoods verse eachother or two others in games set
   distinctPairsCheck = {(u, v) in uniqueNeighbourhoods for (u, v) in games}

   # Create a dictionary of the players and their games (degrees)
   gamesPlayed = {player: graphs.degree(playerNames, games, player) for player in playerNames}
   # Check that all players have played the same amount of games (have the same amount of degrees)
   allSameGamesPlayed = len(set(gamesPlayed.values())) == 1

   # Return the and of both conditions
   return allSameGamesPlayed and distinctPairsCheck

def referees(games, refereecsvfilename):
   conflicts = {}

   # Read referee conflicts from CSV file
   with open(refereecsvfilename, 'r') as file:
      reader = csv.DictReader(file)
      conflicts = {row['Referee']: set(row.values()) - {row['Referee']} for row in reader}
   
   # Create bipartion between games and referees with games and referees as vertices and edges as all legal pairings ->
   # all pairings where the refeeree is not in conflict
   nonConflictingMatches = {(game, referee) for game in games for referee in conflicts if not (set(game) & conflicts[referee])}

   # Use maxMatching to assign each refeeree to one game
   # Use digraphs.maxMatching with a set of the games (A) and a set of the referee names (B) as the veritices and nonConflictingMatches (E) as edges
   # Creates asymmetrical duplicates? unsure why
   maxMatchingMatches = digraphs.maxMatching(set(games), set(conflicts.keys()), nonConflictingMatches)

   # Filter out asymmetrical duplicates by only including (u,v) if u (game) is an instance of a tuple -> excludes asymmetric pair (v,u)
   filteredMatches = {(game, referee) for game, referee in maxMatchingMatches if isinstance(game, tuple)}

   # Create a dictionary of the games as keys and the assigned referee as the value
   refereeMapping = {game: referee for game, referee in filteredMatches}

   # Check if all games are assigned a referee so that the length refereeMapping is the same as the length of scheduled games
   if len(refereeMapping) != len(games):
      return None  
   else:
      return refereeMapping     

def gameGroups(assignedReferees):
   V = {name for game in assignedReferees for name in game}
   colorClasses = graphs.colourClassesFromColouring(assignedReferees)

   E = {game for s in colorClasses for game in s}
   # Check if games set is semmetrical and undirected 
   if all( (v, u) in E for (u,v) in E) == False:
      symmetricPairs = {(b, a) for (a, b) in E}
      # Add the symmetric pairs to test games with an update to avoid duplicates
      E.update(symmetricPairs)

   # Minimus colours requird is the number of schedules requeqired
   minColoring = graphs.minColouring(V,E)

   group = []

   # For each schedule, remove a pair from the colour classes and check if there is another pair froma different colour class with two different players
   # for i in minColoring[0]:
      # checkingPair = colorClasses.pop()
      # scheduledPair = {}
      # if (for game in colorClasses if any((p1,p2) != (p3,p4))):
         # matchedPair = tuple(for game in colorClasses if any((p1,p2) != (p3,p4)))
         # scheduledPair.append(checkingPair, scheduledPair)
      # group.append(scheduledPair)
   # simultaneous_games = games where p1 or p2 1= p3 or p4 and (p1,p2) not in color class of (p3,p4)
   return group

   
      
def gameSchedule(assigned_referees, gameGroups):
   # Graph which connects all the games where there are overlaps in players and refs
      # Verticies V will be a set of the tuples of the players and refs for each game
      # Operator * unpacks the players from the key tuple and assigned_referees.items() gets the refs
   V = {(*pair, ref) for (pair, ref) in assigned_referees.items()}
   print(V)
      # Edges E draws edges between verticies V if there is an intersection (overlapping ref) between two verticies
   E = {(V1, V2) for V1 in V for V2 in V if V1 != V2 and set(V1) & set(V2)}
   # graphs.minColouring to return the minimum chromatic number for the previously created graph, if it is not equal 
   # to the length of gameGroups, not possible to schedule so return Nonew
   k, c = graphs.minColouring(V, E)
   if(len(assigned_referees) > k):
      return None
   
   # Fill the schedule list with the game groups in order of how they should be played (refs should play their game before refeering another game)
   else:
      # Create a list of the highest possible schedule index for each game in game groups
      # Index position should be determined by how 
      scheduleIndices = [
         max(
            (index for index, scheduledGame in enumerate(gameGroups) if any(referee in scheduledGame for referee in game)),
            default=-1
         ) + 1
         for game in gameGroups
      ]
      return [gameGroups[i] for i in sorted(range(len(gameGroups)), key=lambda x: scheduleIndices[x])]


games = {
         ('Edward', 'Vicious'),
         ('Faye Valentine', 'Ein'),
         ('Faye Valentine', 'Vicious'),
         ('Jet Black', 'Edward'),
         ('Jet Black', 'Ein'),
         ('Jet Black', 'Vicious'),
         ('Spike Spiegel', 'Edward'),
         ('Spike Spiegel', 'Ein'),
         ('Spike Spiegel', 'Faye Valentine')
      }

def scores(p, s, c, games):
   unique_names = {name for pair in games for name in pair}

   def get_points(current_name): #For alice
      # Set of verticies where each vertice is the name of the player that player current_name defeated
      vPrimaryWins = {loser for winner, loser in games if winner == current_name}
     
      # Sset of verticies where each verticie is the name of the player that each player in vPrimaryWins defeated
      vSecondaryWins = {loser for winner in vPrimaryWins for winner2, loser in games if winner2 == winner}

      # Set of edges connecting each player in vPrimaryWins to the player they defeated in vSecondaryWins
      E = {(winner, loser) for winner in vPrimaryWins for loser in vSecondaryWins if (winner, loser) in games}

      # Check if games set is semmetrical and undirected 
      if all( (v, u) in E for (u,v) in E) == False:
         symmetricPairs = {(b, a) for (a, b) in E}
         # Add the symmetric pairs to test games with an update to avoid duplicates
         E.update(symmetricPairs)

      if graphs.bipartition(vPrimaryWins, E) == None:
         return  0
      else: 
         # Dictionary with, for every name in vPrimaryWins, adds the name of the player defeated and how many primary tokens p they are worth
         primaryPointsAssignment = {vPrimaryWins_name: p for vPrimaryWins_name in vPrimaryWins}
      
         # Dictionary with, for every name in vsecondayWins, adds the name of the player defeated and how many primary tokens s they are worth
         secondaryPointsAssignment = {vSecondaryWins_name: s for vSecondaryWins_name in vSecondaryWins}

         # Find common edges which can be used to move tokens for each player which can be updated in pimrary and secondary wins
         commonEdges = {(winner, loser) for winner in primaryPointsAssignment for loser in secondaryPointsAssignment if (winner, loser) in E}

         # Move tokens from the secondary winner to the primary winner across common edges until each primary token has reached the limit c
         for edge in commonEdges:
            winner, loser = edge
            if primaryPointsAssignment[winner] < c:
               primaryPointsAssignment[winner] += 1
               secondaryPointsAssignment[loser] -= 1
            else:
               continue

      return sum(primaryPointsAssignment.values())      

   return {name: get_points(name) for name in unique_names}

print(scores(4, 2, 8, games))