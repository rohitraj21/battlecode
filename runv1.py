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


while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round())
    unit_counter = {}
    for unit in gc.my_units():
        if unit.unit_type == bc.UnitType.Worker:
            unit_counter["Worker"] +=1
        if unit.unit_type == bc.UnitType.Ranger:
            unit_counter["Ranger"] +=1
        if unit.unit_type == bc.UnitType.Factory:
            unit_counter["Factory"] +=1
        if unit.unit_type == bc.UnitType.Rocket:
            unit_counter["Rocket"] +=1

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():

            if unit.unit_type == bc.UnitType.Worker:

                #continue building
                location = unit.location
                if location.is_on_map():
                    nearbyfac = gc.sense_nearby_units_by_type(location.map_location(), 2, bc.UnitType.Factory)
                    nearbyroc = gc.sense_nearby_units_by_type(location.map_location(), 2, bc.UnitType.Rocket)
                    for other in nearbyroc:
                        if gc.can_build(unit.id, other.id):
                            gc.build(unit.id, other.id)
                            break
                    for other in nearbyfac:
                        if gc.can_build(unit.id, other.id):
                            gc.build(unit.id, other.id)
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
                        gc.move(unit.id,mov_dir)

                #factory_blueprint
                if unit_counter["Factory"] < 3:
                    d = valid_direction(unit.id)
                    if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                        gc.blueprint(unit.id, bc.UnitType.Factory, d)
                        unit_counter["Factory"] += 1
                        continue

                #rocket_blueprint
                if unit_counter["Rocket"] < 1:
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
                            gc.load(other.id, unit.id)
                            unit_counter["Ranger"] -= 1
                            break
                    d = valid_direction(unit.id)

                #attack
                location = unit.location
                if location.is_on_map():
                    nearby = gc.sense_nearby_units_by_team(location.map_location(), 50, 1 - my_team)
                    for other in nearby:
                        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                            gc.attack(unit.id, other.id)
                            break

                #random move
                d = valid_direction(unit.id)
                if gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                    gc.move_robot(unit.id, d)

            if unit.unit_type == bc.UnitType.Rocket:

                if unit.location.is_on_planet(bc.Planet.Mars):
                    garrison = unit.structure_garrison()
                    if len(garrison) > 0:
                        for d in directions:
                            if gc.can_unload(unit.id, d):
                                gc.unload(unit.id, d)
                                break
                    continue
                x = random.randint(0, mars.height)
                y = random.randint(0, mars.width)
                garrison = unit.structure_garrison()
                    if len(garrison)>3 and orb_pat.duration(gc.round()) < 100:
                        if gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x, y)):
                            gc.launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x, y))
                            unit_counter["Rocket"] -= 1


    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
