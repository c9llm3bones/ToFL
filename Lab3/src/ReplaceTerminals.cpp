#include "../include/ReplaceTerminals.h"

using namespace std;

// генерирует новый нетерминал для терминала
string get_or_create_terminal_nonterm(unordered_map<string, string> &termToNonterm,
                                           set<string> &Nonterms,
                                           const string &term) {
    auto it = termToNonterm.find(term);
    if (it != termToNonterm.end()) {
        return it->second;
    }

    string newNonterm = "U_" + term;
    Nonterms.insert(newNonterm);

    termToNonterm[term] = newNonterm;
    return newNonterm;
}

void replace_terminals(Grammatic &G) {
    unordered_map<string, string> termToNonterm;
    vector<pair<string, string>> newTerminalRules;

    for (auto &r : G.Rules) {
        for (auto &alt : r.second) {
            if (alt.size() > 1) {
                for (int i = 0; i < (int)alt.size(); i++) {
                    const string &sym = alt[i];
                    if (G.Terms.find(sym) != G.Terms.end()) {
                        string U = get_or_create_terminal_nonterm(termToNonterm, G.Nonterms, sym);
                        alt[i] = U;
                    }
                }
            }
        }
    }

    for (auto &p : termToNonterm) {
        const string &term = p.first;
        const string &nonterm = p.second;
        // U_term -> term
        G.Rules[nonterm].push_back({term});
    }
}


void delete_dublicate_rules(Grammatic &G) {
    for (auto &rule : G.Rules) {
        const string &nonterm = rule.first;          
        vector<vector<string>> &alts = rule.second;
        
        set<vector<string>> uniqueAlts(alts.begin(), alts.end());
        
        alts.assign(uniqueAlts.begin(), uniqueAlts.end());
    }
}
