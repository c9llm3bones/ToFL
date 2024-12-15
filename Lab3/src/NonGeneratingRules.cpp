#include "../include/NonGeneratingRules.h"

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