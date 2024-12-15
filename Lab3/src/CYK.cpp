#include "../include/CYK.h"

using namespace std;


bool cyk(const Grammatic &G, const string &w) {
    int n = (int)w.size();
    if (n == 0) {
        // Пустая строка: если стартовый нетерминал может породить ε, тогда true, иначе false.
        // В НФХ пустая строка не выводится, если есть исключения, их надо обрабатывать отдельно.
        return true;  
    }

    // Соберём список нетерминалов
    vector<string> nonterms(G.Nonterms.begin(), G.Nonterms.end());
    // Создадим индекс для нетерминалов
    unordered_map<string,int> nontermIndex;
    for (int i = 0; i < (int)nonterms.size(); i++) {
        nontermIndex[nonterms[i]] = i;
    }

    // Определим стартовый нетерминал индекс
    int startIndex = nontermIndex.at(G.Start);

    // Разделим правила на два типа:
    // 1. A -> a (терминальные)
    // 2. A -> B C (нетерминальные)
    // Для ускорения CYK нам нужен обратный индекс:
    // Для каждого терминала a - список нетерминалов A: A->a
    unordered_map<string, vector<int>> termToNonterms;
    // Для каждой пары (B,C) - список нетерминалов A: A->B C
    // Используем ключ "B C"
    unordered_map<string, vector<int>> pairToNonterms;

    for (auto &r : G.Rules) {
        int A = nontermIndex.at(r.first);
        for (auto &alt : r.second) {
            if (alt.size() == 1 && G.Terms.find(alt[0]) != G.Terms.end()) {
                // A -> a
                termToNonterms[alt[0]].push_back(A);
            } else if (alt.size() == 2 && 
                       G.Nonterms.find(alt[0]) != G.Nonterms.end() &&
                       G.Nonterms.find(alt[1]) != G.Nonterms.end()) {
                // A -> B C
                int B = nontermIndex.at(alt[0]);
                int C = nontermIndex.at(alt[1]);
                // Ключ для пары
                string key = to_string(B) + " " + to_string(C);
                pairToNonterms[key].push_back(A);
            } else {
                cout << endl << alt[0] << endl;
                throw invalid_argument("NOT in CNF");
                
                // Правило не в ХНФ или нестандартное - предполагается, что грамматика уже в ХНФ
            }
        }
    }

    // Создадим массив d: d[a][i][j]
    // В C++ лучше использовать vector<bool> или vector<vector<vector<bool>>>.
    // i, j от 0 до n-1, a от 0 до |N|-1
    vector<vector<vector<bool>>> d(nonterms.size(), vector<vector<bool>> (n, vector<bool>(n,false)));

    // Инициализация для подстрок длины 1
    for (int i = 0; i < n; i++) {
        string sym(1, w[i]);
        if (termToNonterms.find(sym) != termToNonterms.end()) {
            for (int A : termToNonterms[sym]) {
                d[A][i][i] = true;
            }
        }
    }

    // Заполняем для подстрок длины m = 2..n
    // m - длина подстроки
    for (int length = 2; length <= n; length++) {
        for (int i = 0; i <= n - length; i++) {
            int j = i + length - 1;
            // Перебираем разбиение подстроки w[i..j] на две части: w[i..k] и w[k+1..j]
            for (int k = i; k < j; k++) {
                // Перебираем все пары нетерминалов (B,C) такие, что d[B][i][k] и d[C][k+1][j] = true
                // Чтобы не перебирать все B и C, пройдемся по всем, для которых d[B][i][k] = true и d[C][k+1][j] = true.

                // Одним из вариантов является перебор всех B,C, но это неэффективно.
                // Более эффективный подход - пройтись по всем нетерминалов B, для которых d[B][i][k] = true,
                // и по всем нетерминалам C, для которых d[C][k+1][j] = true,
                // и проверить, есть ли A с A->B C.

                // Собираем списки B,C
                vector<int> Bs, Cs;
                for (int b = 0; b < (int)nonterms.size(); b++) {
                    if (d[b][i][k]) Bs.push_back(b);
                }
                for (int c = 0; c < (int)nonterms.size(); c++) {
                    if (d[c][k+1][j]) Cs.push_back(c);
                }

                // Теперь для каждой пары (B,C) ищем A
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

    // Результат - d[S][0][n-1]
    return d[startIndex][0][n-1];
}