#include "../include/CYK.h"

using namespace std;


bool cyk(Grammatic &G, string &w) {
    int n = (int)w.size();
    if (n == 0) {
       
        return true;  
    }

    vector<string> nonterms(G.Nonterms.begin(), G.Nonterms.end());
    unordered_map<string,int> nontermIndex;
    for (int i = 0; i < (int)nonterms.size(); i++) {
        nontermIndex[nonterms[i]] = i;
    }

    int startIndex = nontermIndex.at(G.Start);

    unordered_map<string, vector<int>> termToNonterms;

    unordered_map<string, vector<int>> pairToNonterms;

    for (auto &r : G.Rules) {
        int A = nontermIndex.at(r.first);
        for (auto &alt : r.second) {
            if (alt.size() == 1 && G.Terms.find(alt[0]) != G.Terms.end()) {

                termToNonterms[alt[0]].push_back(A);
            } else if (alt.size() == 2 && 
                       G.Nonterms.find(alt[0]) != G.Nonterms.end() &&
                       G.Nonterms.find(alt[1]) != G.Nonterms.end()) {
               
                int B = nontermIndex.at(alt[0]);
                int C = nontermIndex.at(alt[1]);
           
                string key = to_string(B) + " " + to_string(C);
                pairToNonterms[key].push_back(A);
            } else {
                cout << endl << alt[0] << endl;
                throw invalid_argument("NOT in CNF");
             
            }
        }
    }


    vector<vector<vector<bool>>> d(nonterms.size(), vector<vector<bool>> (n, vector<bool>(n,false)));

    for (int i = 0; i < n; i++) {
        string sym(1, w[i]);
        if (termToNonterms.find(sym) != termToNonterms.end()) {
            for (int A : termToNonterms[sym]) {
                d[A][i][i] = true;
            }
        }
    }

    for (int length = 2; length <= n; length++) {
        for (int i = 0; i <= n - length; i++) {
            int j = i + length - 1;
           
            for (int k = i; k < j; k++) {
               
                vector<int> Bs, Cs;
                for (int b = 0; b < (int)nonterms.size(); b++) {
                    if (d[b][i][k]) Bs.push_back(b);
                }
                for (int c = 0; c < (int)nonterms.size(); c++) {
                    if (d[c][k+1][j]) Cs.push_back(c);
                }

                for (int B : Bs) {
                    for (int C : Cs) {
                        string key = to_string(B) + " " + to_string(C);
                        if (pairToNonterms.find(key) != pairToNonterms.end()) {
                            for (int A : pairToNonterms[key]) {
                                d[A][i][j] = true;
                            }
                        }
                    }
                }
            }
        }
    }

    return d[startIndex][0][n-1];
}