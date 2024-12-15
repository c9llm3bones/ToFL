#include "../include/GenerateWords.h"

// вероятность выбрать не из allowedBigrams для негатива
double p_noise = 0.05; 
// вероятность остановиться на финальном терминале
double p_stop_on_final = 0.3; 
int maxLen = 1000;

template<typename T>
T random_choice( unordered_set<T>& s) {
    vector<T> vec(s.begin(), s.end());
    uniform_int_distribution<size_t> dist(0, vec.size()-1);
    return vec[dist(gen)];
}

template<typename T>
T random_choice( vector<T>& v) {
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

string removeChar( string& input, char toRemove) {
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

set<pair<string,bool>> generate_tests_bigrambased(Grammatic& G, int numTests, double positiveRatio) {
    int numPos = (int)(numTests * positiveRatio);
    int numNeg = numTests - numPos;

    set<pair<string,bool>> tests;
    
    while (tests.size() < numTests) {
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
    }
    return tests;
}