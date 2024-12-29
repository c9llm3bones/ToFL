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

Grammatic readGrammarFromFile(const string& filename) {
    Grammatic G;
    ifstream file(filename);

    if (!file.is_open()) {
        throw runtime_error("Не удалось открыть файл: " + filename);
    }

    string line;
    while (getline(file, line)) {
        if (line.empty()) continue; 

        istringstream iss(line);
        string lhs;       
        string arrow;     
        string token;     

        iss >> lhs >> arrow; 

        if (arrow != "->") {
            throw runtime_error("Ошибка формата в строке: " + line);
        }

        G.Nonterms.insert(lhs); 

        vector<string> currentAlternative;
        while (iss >> token) {
            if (token == "|") {
                
                G.Rules[lhs].push_back(currentAlternative);
                currentAlternative.clear();
            } else {
                currentAlternative.push_back(token);
            }
        }

        if (!currentAlternative.empty()) {
            G.Rules[lhs].push_back(currentAlternative);
        }
    }

    for (const auto& [nonTerminal, alternatives] : G.Rules) {
        for (const auto& alternative : alternatives) {
            for (const auto& symbol : alternative) {
                if (G.Nonterms.find(symbol) == G.Nonterms.end()) {
                    G.Terms.insert(symbol);
                }
            }
        }
    }

    file.close();
    return G;
}


int main() {
    
    test_delete_dublicate_rules();
    test_cyk();

    cout << "All tests passed!" << endl;
    
    try {
        string filename = "tests/grammar.txt";

        Grammatic G = readGrammarFromFile(filename);

        G.print();
    } catch (const exception& e) {
        cerr << "Ошибка: " << e.what() << endl;
    }

    return 0;
}

/*
int main() {
    

    try {
        Grammatic G = loadGFromFile("tests/G.txt");
        //G.print();

    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
    }
    
    return 0;
}
*/