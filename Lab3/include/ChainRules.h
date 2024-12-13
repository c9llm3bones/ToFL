#ifndef CHAINRULES_H
#define CHAINRULES_H

#include "Grammatic.h"
#include <string>
#include <set>
#include <vector>
#include <queue>
#include <algorithm>

using namespace std;

bool isChainRule(const vector<string> &alt, const set<string> &Nonterms);
void remove_chain_rules(Grammatic &G);

#endif // CHAINRULES_H
