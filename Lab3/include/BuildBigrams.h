#ifndef BUILDBIGRAMS_H
#define BUILDBIGRAMS_H

#include <string>
#include <set>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include "Grammatic.h"

using namespace std;

extern unordered_set<string> startTerminals;
extern unordered_set<string> finalTerminals;
extern vector<string> allTerminals;

extern unordered_map<string, unordered_set<string>> allowedBigrams;

void build_bigrams(
    Grammatic &G,
    unordered_map<string, unordered_set<string>> &FIRST,
    unordered_map<string, unordered_set<string>> &FOLLOW,
    unordered_map<string, unordered_set<string>> &LAST,
    unordered_map<string, unordered_set<string>> &PRECEDE
);

void compute_PRECEDE(Grammatic &G,
     unordered_map<string, unordered_set<string>> &LAST,
    unordered_map<string, unordered_set<string>> &PRECEDE);

void compute_FOLLOW( Grammatic &G,
     unordered_map<string, unordered_set<string>> &FIRST,
    unordered_map<string, unordered_set<string>> &FOLLOW);

void compute_LAST( Grammatic &G,
    unordered_map<string, unordered_set<string>> &LAST);

void compute_FIRST( Grammatic &G,
    unordered_map<string, unordered_set<string>> &FIRST);

#endif // BUILDBIGRAMS_H
