#ifndef GRAMMATIC_H
#define GRAMMATIC_H

#include <string>
#include <set>
#include <vector>
#include <unordered_map>

using namespace std;

class Grammatic {
public:
    set<string> Nonterms;
    set<string> Terms;
    unordered_map<string, vector<vector<string>>> Rules; // N -> list(alternative_1, ... alternative_n)
    string Start = "S";

    //Grammatic(); // Конструктор
    void print() const; 
};

string add_nonterm(set<string> &Nonterms);

#endif // GRAMMATIC_H
