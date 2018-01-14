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

count = 0
poocount = 0

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round())

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        for unit in gc.my_units():
            print(poocount)

            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('produced a knight!')
                    continue

            x = random.randint(1, 10)
            y = random.randint(1, 10)

            if unit.unit_type == bc.UnitType.Rocket and gc.can_launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x, y)):
                garrison = unit.structure_garrison()
                if len(garrison) > 0 :
                    print("yoooooooooooooooooooooooooo")
                    gc.launch_rocket(unit.id, bc.MapLocation(bc.Planet.Mars, x, y))
            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    print(unit.unit_type, "  ", other.unit_type)
                    if other.unit_type == bc.UnitType.Rocket and unit.unit_type == bc.UnitType.Worker and gc.can_load(other.id, unit.id):
                        print("feaf")
                        gc.load(other.id, unit.id)
                        break
                    if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                        print("pooooo")
                        poocount = poocount + 1
                        gc.build(unit.id, other.id)
                        # move onto the next unit
                        break
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        break

            # okay, there weren't any dudes around
            # pick a random direction:
            d = random.choice(directions)

            # or, try to build a factory:
            if count<1 and gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                count = count + 1
            # and if that fails, try to move
            # elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
            #     gc.move_robot(unit.id, d)

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