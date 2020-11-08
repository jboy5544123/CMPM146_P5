import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush
from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.
    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Requires' in rule:
            for x in rule['Requires']:
                if x not in state.keys() or state[x] < 1:
                    return False
        if 'Consumes' in rule:
            if any(x not in state or state[x] < rule['Consumes'][x] for x in rule['Consumes']):
                return False
        return True
    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        Produced = rule['Produces']
        for item_produced in Produced:
            next_state[item_produced] += Produced[item_produced]
        if 'Consumes' in rule:
            Consumed = rule['Consumes']
            for item_consumed in Consumed:
                next_state[item_consumed] -= Consumed[item_consumed]
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for item in goal:
            if item not in state or goal[item] > state[item]:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state, time, goal):
    # Implement your heuristic here!
    if is_goal(state):
        return 0
    #if we already have a tool dont remake the tool
    elif state['bench'] > 1 or state['furnace'] > 1 or state['cart'] > 1:
        return inf
    elif state['wooden_pickaxe'] > 1 or state['stone_pickaxe'] > 1 or state['iron_pickaxe'] > 1:
        return inf
    elif state['stone_axe'] > 1 or state['wooden_axe'] > 1 or state['iron_axe'] > 1:
        return inf
    elif state['stick'] > 4 or state['plank'] > 4 or state['wood'] > 1 or state['cobble'] > 8:
        return 1000
    elif state['coal'] > 9 or state['ore'] > 9:
        return 1000
    return time


def search(graph, state, is_goal, limit, heuristic, goal):
    start_time = time()
    next_state = state
    cost = 0
    actions = [(state.copy(), None)]
    if is_goal(next_state):
        return actions, cost

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    while time() - start_time < limit:
        states_to_search = []
        for new_state in graph(next_state.copy()):
            heu = heuristic(new_state[1], new_state[2], goal)
            heappush(states_to_search,(heu, (new_state[0], new_state[1].copy(), new_state[2])))
            checker_state = next_state.copy()
        test = heappop(states_to_search)[1]
        next_state = test[1].copy()
        test_tuple = (test[1].copy(), test[0])
        cost += test[2]
        actions.append(test_tuple)
        if is_goal(next_state):
            return actions, cost
        pass

    # Failed to find a path
    print("here")
    print(next_state)
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    goal = Crafting['Goal']
    is_goal = make_goal_checker(goal)

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan, cost = search(graph, state, is_goal, 5, heuristic, goal)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print(action)
            print('\t',state)
        print(cost)
        print(len(resulting_plan) - 1)
