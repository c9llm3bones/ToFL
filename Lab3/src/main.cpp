//g++ -std=c++17 -Iinclude -o main src/main.cpp src/Grammatic.cpp src/LongRules.cpp src/EpsilonRules.cpp src/ChainRules.cpp src/NonGeneratingRules.cpp src/UnreachableRules.cpp src/ReplaceTerminals.cpp src/CYK.cpp

#include "../include/Grammatic.h"
#include "../include/LongRules.h"
#include "../include/EpsilonRules.h"
#include "../include/ChainRules.h"
#include "../include/NonGeneratingRules.h"
#include "../include/UnreachableRules.h"
#include "../include/ReplaceTerminals.h"
#include "../include/CYK.h"
#include <iostream>

using namespace std;

int main() {
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
    G.print();

    delete_dublicate_rules(G);

    G.print();
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


    return 0;
}   