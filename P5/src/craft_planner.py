import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time

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
            if any(x not in state for x in rule['Requires'].keys()):
                return False
            elif 'Consumes' in rule:
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
        next_state = None
        next_state = state
        if 'Consumes' in rule:
            for items_to_delete, num_items_to_delete in rule['Consumes'].items():
                if(items_to_delete in next_state):
                    if(next_state[items_to_delete] > num_items_to_delete):
                        next_state[items_to_delete] = next_state[items_to_delete]-num_items_to_delete
                    else:
                        next_state.pop(items_to_delete)
                else:
                    return False

        for items_to_add, num_items_to_add in rule['Produces'].items():
            if(items_to_add in next_state):
                next_state[items_to_add] = next_state[items_to_add]+num_items_to_add
            else:
                next_state[items_to_add] = num_items_to_add

        return next_state

    return effect

#this is useless since 'Produces' cant be assigned to anything
def reverse_effect(state, goal):
    print("running reverse_effect on: ")
    print(state)
    next_state = None
    next_state = state
    print("Produces is ")
    print(all_recipes(rule['Produces'])
    for items_to_delete, num_items_to_delete in rule['Produces'].items():
        if(items_to_delete in next_state):
            if(next_state[items_to_delete] > num_items_to_delete):
                next_state[items_to_delete] = next_state[items_to_delete]-num_items_to_delete
            else:
                next_state.pop(items_to_delete)
        else:
            print(items_to_delete)
            print(" is not in ")
            print(next_state)
            return False

    for items_to_add, num_items_to_add in rule['Consumes'].items():
        if(items_to_add in next_state):
            next_state[items_to_add] = next_state[items_to_add]+num_items_to_add
        else:
            next_state[items_to_add] = num_items_to_add

    print("next state is: ")
    print(state)
    return next_state



def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for items_needed, num_items_needed in goal:
            if((items_needed in state) == False):
                return False
            else:
                if(state[items_needed] < num_items_needed):
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

def costly_graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    #print ('running costly_graph on: ')
    #print (state)
    #print ("")
    list = []
    for r in all_recipes:
        if r.check(state):
            list.append((r.name, r.effect(state), r.cost))
    #print("all possible things to craft from current state: ")
    #print(list)
    return list

def heuristic(state):
    # Implement your heuristic here!
    return 0

def search(graph, state, is_goal, limit, heuristic, Goal):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    path = []
    reverse_path = []
    current_state = Goal

    #while time() - start_time < limit:
    while True:
        #next(graph(state))


        for current_items, num_current_items in current_state.items():
            if(current_items in state):
                if(num_current_items > state[current_items]):
                    current_state[current_items] = current_state[current_items] - state[current_items]
                elif(num_current_items == state[current_items]):
                    current_state.pop(current_items)

        if(current_state == {}):
            break

        previous_state = current_state
        current_state = reverse_effect(current_state)

        #item = next(graph(state))
        for next_item in costly_graph(state):
            if(next_item[1] == previous_state):
                reverse_path.append(current_state, next_item[0])
                break





        #next = (graph(state))
        #path.append(state, next[0])
        #state = next[1]

    #reversing the path
    print(reverse_path)
    while(len(reverse_path) > 0):
        path.append(reverse_path[-1])
        reverse_path.pop()

    print(path)
    return path
    pass

    # Failed to find a path
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
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 5, heuristic, Crafting['Goal'])

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
