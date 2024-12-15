//  g++ -std=c++17 -Iinclude -o test tests/testsMain.cpp src/Grammatic.cpp src/LongRules.cpp src/EpsilonRules.cpp src/ChainRules.cpp src/NonGeneratingRules.cpp src/UnreachableRules.cpp src/ReplaceTerminals.cpp src/CYK.cpp 
#include "../include/Grammatic.h"
#include "../include/CYK.h"
#include "../include/ReplaceTerminals.h"
#include <iostream>
#include <cassert>
#include <sstream>
#include <stdexcept>
#include <string>
#include <fstream>

using namespace std;


void test_delete_dublicate_rules() {
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S", "A"};
    G.Terms = {"a", "b"};

    G.Rules["S"] = {{"A", "b"}, {"A", "b"}, {"a"}};
    G.Rules["A"] = {{"a"}, {"a"}, {"b"}};

    delete_dublicate_rules(G);

    assert(G.Rules["S"].size() == 2); // "A b" и "a"
    assert(G.Rules["A"].size() == 2); // "a" и "b"
    cout << "Test delete_dublicate_rules passed!" << endl;
}

void test_cyk() {
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S", "A", "B"};
    G.Terms = {"a", "b"};

    G.Rules["S"] = {{"A", "B"}};
    G.Rules["A"] = {{"a"}};
    G.Rules["B"] = {{"b"}};

    string testString = "ab";
    assert(cyk(G, testString) == true);

    testString = "aa";
    assert(cyk(G, testString) == false);

    testString = "b";
    assert(cyk(G, testString) == false);

    cout << "Test CYK passed!" << endl;
}

//дорабатывается 
Grammatic loadGrammarFromFile(const string &filename) {
    Grammatic G;
    ifstream file(filename);

    if (!file.is_open()) {
        throw runtime_error("Failed to open file: " + filename);
    }

    getline(file, G.Start);

    int numNonterms;
    file >> numNonterms;
    file.ignore(); 

    string line;
    getline(file, line);
    istringstream nontermsStream(line);
    for (int i = 0; i < numNonterms; ++i) {
        string nonterm;
        nontermsStream >> nonterm;
        G.Nonterms.insert(nonterm);
    }
    for (const auto N : G.Nonterms) {
        cout << N << ' ';
    }

    int numTerms;
    file >> numTerms;
    file.ignore(); 

    getline(file, line);
    istringstream termsStream(line);
    for (int i = 0; i < numTerms; ++i) {
        string term;
        termsStream >> term;
        G.Terms.insert(term);
    }

    int numRules;
    file >> numRules;
    file.ignore(); 

    for (int i = 0; i < numRules; ++i) {
        getline(file, line);
        istringstream ruleStream(line);

        string left;
        ruleStream >> left;

        vector<string> right;
        string sym;
        while (ruleStream >> sym) {
            right.push_back(sym);
        }

        G.Rules[left].push_back(right);
    }

    file.close();
    return G;
}


int main() {
    
    test_delete_dublicate_rules();
    test_cyk();

    cout << "All tests passed!" << endl;
    
    
    return 0;
}

/*
int main() {
    

    try {
        Grammatic G = loadGrammarFromFile("tests/grammar.txt");
        //G.print();

    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
    }
    
    return 0;
}
*/