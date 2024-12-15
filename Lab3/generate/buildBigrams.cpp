#include <string>
#include <set>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <random>
#include <iostream>
#include <algorithm>
#include "../include/BuildBigrams.h"

unordered_set<string> startTerminals;
unordered_set<string> finalTerminals;
vector<string> allTerminals;

unordered_map<string, unordered_set<string>> allowedBigrams;

using namespace std;
// Множества:
// FIRST, FOLLOW, LAST, PRECEDE: string (нетерминал) -> множество терминалов

void compute_FIRST(Grammatic &G,
    unordered_map<string, unordered_set<string>> &FIRST) 
{
    for (auto &A : G.Nonterms) {
        FIRST[A] = {};
    }

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto &r : G.Rules) {
            string A = r.first;
            for (auto &alt : r.second) {
                if (alt.size() == 1 && G.Terms.find(alt[0]) != G.Terms.end()) {
                    auto beforeSize = FIRST[A].size();
                    FIRST[A].insert(alt[0]);
                    if (FIRST[A].size() > beforeSize) changed = true;
                } else if (alt.size() == 2) {
                    string B = alt[0];
                    for (auto &t : FIRST[B]) {
                        auto beforeSize = FIRST[A].size();
                        FIRST[A].insert(t);
                        if (FIRST[A].size() > beforeSize) changed = true;
                    }
                }
            }
        }
    }
}

void compute_LAST(Grammatic &G,
    unordered_map<string, unordered_set<string>> &LAST) 
{
    for (auto &A : G.Nonterms) {
        LAST[A] = {};
    }

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto &r : G.Rules) {
            string A = r.first;
            for (auto &alt : r.second) {
                if (alt.size() == 1 && G.Terms.find(alt[0]) != G.Terms.end()) {
                    auto beforeSize = LAST[A].size();
                    LAST[A].insert(alt[0]);
                    if (LAST[A].size() > beforeSize) changed = true;
                } else if (alt.size() == 2) {
                    string C = alt[1];
                    size_t beforeSize = LAST[A].size();
                    for (auto &t : LAST[C]) {
                        LAST[A].insert(t);
                    }
                    if (LAST[A].size() > beforeSize) changed = true;
                }
            }
        }
    }
}

void compute_FOLLOW(Grammatic &G,
     unordered_map<string, unordered_set<string>> &FIRST,
    unordered_map<string, unordered_set<string>> &FOLLOW)
{
    for (auto &A : G.Nonterms) {
        FOLLOW[A] = {};
    }

    FOLLOW[G.Start].insert("$");

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto &r : G.Rules) {
            string A = r.first;
            for (auto &alt : r.second) {
                for (size_t i = 0; i < alt.size(); i++) {
                    string X = alt[i];
                    if (G.Nonterms.find(X) == G.Nonterms.end()) continue; 
                    if (i+1 < alt.size()) {
                        string Y = alt[i+1];
                        if (G.Terms.find(Y) != G.Terms.end()) {
                            size_t beforeSize = FOLLOW[X].size();
                            FOLLOW[X].insert(Y);
                            if (FOLLOW[X].size() > beforeSize) changed = true;
                        } else {
                            size_t beforeSize = FOLLOW[X].size();
                            for (auto &t : FIRST.at(Y)) {
                                FOLLOW[X].insert(t);
                            }
                            if (FOLLOW[X].size() > beforeSize) changed = true;
                        }
                    } else {
                        size_t beforeSize = FOLLOW[X].size();
                        for (auto &t : FOLLOW[A]) {
                            FOLLOW[X].insert(t);
                        }
                        if (FOLLOW[X].size() > beforeSize) changed = true;
                    }
                }
            }
        }
    }
}

void compute_PRECEDE(Grammatic &G,
     unordered_map<string, unordered_set<string>> &LAST,
    unordered_map<string, unordered_set<string>> &PRECEDE)
{
    for (auto &A : G.Nonterms) {
        PRECEDE[A] = {};
    }

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto &r : G.Rules) {
            string A = r.first;
            for (auto &alt : r.second) {
                if (alt.size() == 2) {
                    string B = alt[0], C = alt[1];
                    if (G.Nonterms.find(B) != G.Nonterms.end()) {
                        size_t beforeSize = PRECEDE[C].size();
                        for (auto &t : LAST.at(B)) {
                            PRECEDE[C].insert(t);
                        }
                        if (PRECEDE[C].size() > beforeSize) changed = true;
                    } else if (G.Terms.find(B) != G.Terms.end()) {
                        size_t beforeSize = PRECEDE[C].size();
                        PRECEDE[C].insert(B);
                        if (PRECEDE[C].size() > beforeSize) changed = true;
                    }
                }
            }
        }
    }
}


void build_bigrams(
    Grammatic &G,
    unordered_map<string, unordered_set<string>> &FIRST,
    unordered_map<string, unordered_set<string>> &FOLLOW,
    unordered_map<string, unordered_set<string>> &LAST,
    unordered_map<string, unordered_set<string>> &PRECEDE
) {
   
    for (auto &r : G.Rules) {
        for (auto &alt : r.second) {
            for (size_t i = 0; i + 1 < alt.size(); i++) {
                 string &sym1 = alt[i];
                 string &sym2 = alt[i+1];
                if (G.Terms.find(sym1) != G.Terms.end() && G.Terms.find(sym2) != G.Terms.end()) {
                    allowedBigrams[sym1].insert(sym2);
                }
            }
        }
    }

    for (auto &A1 : G.Nonterms) {
         auto &lastSet = LAST.at(A1);
         auto &followSet = FOLLOW.at(A1);
        for (auto &gam1 : lastSet) {
            for (auto &gam2 : followSet) {
                allowedBigrams[gam1].insert(gam2);
            }
        }
    }

    for (auto &A2 : G.Nonterms) {
         auto &precedeSet = PRECEDE.at(A2);
         auto &firstSet = FIRST.at(A2);
        for (auto &gam1 : precedeSet) {
            for (auto &gam2 : firstSet) {
                allowedBigrams[gam1].insert(gam2);
            }
        }
    }

    for (auto &A1 : G.Nonterms) {
         auto &lastSet = LAST.at(A1);
         auto &followSet = FOLLOW.at(A1);
        for (auto &A2 : G.Nonterms) {
             auto &firstSet = FIRST.at(A2);
            for (auto &gam1 : lastSet) {
                for (auto &gam2 : firstSet) {
                    if (followSet.find(gam2) != followSet.end()) {
                        allowedBigrams[gam1].insert(gam2);
                    }
                }
            }
        }
    }

}

