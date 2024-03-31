from utils.utils import ContainerSet, DisjointSet


class NFA:
    def __init__(self, states, finals, transitions, start=0):
        self.states = states
        self.start = start
        self.finals = set(finals)
        self.map = transitions
        self.vocabulary = set()
        self.transitions = {state: {} for state in range(states)}

        for (origin, symbol), destinations in transitions.items():
            assert hasattr(destinations, '__iter__'), 'Invalid collection of states'
            self.transitions[origin][symbol] = destinations
            self.vocabulary.add(symbol)

        self.vocabulary.discard('')

    def epsilon_transitions(self, state):
        assert state in self.transitions, 'Invalid state'
        try:
            return self.transitions[state]['']
        except KeyError:
            return ()


class DFA(NFA):

    def __init__(self, states, finals, transitions, start=0):
        assert all(isinstance(value, int) for value in transitions.values())
        assert all(len(symbol) > 0 for origin, symbol in transitions)

        transitions = {key: [value] for key, value in transitions.items()}
        NFA.__init__(self, states, finals, transitions, start)
        self.current = start

    def _move(self, symbol):
        target = self.transitions[self.current].get(symbol, None)
        if not target:
            return False
        self.current = target[0]
        return True

    def _reset(self):
        self.current = self.start

    def recognize(self, string):
        self._reset()
        for c in string:
            if not self._move(c):
                return False
        return self.current in self.finals


def move(automaton: NFA, states, symbol):
    moves = set()
    for state in states:
        targets = automaton.transitions[state].get(symbol, None)
        if not targets:
            continue
        for t in targets:
            moves.add(t)
    return moves


def epsilon_closure(automaton: NFA, states):
    pending = list(states)
    closure = set(states)

    while pending:
        state = pending.pop()
        e_targets = automaton.epsilon_transitions(state)
        for t in e_targets:
            if t not in closure:
                closure.add(t)
                pending.append(t)

    return ContainerSet(*closure)


def nfa_to_dfa(automaton: NFA):
    transitions = {}

    start = epsilon_closure(automaton, [automaton.start])
    start.id = 0
    start.is_final = any(s in automaton.finals for s in start)
    states = [start]

    pending = [start]
    while pending:
        state = pending.pop()

        for symbol in automaton.vocabulary:
            targets = epsilon_closure(automaton, move(automaton, state, symbol))

            if not targets:
                continue

            try:
                index = states.index(targets)
                targets = states[index]
            except ValueError:
                targets.id = len(states)
                targets.is_final = any(t in automaton.finals for t in targets)
                pending.append(targets)
                states.append(targets)

            transitions[state.id, symbol] = targets.id

    finals = [state.id for state in states if state.is_final]

    dfa = DFA(len(states), finals, transitions)
    return dfa


def automata_union(a1, a2):
    transitions = {}

    start = 0
    d1 = 1
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        transitions[d1 + origin, symbol] = [d + d1 for d in destinations]

    for (origin, symbol), destinations in a2.map.items():
        transitions[d2 + origin, symbol] = [d + d2 for d in destinations]

    transitions[0, ''] = [d1 + a1.start, d2 + a2.start]

    for f in a1.finals:
        try:
            transitions[f + d1, ''].append(final)
        except KeyError:
            transitions[f + d1, ''] = [final]

    for f in a2.finals:
        try:
            transitions[f + d2, ''].append(final)
        except KeyError:
            transitions[f + d2, ''] = [final]

    states = a1.states + a2.states + 2
    finals = {final}

    return NFA(states, finals, transitions, start)


def automata_concatenation(a1, a2):
    transitions = {}

    start = a1.start
    d1 = 0
    d2 = a1.states + d1
    final = a2.states + d2

    for (origin, symbol), destinations in a1.map.items():
        transitions[d1 + origin, symbol] = [d + d1 for d in destinations]

    for (origin, symbol), destinations in a2.map.items():
        transitions[d2 + origin, symbol] = [d + d2 for d in destinations]

    for f in a1.finals:
        try:
            transitions[f + d1, ''].append(d2 + a2.start)
        except KeyError:
            transitions[f + d1, ''] = [d2 + a2.start]

    for f in a2.finals:
        try:
            transitions[f + d2, ''].append(final)
        except KeyError:
            transitions[f + d2, ''] = [final]

    states = a1.states + a2.states + 1
    finals = {final}

    return NFA(states, finals, transitions, start)


def automata_closure(a1):
    transitions = {}

    start = 0
    d1 = 1

    for (origin, symbol), destinations in a1.map.items():
        transitions[d1 + origin, symbol] = [d + d1 for d in destinations]

    transitions[start, ''] = [d1 + a1.start]

    for f in a1.finals:
        try:
            transitions[f + d1, ''].append(start)
        except KeyError:
            transitions[f + d1, ''] = [start]

    states = a1.states + 1
    finals = {start}

    return NFA(states, finals, transitions, start)


def automata_positive_closure(a1):
    return automata_concatenation(a1, automata_closure(a1))


def automata_epsilon():
    return NFA(states=1, finals=[0], transitions={})


def automata_optional(a1):
    return automata_union(a1, automata_epsilon())


def automata_negation(a1):
    finals = set()
    for i in range(a1.states):
        if i not in a1.finals:
            finals.add(i)
    a1.finals = finals
    return a1


def automata_symbol(symbol):
    return NFA(states=2, finals=[1], transitions={(0, symbol): [1]})


def distinguish_states(group, automaton, partition):
    split = {}

    for member in group:
        found_group = False
        for rep in split.keys():
            if are_in_same_subgroup(member, rep, automaton, partition):
                found_group = True
                split[rep] += [member]
        if found_group:
            continue
        split[member] = [member]

    return [group for group in split.values()]


def are_in_same_subgroup(s1, s2, automaton, partition, _inverse=False):
    for symbol in automaton.transitions[s1].keys():
        s = automaton.transitions[s1][symbol][0]
        g = partition_index(s, partition)
        if symbol not in automaton.transitions[s2].keys():
            return False
        if g != partition_index(automaton.transitions[s2][symbol][0], partition):
            return False
    return not _inverse or are_in_same_subgroup(s2, s1, automaton, partition, _inverse=True)


def partition_index(state, partition):
    for i in range(len(partition.groups)):
        if state in [n.lex for n in partition.groups[i]]:
            return i
    raise KeyError("Couldn't find partition group for state")


def state_minimization(automaton):
    partition = DisjointSet(*range(automaton.states))

    partition.merge(automaton.finals)
    partition.merge([s for s in range(automaton.states) if s not in automaton.finals])

    while True:
        new_partition = DisjointSet(*range(automaton.states))

        for group in partition.groups:
            sub_groups = distinguish_states([n.lex for n in group], automaton, partition)
            for sub_group in sub_groups:
                new_partition.merge(sub_group)

        if len(new_partition) == len(partition):
            break

        partition = new_partition

    return partition


def automata_minimization(automaton):
    partition = state_minimization(automaton)

    states = [s for s in partition.representatives]

    transitions = {}
    for i, state in enumerate(states):
        origin = state.lex
        for symbol, destinations in automaton.transitions[origin].items():
            dest = destinations[0]
            for e in range(len(states)):
                if dest in [n.lex for n in partition.groups[e]]:
                    dest = e
                    break

            transitions[i, symbol] = dest

    finals = [i for i in range(len(states))
              if any([node.lex in automaton.finals for node in partition.groups[i]])]

    start = None

    for i in range(len(states)):
        if automaton.start in [node.lex for node in partition.groups[i]]:
            start = i

    return DFA(len(states), finals, transitions, start)
