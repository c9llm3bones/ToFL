#include "../include/ChainRules.h"

bool isChainRule(const vector<string> &alt, const set<string> &Nonterms) {
    return (alt.size() == 1 && Nonterms.find(alt[0]) != Nonterms.end());
}

void remove_chain_rules(Grammatic &G) {
    // граф цепных переходов
    unordered_map<string, vector<string>> chainGraph;
    
    for (auto &r : G.Rules) {
        string A = r.first;
        for (auto &alt : r.second) {
            if (isChainRule(alt, G.Nonterms)) {
                chainGraph[A].push_back(alt[0]);
            }
        }
    }

    //  находим все цепные пары 
    set<pair<string, string>> chainPairs;
    for (auto &A : G.Nonterms) {
        queue<string>q;
        q.push(A);
        set<string> visited;
        visited.insert(A);

        while (!q.empty()) {
            string cur = q.front(); q.pop();
            chainPairs.insert({A, cur});

            if (chainGraph.find(cur) != chainGraph.end()) {
                for (auto &nx : chainGraph[cur]) {
                    if (visited.find(nx) == visited.end()) {
                        visited.insert(nx);
                        q.push(nx);
                    }
                }
            }
        }
    }

    // добавляем нецепные правила
    unordered_map<string, set<vector<string>>> newRules; 
    for (auto &p : chainPairs) {
        string A = p.first;
        string B = p.second;
        if (G.Rules.find(B) != G.Rules.end()) {
            for (auto &alt : G.Rules[B]) {
                if (!isChainRule(alt, G.Nonterms)) {
                    newRules[A].insert(alt);
                }
            }
        }
    }

    for (auto &r : newRules) {
        string A = r.first;
        for (auto &alt : r.second) {
            auto &alts = G.Rules[A];
            if (find(alts.begin(), alts.end(), alt) == alts.end()) {
                alts.push_back(alt);
            }
        }
    }

    // удаляем цепные правила 
    for (auto &r : G.Rules) {
        auto &alts = r.second;
        alts.erase(remove_if(alts.begin(), alts.end(), 
                [&](const vector<string> &alt){ return isChainRule(alt, G.Nonterms); }), alts.end());
    }
}