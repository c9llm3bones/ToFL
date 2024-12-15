#ifndef REPLACETERMINALS_H
#define REPLACETERMINALS_H

#include <string>
#include <set>
#include <vector>
#include <unordered_map>
#include "Grammatic.h"

using namespace std;

void replace_terminals(Grammatic& G);
string get_or_create_terminal_nonterm(unordered_map<string, string> &termToNonterm,
                                           set<string> &Nonterms,
                                           const string &term);
void delete_dublicate_rules(Grammatic &G);
#endif // REPLACETERMINALS_H
