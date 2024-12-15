#include "../include/Grammatic.h"
#include <iostream>
#include <set>
#include <string>

using namespace std;

/*Grammatic::Grammatic() {
  
}
*/

void Grammatic::print() const {
    /*
    for (const auto N : Nonterms) {
        cout << N << ' ';
    }
    cout << endl;
    for (const auto T : Terms) {
        cout << T << ' ';
    }
    */
    for (const auto &rule : Rules) {
        for (const auto &alt : rule.second) {
            cout << rule.first << " -> ";
            if (alt.empty()) {
                cout << "EPSILON";
            } else {
                for (const auto &sym : alt) {
                    cout << sym << " ";
                }
            }
            cout << endl;
        }
    }
    cout << endl;
}

const string ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

static int newNontermCounter = 0;
string add_nonterm(set<string> &Nonterms) {
    string newN;
    do {
        newN = ALPH[rand() % ALPH.length()] + to_string(newNontermCounter++);
    } while (Nonterms.find(newN) != Nonterms.end());
    Nonterms.insert(newN);
    return newN;
}