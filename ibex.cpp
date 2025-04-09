#include <iostream>
#include "ibex.h"   // 請根據實際安裝路徑調整

using namespace ibex;
using namespace std;

int main() {
    // 定義變數順序與對應索引：
    // [0]: X, [1]: Y, [2]: Z, [3]: B, [4]: S, [5]: K, [6]: A, [7]: C, [8]: D, [9]: R
    const int n_vars = 10;
    
    // 建立 IntervalVector
    IntervalVector domain(n_vars);
    
    // 給定目標變數與參數的區間：
    // X 有限制
    domain[0] = Interval(3, 8); // X
    // 假設參數已知區間：
    domain[5] = Interval(1, 2);     // K
    domain[3] = Interval(123, 125);   // B
    domain[8] = Interval(-1, 1);      // D
    // R 有多個選項，這裡取凸包 [3,22] 作為初始區間
    domain[9] = Interval(3, 22);      // R
    
    // 對於中間變數（Y, Z, S, A, C），若沒有明確限制則設定寬泛的預設區間
    Interval wide(-1e6, 1e6);
    domain[1] = wide;  // Y
    domain[2] = wide;  // Z
    domain[4] = wide;  // S
    domain[6] = wide;  // A
    domain[7] = wide;  // C

    // --- 定義約束（轉換為 "左 - 右 = 0" 形式）---
    // (1) X = Y + Z + B  →  X - Y - Z - B = 0
    Constraint cons1("X - Y - Z - B", vector<string>{"X", "Y", "Z", "B"});
    
    // (2) Y = S * R  →  Y - S * R = 0
    Constraint cons2("Y - S * R", vector<string>{"Y", "S", "R"});
    
    // (3) S = K - 1  →  S - (K - 1) = 0
    Constraint cons3("S - (K - 1)", vector<string>{"S", "K"});
    
    // (4) Z = A  →  Z - A = 0
    Constraint cons4("Z - A", vector<string>{"Z", "A"});
    
    // (5) A = C - 1  →  A - (C - 1) = 0
    Constraint cons5("A - (C - 1)", vector<string>{"A", "C"});
    
    // (6) C = D * 2  →  C - 2 * D = 0
    Constraint cons6("C - 2 * D", vector<string>{"C", "D"});
    
    // --- 建立 Contractor Network 並加入約束 ---
    ContractorNetwork network;
    network.add(cons1);
    network.add(cons2);
    network.add(cons3);
    network.add(cons4);
    network.add(cons5);
    network.add(cons6);
    
    // --- 反向區間收縮 ---
    double tol = 1e-5; // 收縮容差
    network.contract(domain, tol);
    
    // --- 輸出收縮後的區間 ---
    cout << "Contracted intervals:" << endl;
    cout << "X: " << domain[0] << endl;
    cout << "Y: " << domain[1] << endl;
    cout << "Z: " << domain[2] << endl;
    cout << "B: " << domain[3] << endl;
    cout << "S: " << domain[4] << endl;
    cout << "K: " << domain[5] << endl;
    cout << "A: " << domain[6] << endl;
    cout << "C: " << domain[7] << endl;
    cout << "D: " << domain[8] << endl;
    cout << "R: " << domain[9] << endl;
    
    return 0;
}
