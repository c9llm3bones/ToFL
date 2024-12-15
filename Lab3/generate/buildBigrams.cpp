#include <string>
#include <set>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <random>
#include <iostream>
#include <algorithm>
#include "../include/Grammatic.h"
#include "../include/CYK.h"
#include "../include/LongRules.h"
#include "../include/EpsilonRules.h"
#include "../include/ChainRules.h"
#include "../include/NonGeneratingRules.h"
#include "../include/UnreachableRules.h"
#include "../include/ReplaceTerminals.h"

using namespace std;
// Множества:
// FIRST, FOLLOW, LAST, PRECEDE: string (нетерминал) -> множество терминалов

static random_device rd;
static mt19937 gen(rd());


void compute_FIRST(const Grammatic &G,
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

void compute_LAST(const Grammatic &G,
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

void compute_FOLLOW(const Grammatic &G,
    const unordered_map<string, unordered_set<string>> &FIRST,
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

void compute_PRECEDE(const Grammatic &G,
    const unordered_map<string, unordered_set<string>> &LAST,
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

unordered_map<string, unordered_set<string>> allowedBigrams;

void build_bigrams(
    const Grammatic &G,
    const unordered_map<string, unordered_set<string>> &FIRST,
    const unordered_map<string, unordered_set<string>> &FOLLOW,
    const unordered_map<string, unordered_set<string>> &LAST,
    const unordered_map<string, unordered_set<string>> &PRECEDE
) {
   
    for (auto &r : G.Rules) {
        for (auto &alt : r.second) {
            for (size_t i = 0; i + 1 < alt.size(); i++) {
                const string &sym1 = alt[i];
                const string &sym2 = alt[i+1];
                if (G.Terms.find(sym1) != G.Terms.end() && G.Terms.find(sym2) != G.Terms.end()) {
                    allowedBigrams[sym1].insert(sym2);
                }
            }
        }
    }

    for (auto &A1 : G.Nonterms) {
        const auto &lastSet = LAST.at(A1);
        const auto &followSet = FOLLOW.at(A1);
        for (auto &γ1 : lastSet) {
            for (auto &γ2 : followSet) {
                allowedBigrams[γ1].insert(γ2);
            }
        }
    }

    for (auto &A2 : G.Nonterms) {
        const auto &precedeSet = PRECEDE.at(A2);
        const auto &firstSet = FIRST.at(A2);
        for (auto &γ1 : precedeSet) {
            for (auto &γ2 : firstSet) {
                allowedBigrams[γ1].insert(γ2);
            }
        }
    }

    for (auto &A1 : G.Nonterms) {
        const auto &lastSet = LAST.at(A1);
        const auto &followSet = FOLLOW.at(A1);
        for (auto &A2 : G.Nonterms) {
            const auto &firstSet = FIRST.at(A2);
            for (auto &γ1 : lastSet) {
                for (auto &γ2 : firstSet) {
                    if (followSet.find(γ2) != followSet.end()) {
                        allowedBigrams[γ1].insert(γ2);
                    }
                }
            }
        }
    }

}

unordered_set<string> startTerminals;
unordered_set<string> finalTerminals;

vector<string> allTerminals;

// вероятность выбрать не из allowedBigrams для негатива
double p_noise = 0.05; 
// вероятность остановиться на финальном терминале
double p_stop_on_final = 0.3; 
int maxLen = 1000;

template<typename T>
T random_choice(const unordered_set<T>& s) {
    vector<T> vec(s.begin(), s.end());
    uniform_int_distribution<size_t> dist(0, vec.size()-1);
    return vec[dist(gen)];
}

template<typename T>
T random_choice(const vector<T>& v) {
    uniform_int_distribution<size_t> dist(0, v.size()-1);
    return v[dist(gen)];
}

string generate_positive_bigrambased() {
    if (startTerminals.empty()) return "";
    string current = random_choice(startTerminals);

    vector<string> result;
    result.push_back(current);

    for (int i = 1; i < maxLen; i++) {
        if (finalTerminals.find(current) != finalTerminals.end()) {
            uniform_real_distribution<double> dist(0.0, 1.0);
            if (dist(gen) < p_stop_on_final) {
                break; 
            }
        }

        auto it = allowedBigrams.find(current);
        if (it == allowedBigrams.end() || it->second.empty()) {
            break;
        }

        string nextTerm = random_choice(it->second);
        result.push_back(nextTerm);
        current = nextTerm;
    }
    
    string out;
    for (auto &t : result) {
        out += t;
    }
    return out;
}

string removeChar(const string& input, char toRemove) {
    string result = input;
    result.erase(remove(result.begin(), result.end(), toRemove), result.end());
    return result;
}

string generate_negative_bigrambased() {
    // начнём со стартового, но на одном из шагов подмешаем терминал, которого нет в allowedBigrams[current].

    if (startTerminals.empty()) return "";
    string current = random_choice(startTerminals);

    vector<string> result;
    result.push_back(current);

    for (int i = 1; i < maxLen; i++) {
        uniform_real_distribution<double> dist(0.0, 1.0);
        if (dist(gen) < p_noise) {
            string noiseTerm = "#";
            auto it = allowedBigrams.find(current);
            unordered_set<string> allowedSet;
            if (it != allowedBigrams.end()) {
                allowedSet = it->second;
            }

            bool foundNoise = false;
            for (auto &tm : allTerminals) {
                if (allowedSet.find(tm) == allowedSet.end()) {
                    noiseTerm = tm;
                    foundNoise = true;
                    break;
                }
            }

            result.push_back(noiseTerm);
            current = noiseTerm;
        } else {
            auto it = allowedBigrams.find(current);
            if (it == allowedBigrams.end() || it->second.empty()) {
                break;
            }
            string nextTerm = random_choice(it->second);
            result.push_back(nextTerm);
            current = nextTerm;
        }
    }

    string out;
    for (auto &t : result) {
        out += t;
    }
    return out;
}

set<pair<string,bool>> generate_tests_bigrambased(Grammatic G, int numTests, double positiveRatio) {
    int numPos = (int)(numTests * positiveRatio);
    int numNeg = numTests - numPos;

    set<pair<string,bool>> tests;

    for (int i = 0; i < numPos; i++) {
        string s = generate_positive_bigrambased();
        s = removeChar(s, '$');
        //s = removeChar(s, ' ');
        //cout << s << endl;
        if (cyk(G, s))
            tests.insert({s,true});
    }

    for (int i = 0; i < numNeg; i++) {
        string s = generate_negative_bigrambased();
        s = removeChar(s, '$');
        //s = removeChar(s, ' ');
        //cout << s << endl;
        if (!cyk(G, s))
            tests.insert({s,false});
    }

    return tests;
}

int main() {
    
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S", "A", "B", "D"};
    G.Terms = {"x", "y", "z", "w"};

    G.Rules["S"].push_back({"A", "B"});   // S → A B
    G.Rules["S"].push_back({"x"});        // S → x
    G.Rules["A"].push_back({"y", "A"});   // A → y A
    G.Rules["A"].push_back({"z"});        // A → z
    G.Rules["B"].push_back({"w"});        // B → w
    G.Rules["B"].push_back({"D"});        // B → D
    G.Rules["D"].push_back({"x", "y"});   // D → x y
    G.Rules["D"].push_back({"A"});        // D → z


    remove_long_rules(G);
    //G.print();
    remove_epsilon_rules(G);
    //G.print();
    remove_chain_rules(G);
    //G.print();
    remove_nongenerating(G);
    //G.print();
    remove_unreachable(G);
    //G.print();
    replace_terminals(G);

    delete_dublicate_rules(G);

    G.print();

    unordered_map<string, unordered_set<string>> FIRST, FOLLOW, LAST, PRECEDE;

    compute_FIRST(G, FIRST);
    compute_LAST(G, LAST);
    compute_FOLLOW(G, FIRST, FOLLOW);
    compute_PRECEDE(G, LAST, PRECEDE);

    //cout << "FIRST sets:\n";
    for (auto &p : FIRST) {
        //cout << p.first << ": ";
        for (auto &t : p.second)  {
            //cout << t << " ";
            startTerminals.insert(t);
        }
        //cout << "\n";
    }

    /*cout << "\nFOLLOW sets:\n";
    for (auto &p : FOLLOW) {
        cout << p.first << ": ";
        for (auto &t : p.second) cout << t << " ";
        cout << "\n";
    }
    */
    //cout << "\nLAST sets:\n";
    for (auto &p : LAST) {
        //cout << p.first << ": ";
        for (auto &t : p.second){
            //cout << t << " ";
            finalTerminals.insert(t);
        }
        //cout << "\n";
    }
    
    /*cout << "\nPRECEDE sets:\n";
    for (auto &p : PRECEDE) {
        cout << p.first << ": ";
        for (auto &t : p.second) cout << t << " ";
        cout << "\n";
    }
    */

    build_bigrams(G, FIRST, FOLLOW, LAST, PRECEDE);

    for (auto &pair : allowedBigrams) {
        cout << pair.first << " -> ";
        for (auto &t2 : pair.second) {
            cout << t2 << " ";
        }
        cout << endl;
    }

    auto tests = generate_tests_bigrambased(G, 200, 0.5);
    for (auto &t : tests) {
        cout << (t.second ? "POS: " : "NEG: ") << t.first << "\n";
    }
    return 0;   
}
