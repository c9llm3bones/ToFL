#include "../include/UnreachableRules.h"

using namespace std;

void remove_unreachable(Grammatic &G) {
    set<string> reachable;
    reachable.insert(G.Start);

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto &r : G.Rules) {
            const string &A = r.first;
            if (reachable.find(A) != reachable.end()) {
                for (auto &alt : r.second) {
                    for (auto &sym : alt) {
                        if (G.Nonterms.find(sym) != G.Nonterms.end()) {
                            if (reachable.find(sym) == reachable.end()) {
                                reachable.insert(sym);
                                changed = true;
                            }
                        }
                    }
                }
            }
        }
    }

    set<string> newNonterms;
    for (auto &nt : G.Nonterms) {
        if (reachable.find(nt) != reachable.end()) {
            newNonterms.insert(nt);
        }
    }

    unordered_map<string, vector<vector<string>>> newRules;
    for (auto &r : G.Rules) {
        const string &A = r.first;
        if (reachable.find(A) != reachable.end()) {
            vector<vector<string>> newAlts;
            for (auto &alt : r.second) {
                bool keep = true;
                for (auto &sym : alt) {
                    if (G.Nonterms.find(sym) != G.Nonterms.end()) {
                        if (reachable.find(sym) == reachable.end()) {
                            
                            keep = false;
                            break;
                        }
                    }
                }
                if (keep) {
                    newAlts.push_back(alt);
                }
            }
            if (!newAlts.empty()) {
                newRules[A] = newAlts;
            }
        }
    }

    G.Rules = move(newRules);
    G.Nonterms = newNonterms;

}