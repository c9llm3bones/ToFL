#include "../include/LongRules.h"
#include <iostream>
#include <set>
#include <string>

using namespace std;

void remove_long_rules(Grammatic &G) {
    for (auto &it : G.Rules) {
        string nonterm = it.first;
        vector<vector<string>> &alternatives = it.second;
        vector<vector<string>> new_alts; 

        for (auto &alt : alternatives) {
            int k = (int)alt.size();

            if (k <= 2) {
                new_alts.push_back(alt);
                continue;
            }

            vector<string> newNts;
            for (int i = 0; i < k-2; i++) {
                newNts.push_back(add_nonterm(G.Nonterms));
            }

            vector<string> first_rule = { alt[0], newNts[0] };
            new_alts.push_back(first_rule);

            for (int i = 0; i < (int)newNts.size() - 1; i++) {
                vector<string> mid_rule = { alt[i+1], newNts[i+1] };
                G.Rules[newNts[i]].push_back(mid_rule);
            }

            vector<string> last_rule = { alt[k-2], alt[k-1] };
            G.Rules[newNts.back()].push_back(last_rule);
        }

        alternatives = new_alts;
    }
}
