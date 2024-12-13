#include "../include/Grammatic.h"
#include "../include/LongRules.h"
#include "../include/EpsilonRules.h"
#include "../include/ChainRules.h"
#include <iostream>

using namespace std;

struct RuleInfo {
    string left;
    vector<string> right;
};

void remove_nongenerating(Grammatic& G) {
    vector<string> nontermList(G.Nonterms.begin(), G.Nonterms.end());
    unordered_map<string,int> nontermIndex;
    for (int i = 0; i < (int)nontermList.size(); i++) {
        nontermIndex[nontermList[i]] = i;
    }

    //  все правила в один список
    vector<RuleInfo> allRules;
    for (auto &r : G.Rules) {
        for (auto &alt : r.second) {
            allRules.push_back({r.first, alt});
        }
    }

    int R = (int)allRules.size();
    int N = (int)nontermList.size();
    
    vector<bool> isGenerating(N, false);
    vector<int> counter(R,0);

    vector<vector<int>> concernedRules(N);

    for (int rId = 0; rId < R; rId++) {
        const auto &rule = allRules[rId];
        int nontermsCount = 0;
        for (auto &sym : rule.right) {
            if (G.Nonterms.find(sym) != G.Nonterms.end()) {
                int idx = nontermIndex[sym];
                nontermsCount++;
                concernedRules[idx].push_back(rId);
            }
        }
        counter[rId] = nontermsCount;
    }

    queue<int> q;

    for (int rId = 0; rId < R; rId++) {
        if (counter[rId] == 0) {
            const string &A = allRules[rId].left;
            int Aidx = nontermIndex[A];
            if (!isGenerating[Aidx]) {
                isGenerating[Aidx] = true;
                q.push(Aidx);
            }
        }
    }

    while(!q.empty()) {
        int genNt = q.front(); q.pop();

        for (int rId : concernedRules[genNt]) {
            counter[rId]--;
            if (counter[rId] == 0) {
                int Aidx = nontermIndex[allRules[rId].left];
                if (!isGenerating[Aidx]) {
                    isGenerating[Aidx] = true;
                    q.push(Aidx);
                }
            }
        }
    }

    set<string> generatingNonterms;
    for (int i = 0; i < N; i++) {
        if (isGenerating[i]) {
            generatingNonterms.insert(nontermList[i]);
        }
    }

    unordered_map<string, vector<vector<string>>> newRules;
    for (auto &r : G.Rules) {
        const string &A = r.first;
        if (generatingNonterms.find(A) == generatingNonterms.end())
            continue; 
        
        for (auto &alt : r.second) {
            bool keep = true;
            for (auto &sym : alt) {
                if (G.Nonterms.find(sym) != G.Nonterms.end()) {
                    if (generatingNonterms.find(sym) == generatingNonterms.end()) {
                        keep = false; 
                        break;
                    }
                }
            }
            if (keep) {
                newRules[A].push_back(alt);
            }
        }
    }

    G.Rules = move(newRules);
    G.Nonterms = generatingNonterms;
}


void remove_unreachable(Grammatic &G) {
    std::set<std::string> reachable;
    reachable.insert(G.Start);

    bool changed = true;
    while (changed) {
        changed = false;
        // Просматриваем все правила
        for (auto &r : G.Rules) {
            const std::string &A = r.first;
            // Если A достижим
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

    std::set<std::string> newNonterms;
    for (auto &nt : G.Nonterms) {
        if (reachable.find(nt) != reachable.end()) {
            newNonterms.insert(nt);
        }
    }

    std::unordered_map<std::string, std::vector<std::vector<std::string>>> newRules;
    for (auto &r : G.Rules) {
        const std::string &A = r.first;
        if (reachable.find(A) != reachable.end()) {
            std::vector<std::vector<std::string>> newAlts;
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

    G.Rules = std::move(newRules);
    G.Nonterms = newNonterms;

}


// генерируем новый нетерминал для терминала
std::string get_or_create_terminal_nonterm(std::unordered_map<std::string, std::string> &termToNonterm,
                                           std::set<std::string> &Nonterms,
                                           const std::string &term) {
    auto it = termToNonterm.find(term);
    if (it != termToNonterm.end()) {
        return it->second;
    }

    std::string newNonterm = "U_" + term;
    Nonterms.insert(newNonterm);

    termToNonterm[term] = newNonterm;
    return newNonterm;
}

void replace_terminals(Grammatic &G) {
    std::unordered_map<std::string, std::string> termToNonterm;
    std::vector<std::pair<std::string, std::string>> newTerminalRules;

    for (auto &r : G.Rules) {
        for (auto &alt : r.second) {
            if (alt.size() > 1) {
                for (int i = 0; i < (int)alt.size(); i++) {
                    const std::string &sym = alt[i];
                    if (G.Terms.find(sym) != G.Terms.end()) {
                        std::string U = get_or_create_terminal_nonterm(termToNonterm, G.Nonterms, sym);
                        alt[i] = U;
                    }
                }
            }
        }
    }

    for (auto &p : termToNonterm) {
        const std::string &term = p.first;
        const std::string &nonterm = p.second;
        // U_term -> term
        G.Rules[nonterm].push_back({term});
    }
}

int main() {
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S","A","E", "B", "F"};
    G.Terms = {"a", "s", "f"};


    
    G.Rules["S"].push_back({});            // S → ε
    G.Rules["S"].push_back({"A", "c"});     // S → A B 
    G.Rules["S"].push_back({"C"});          // S -> C   
    G.Rules["A"].push_back({"a", "a", "a"});         // A → a
    G.Rules["A"].push_back({});            // A → ε
    G.Rules["A"].push_back({"B"});          // A -> B
    G.Rules["B"].push_back({"b"});          // B → b
    G.Rules["B"].push_back({"C"});             // B -> C
    G.Rules["C"].push_back({"e"});        // C -> e
    
    /*
    G.Rules["S"].push_back({"A", "S"});
    G.Rules["S"].push_back({"B", "S"});
    G.Rules["S"].push_back({"s"});
    G.Rules["E"].push_back({"E", "F"});
    G.Rules["E"].push_back({"F", "F"});
    G.Rules["A"].push_back({"a"});
    G.Rules["F"].push_back({"f"});
    */

    remove_long_rules(G);
    G.print();
    remove_epsilon_rules(G);
    G.print();
    remove_chain_rules(G);
    G.print();
    remove_nongenerating(G);
    G.print();
    remove_unreachable(G);
    G.print();
    replace_terminals(G);
    G.print();

    return 0;
}