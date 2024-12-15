//g++ -std=c++17 -Iinclude -o main src/main.cpp src/Grammatic.cpp src/LongRules.cpp src/EpsilonRules.cpp src/ChainRules.cpp src/NonGeneratingRules.cpp src/UnreachableRules.cpp src/ReplaceTerminals.cpp generate/BuildBigrams.cpp generate/GenerateWords.cpp src/CYK.cpp 

#include "../include/Grammatic.h"
#include "../include/LongRules.h"
#include "../include/EpsilonRules.h"
#include "../include/ChainRules.h"
#include "../include/NonGeneratingRules.h"
#include "../include/UnreachableRules.h"
#include "../include/ReplaceTerminals.h"
#include "../include/CYK.h"
#include "../include/BuildBigrams.h"
#include "../include/GenerateWords.h"

#include <iostream>


using namespace std;

int main() {
    /*
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S","A","C", "B"};
    G.Terms = {"a", "c", "b", "e", "EPSILON"};


    
    G.Rules["S"].push_back({"EPSILON"});            // S → ε
    G.Rules["S"].push_back({"A", "c"});     // S → A B 
    G.Rules["S"].push_back({"C"});          // S -> C   
    G.Rules["A"].push_back({"a", "a", "a"});         // A → a
    G.Rules["A"].push_back({"EPSILON"});            // A → ε
    G.Rules["A"].push_back({"B"});          // A -> B
    G.Rules["B"].push_back({"b"});          // B → b
    G.Rules["B"].push_back({"C"});             // B -> C
    G.Rules["C"].push_back({"e"});        // C -> e
    */

    /*
    G.Rules["S"].push_back({"A", "S"});
    G.Rules["S"].push_back({"B", "S"});
    G.Rules["S"].push_back({"s"});
    G.Rules["E"].push_back({"E", "F"});
    G.Rules["E"].push_back({"F", "F"});
    G.Rules["A"].push_back({"a"});
    G.Rules["F"].push_back({"f"});
    */

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
    //G.print();

    delete_dublicate_rules(G);

    G.print();
    /*
    string w = "ec";
    bool result = cyk(G,w);
    cout << (result ? "YES" : "NO") << endl;

    Grammatic G1;
    G1.Start = "S";
    G1.Nonterms = {"S","A","B"};
    G1.Terms = {"a","b"};

    // Пример: S->A B, A->a, B->b
    G1.Rules["S"].push_back({"A","B"});
    G1.Rules["A"].push_back({"a"});
    G1.Rules["B"].push_back({"b"});

    w = "ab";
    result = cyk(G1,w);
    cout << (result ? "YES" : "NO") << endl;
    */

   
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
        //cout << pair.first << " -> ";
        for (auto &t2 : pair.second) {
            //cout << t2 << " ";
        }
        //cout << endl;
    }

    auto tests = generate_tests_bigrambased(G, 200, 0.5);
    for (auto &t : tests) {
        cout << (t.second ? "POS: " : "NEG: ") << t.first << "\n";
    }

    return 0;
}   