#!/usr/bin/python
# -------------------------------------------------------
# author     : Jinho D. Choi
# last update: 10/24/2012
# -------------------------------------------------------
import sys
import re
import os
import operator
from treebank import *
from math import log

# Reads a parse file, extract phrase structure rules, and prints the rules to an output file
def printRules(parseFile, ruleFile):
    reader = TBReader()
    reader.open(parseFile)
    fout = open(ruleFile, 'w')

    for tree in reader:
        for rule in tree.getPhraseRules():
            fout.write(' '.join(rule)+'\n')

# Reads phrase structure rules from a rule file and returns a dictionary containing the rules
# The dictionary takes a non-terminal as a key and a sub-dictionary as a value.
# The sub-dictionary takes the righthand side of the non-terminal as a key, and its count as a value
# e.g., the returned map = {'S': {'NP VP': 1}, 'VP': {'VP NP': 2}}
def getRules(ruleFile):
    fin   = open(ruleFile)
    rules = dict()
    
    for rule in fin:
        tmp = rule.split()
        lhs = tmp[0]
        rhs = ' '.join(tmp[1:])
        
        if lhs in rules:
            r = rules[lhs]
            if rhs in r: r[rhs] += 1
            else       : r[rhs]  = 1
        else:
            rules[lhs] = {rhs: 1}

    #Create <UNK> to handle unseen terminals and delete inaccurate
    #non-terminal rules (those occurring only once)
    for lhs in rules.keys():
        r = rules[lhs]
        for rhs in r.keys():
            if r[rhs] == 1:
                del r[rhs]
                if len(rhs.split()) == 1:
                    if '<UNK>' in r: r['<UNK>'] += 1
                    else: r['<UNK>'] = 1
    
    return rules
    
# Converts counts in the rules dictionary into probabilities
def toProbabilities(rules):
    for lhs in rules:
        r = rules[lhs]
        t = 0
        for rhs in r:
            t += r[rhs]
        
        for rhs in r:
            r[rhs] = log(float(r[rhs]) / t)

def printDict(rules, weightFile):
    fout = open(weightFile, 'w')

    for lhs in rules:
        r = rules[lhs]
        for rhs in r:
            print '%4s -> %16s %8.6f' % (lhs, rhs, r[rhs])
            fout.write(lhs + ' ' + rhs + ' ' + str(r[rhs]) + '\n')

PARSE_FILE = 'trn.parse'
RULE_FILE  = 'unweighted.rule'
WEIGHT_FILE = 'weighted.rule'

printRules(PARSE_FILE, RULE_FILE)
rules = getRules(RULE_FILE)
toProbabilities(rules)
printDict(rules, WEIGHT_FILE)

