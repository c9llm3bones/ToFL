#include "../include/EpsilonRules.h"
#include <iostream>
#include <set>
#include <string>

using namespace std;

bool isEpsilonAlternative(const vector<string> &alt) {
    return alt.empty();
}

//  все ε-порождающие нетерминалы
set<string> find_epsilon_nonterms(Grammatic &G) {
    set<string> epsilonNonterms;

    for (auto &r : G.Rules) {
        string A = r.first;
        for (auto &alt : r.second) {
            if (isEpsilonAlternative(alt)) {
                epsilonNonterms.insert(A);
                break;
            }
        }
    }

    bool changed = true;
    while (changed) {
        changed = false;
        for (auto &r : G.Rules) {
            string A = r.first;
            if (epsilonNonterms.find(A) != epsilonNonterms.end())
                continue;

            for (auto &alt : r.second) {
                bool allEpsilon = true;
                for (auto &sym : alt) {
                    if (G.Terms.find(sym) != G.Terms.end()) {
                        allEpsilon = false;
                        break;
                    }
                    if (G.Nonterms.find(sym) != G.Nonterms.end()) {
                        if (epsilonNonterms.find(sym) == epsilonNonterms.end()) {
                            allEpsilon = false;
                            break;
                        }
                    }
                }
                if (allEpsilon) {
                    epsilonNonterms.insert(A);
                    changed = true;
                    break;
                }
            }
        }
    }

    return epsilonNonterms;
}

void remove_epsilon_rules(Grammatic &G) {
    set<string> epsilonNonterms = find_epsilon_nonterms(G);


    unordered_map<string, vector<vector<string>>> newRules;

    for (auto &r : G.Rules) {
        string A = r.first;
        vector<vector<string>> &alts = r.second;

        vector<vector<string>> result_alts; 

        for (auto &alt : alts) {
            vector<int> epsilonPositions;
            for (int i = 0; i < (int)alt.size(); i++) {
                const string &sym = alt[i];
                if (epsilonNonterms.find(sym) != epsilonNonterms.end()) {
                    epsilonPositions.push_back(i);
                }
            }

            int subsetsCount = 1 << (int)epsilonPositions.size();
            for (int mask = 0; mask < subsetsCount; mask++) {
                vector<string> newAlt;
                for (int i = 0; i < (int)alt.size(); i++) {
                    bool removeSymbol = false;
                    for (int j = 0; j < (int)epsilonPositions.size(); j++) {
                        if ((mask & (1 << j)) && (epsilonPositions[j] == i)) {
                            removeSymbol = true;
                            break;
                        }
                    }
                    if (!removeSymbol) {
                        newAlt.push_back(alt[i]);
                    }
                }

                if (newAlt.empty()) {
                    if (A == G.Start && epsilonNonterms.find(A) != epsilonNonterms.end()) {
                        result_alts.push_back(newAlt);
                    }
                } else {
                    result_alts.push_back(newAlt);
                }
            }
        }

        newRules[A] = result_alts;
    }

    G.Rules = move(newRules);

}