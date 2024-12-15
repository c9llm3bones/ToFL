#ifndef GENERATEWORDS_H
#define GENERATEWORDS_H

#include <string>
#include <set>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <random>
#include <iostream>
#include <algorithm>
#include "../include/Grammatic.h"
#include "../include/BuildBigrams.h"
#include "../include/CYK.h"

using namespace std;

static random_device rd;
static mt19937 gen(rd());

string add_nonterm(set<string> &Nonterms);

template<typename T>
T random_choice( unordered_set<T>& s);

template<typename T>
T random_choice( vector<T>& v);

string generate_positive_bigrambased();
string removeChar(string& input, char toRemove);
string generate_negative_bigrambased();
set<pair<string,bool>> generate_tests_bigrambased(Grammatic& G, int numTests, double positiveRatio);

#endif // GENERATEWORDS_H
