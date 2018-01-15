import battlecode as bc
import random
import sys
import traceback

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()
orb_pat = gc.orbit_pattern()

earth_map = gc.starting_map(bc.Planet.Earth)
mars_map = gc.starting_map(bc.Planet.Mars)


count = 0

def valid_direction(id):
    val_dir_list = []
    for d in directions:
        if gc.can_move(id,d):
            val_dir_list.append(d)
    if len(val_dir_list)>0:
        val_dir = random.choice(val_dir_list)
        return val_dir
    return directions[0]

def opp_team(my_team):
    if my_team == bc.Team.Red:
        return bc.Team.Blue
    else:
        return bc.Team.Red


def preferred_valid_direction(id,location1,location2):
    diff_x = location1.x - location2.x
    diff_y = location1.y - location2.y
    priority_list = [0,1,2,3,4,5,6,7,8]
    if diff_x > 0 and diff_y > 0:
        priority_list = [3,2,4,1,5,6,0,7,8]

    if diff_x < 0 and diff_y < 0:
        priority_list = [7,6,0,1,5,2,4,3,8]

    if diff_x > 0 and diff_y < 0:
        priority_list = [1,0,2,3,7,6,4,5,8]

    if diff_x < 0 and diff_y > 0:
        priority_list = [5,4,6,3,7,0,2,1,8]

    if diff_x == 0 and diff_y > 0:
        priority_list = [4,3,5,2,6,1,7,0,8]

    if diff_x == 0 and diff_y < 0:
        priority_list = [0,1,7,2,6,3,5,4,8]

    if diff_x > 0 and diff_y == 0:
        priority_list = [2,1,3,0,4,5,7,6,8]

    if diff_x < 0 and diff_y == 0:
        priority_list = [6,7,5,4,0,3,1,2,8]

    for i in range(9):
        if gc.can_move(id,directions[priority_list[i]]):
            return directions[priority_list[i]]
    return directions[0]





while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round())
    print("Karbonite: ", gc.karbonite())
    unit_counter = {"Worker":0, "Ranger":0, "Factory":0, "Rocket":0}
    for unit in gc.my_units():
        if unit.unit_type == bc.UnitType.Worker:
            unit_counter["Worker"] +=1
        if unit.unit_type == bc.UnitType.Ranger:
            unit_counter["Ranger"] +=1
        if unit.unit_type == bc.UnitType.Factory:
            unit_counter["Factory"] +=1
        if unit.unit_type == bc.UnitType.Rocket:
            unit_counter["Rocket"] +=1

    print("Num of Rocket :", unit_counter["Rocket"])
    # frequent try/catches are a good idea
    #try:
        # walk through our units:
    for unit in gc.my_units():

        if unit.unit_type == bc.UnitType.Worker:

            #continue building
            location = unit.location
            if location.is_on_map():
                nearbyfac = gc.sense_nearby_units_by_type(location.map_location(), 2, bc.UnitType.Factory)
                nearbyroc = gc.sense_nearby_units_by_type(location.map_location(), 2, bc.UnitType.Rocket)
                for other in nearbyroc:
                    if (not other.structure_is_built()) and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        break
                for other in nearbyfac:
                    if (not other.structure_is_built()) and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        break

                #move to complete
                nearbyfac = gc.sense_nearby_units_by_type(location.map_location(), 50, bc.UnitType.Factory)
                nearbyroc = gc.sense_nearby_units_by_type(location.map_location(), 50, bc.UnitType.Rocket)
                for other in nearbyroc:
                    if not other.structure_is_built():
                        mov_dir = preferred_valid_direction(unit.id,unit.location.map_location(),other.location.map_location())
                        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, mov_dir):
                            gc.move_robot(unit.id, mov_dir)
                            break
                for other in nearbyfac:
                    if not other.structure_is_built():
                        mov_dir = preferred_valid_direction(unit.id,unit.location.map_location(),other.location.map_location())
                        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, mov_dir):
                            gc.move_robot(unit.id, mov_dir)
                            break
            # replicate-logic
            if unit_counter["Worker"] < 10:
                rep_dir = valid_direction(unit.id)
                if gc.can_replicate(unit.id,rep_dir):
                    gc.replicate(unit.id,rep_dir)
                    unit_counter["Worker"] +=1
                    continue

            #harvest
            for d in directions:
                if gc.can_harvest(unit.id,d):
                    gc.harvest(unit.id,d)
                    break

            #karbonite_low_move
            if gc.karbonite() < 100 :
                mov_dir = valid_direction(unit.id)
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id,mov_dir):
                    gc.move_robot(unit.id,mov_dir)

            #factory_blueprint
            if unit_counter["Factory"] < 3:
                d = valid_direction(unit.id)
                if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                    gc.blueprint(unit.id, bc.UnitType.Factory, d)
                    unit_counter["Factory"] += 1
                    continue

            #rocket_blueprint
            if unit_counter["Rocket"] < 3:
                d = valid_direction(unit.id)
                if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                    gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                    unit_counter["Rocket"] += 1
                    continue

            #more factories
            if gc.karbonite()>200 and unit_counter["Factory"] < 10:
                d = valid_direction(unit.id)
                if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                    gc.blueprint(unit.id, bc.UnitType.Factory, d)
                    unit_counter["Factory"] += 1
                    continue

            #random move
            d = valid_direction(unit.id)
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)


        if unit.unit_type == bc.UnitType.Factory:

            #unload soldiers
            garrison = unit.structure_garrison()
            if len(garrison) > 0:
                for d in directions:
                    if gc.can_unload(unit.id, d):
                        gc.unload(unit.id, d)
                        unit_counter["Ranger"] += 1
                        break
            elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
                gc.produce_robot(unit.id, bc.UnitType.Ranger)
                continue

        if unit.unit_type == bc.UnitType.Ranger:

            #sits in the rocket
            location = unit.location
            if location.is_on_map() and location.is_on_planet(bc.Planet.Earth):
                nearbyroc = gc.sense_nearby_units_by_type(location.map_location(), 2, bc.UnitType.Rocket)
                for other in nearbyroc:
                    if gc.can_load(other.id, unit.id):
                        print ("sits in the rocket")
                        gc.load(other.id, unit.id)
                        unit_counter["Ranger"] -= 1
                        break

                #move towards rocket
                nearbyroc = gc.sense_nearby_units_by_type(location.map_location(), 50, bc.UnitType.Rocket)
                for other in nearbyroc:
                    if other.structure_is_built():
                        mov_dir = preferred_valid_direction(unit.id,location.map_location(),other.location.map_location())
                        if gc.is_move_ready(unit.id) and gc.can_move(unit.id, mov_dir):
                            gc.move_robot(unit.id, mov_dir)
                            break

            #attack
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, opp_team(my_team))
                for other in nearby:
                    if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        gc.attack(unit.id, other.id)
                        break

            #random move
            d = valid_direction(unit.id)
            if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)

        if unit.unit_type == bc.UnitType.Rocket:

            print("Loc of Rocket :", unit.location.map_location())
            if unit.location.is_on_planet(bc.Planet.Mars):
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    for d in directions:
                        if gc.can_unload(unit.id, d):
                            gc.unload(unit.id, d)
                            break
                continue
            x = random.randint(0, mars_map.height)
            y = random.randint(0, mars_map.width)
            garrison = unit.structure_garrison()
            if len(garrison)>3:
                if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x, y)):
                    gc.launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x, y))
                    unit_counter["Rocket"] -= 1


    # except Exception as e:
    #     print('Error:', e)
    #     # use this to show where the error was
    #     traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()