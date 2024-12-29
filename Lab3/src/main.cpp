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

#include <sstream>
#include <stdexcept>
#include <string>
#include <fstream>
#include <iostream>
#include <set>

using namespace std;

Grammatic readGrammarFromFile(const string& filename, const string& startSymbol = "S") {
    Grammatic G;
    ifstream file(filename);

    if (!file.is_open()) {
        throw runtime_error("Не удалось открыть файл: " + filename);
    }

    string line;
    int lineNumber = 0;
    set<string> tempTerminals;  // Temporary set to collect terminals

    while (getline(file, line)) {
        lineNumber++;
        if (line.empty()) continue;

        // Trim whitespace
        line.erase(0, line.find_first_not_of(" \t"));
        line.erase(line.find_last_not_of(" \t") + 1);
        if (line.empty()) continue;

        // Split into LHS and RHS
        size_t arrowPos = line.find("->");
        if (arrowPos == string::npos) {
            throw runtime_error("Ошибка формата в строке " + to_string(lineNumber) + ": " + line + 
                              "\nОжидалось '->'");
        }

        string lhs = line.substr(0, arrowPos);
        string rhs = line.substr(arrowPos + 2);

        // Trim spaces
        lhs.erase(0, lhs.find_first_not_of(" \t"));
        lhs.erase(lhs.find_last_not_of(" \t") + 1);
        rhs.erase(0, rhs.find_first_not_of(" \t"));
        rhs.erase(rhs.find_last_not_of(" \t") + 1);

        if (lhs.empty()) {
            throw runtime_error("Ошибка в строке " + to_string(lineNumber) + ": пустой нетерминал слева");
        }

        G.Nonterms.insert(lhs);

        // Split RHS by '|'
        vector<string> alternatives;
        size_t start = 0;
        size_t end = rhs.find('|');
        
        while (start < rhs.length()) {
            string alt;
            if (end == string::npos) {
                alt = rhs.substr(start);
                start = rhs.length();
            } else {
                alt = rhs.substr(start, end - start);
                start = end + 1;
                end = rhs.find('|', start);
            }
            
            // Trim the alternative
            alt.erase(0, alt.find_first_not_of(" \t"));
            alt.erase(alt.find_last_not_of(" \t") + 1);
            
            if (!alt.empty()) {
                alternatives.push_back(alt);
            }
        }

        if (alternatives.empty()) {
            throw runtime_error("Ошибка в строке " + to_string(lineNumber) + 
                              ": отсутствует правая часть правила для " + lhs);
        }

        // Process each alternative
        for (const string& alt : alternatives) {
            if (alt == "e") {
                G.Rules[lhs].push_back(vector<string>());  // empty production for epsilon
                continue;
            }

            vector<string> symbols;
            string currentSymbol;

            for (size_t i = 0; i < alt.length(); ++i) {
                if (isupper(alt[i])) {
                    // If we have accumulated a symbol, add it
                    if (!currentSymbol.empty()) {
                        symbols.push_back(currentSymbol);
                        if (G.Nonterms.find(currentSymbol) == G.Nonterms.end()) {
                            tempTerminals.insert(currentSymbol);
                        }
                        currentSymbol.clear();
                    }
                    // Add the uppercase letter as a separate symbol
                    symbols.push_back(string(1, alt[i]));
                } else {
                    currentSymbol += alt[i];
                }
            }
            // Add the last symbol if there is one
            if (!currentSymbol.empty()) {
                symbols.push_back(currentSymbol);
                if (G.Nonterms.find(currentSymbol) == G.Nonterms.end()) {
                    tempTerminals.insert(currentSymbol);
                }
            }

            G.Rules[lhs].push_back(symbols);
        }
    }

    // Copy unique terminals to G.Terms
    G.Terms = tempTerminals;

    // Validate start symbol
    if (G.Nonterms.find(startSymbol) == G.Nonterms.end()) {
        throw runtime_error("Ошибка: стартовый символ '" + startSymbol + 
                          "' не найден среди нетерминалов грамматики");
    }
    G.Start = startSymbol;

    file.close();
    return G;
}

int main() {
    /*
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S","A","C", "B"};
    G.Terms = {"a", "c", "b", "e"};
 
    G.Rules["S"].push_back({"A", "c"});     // S → A B 
    G.Rules["S"].push_back({"C"});          // S -> C   
    G.Rules["A"].push_back({"a", "a", "a"});         // A → a
    G.Rules["A"].push_back({"B"});          // A -> B
    G.Rules["B"].push_back({"b"});          // B → b
    G.Rules["B"].push_back({"C"});             // B -> C
    G.Rules["C"].push_back({"e"});        // C -> e
    */

    /*
    Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S","E","F", "A"};
    G.Terms = {"s", "a", "f"};
    G.Rules["S"].push_back({"A", "S"});
    G.Rules["S"].push_back({"B", "S"});
    G.Rules["S"].push_back({"s"});
    G.Rules["E"].push_back({"E", "F"});
    G.Rules["E"].push_back({"F", "F"});
    G.Rules["A"].push_back({"a"});
    G.Rules["F"].push_back({"f"});
    */

    /*
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
    */
    /*Grammatic G;
    G.Start = "S";
    G.Nonterms = {"S"};
    G.Terms = {"w", "t"};

    // Правила грамматики
    G.Rules["S"].push_back({"S", "t","S","t","S"});   // S → [SS1]
    G.Rules["S"].push_back({"w", "w","w","w","w"});
    */
    string filename = "tests/simple_grammar.txt";

    Grammatic G = readGrammarFromFile(filename);
    
    // Debug output
    cout << "Parsed Grammar Rules:" << endl;
    for (const auto& [nonterm, rules] : G.Rules) {
        cout << nonterm << " -> ";
        for (size_t i = 0; i < rules.size(); ++i) {
            const auto& rule = rules[i];
            if (rule.empty()) {
                cout << "e";
            } else {
                for (const auto& symbol : rule) {
                    cout << symbol;
                }
            }
            if (i < rules.size() - 1) {
                cout << " | ";
            }
        }
        cout << endl;
    }
    cout << "\nNon-terminals: ";
    for (const auto& nt : G.Nonterms) {
        cout << nt << " ";
    }
    cout << "\nTerminals: ";
    for (const auto& t : G.Terms) {
        cout << t << " ";
    }
    cout << endl;

    G.print();

    remove_long_rules(G);
    G.print();
    remove_epsilon_rules(G);
    G.print();
    remove_chain_rules(G);
    G.print();
    remove_nongenerating(G);
    G.print();
    remove_unreachable(G);
    G.print();
    replace_terminals(G);
    G.print();

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

    cout << "FIRST sets:\n";
    for (auto &p : FIRST) {
        cout << p.first << ": ";
        for (auto &t : p.second)  {
            cout << t << " ";
            startTerminals.insert(t);
        }
        cout << "\n";
    }

    cout << "\nFOLLOW sets:\n";
    for (auto &p : FOLLOW) {
        cout << p.first << ": ";
        for (auto &t : p.second) cout << t << " ";
        cout << "\n";
    }
    
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

    auto tests = generate_tests_bigrambased(G, 20, 0.5);
    for (auto &t : tests) {
        cout << (t.second ? "POS: " : "NEG: ") << t.first << "\n";
    }

    return 0;
}   