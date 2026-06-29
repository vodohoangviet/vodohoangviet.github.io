#include <iostream>
#include <optional>
#include <stdexcept>
#include <sstream>
#include <string>
#include <vector>
#include <limits>

#include "stack.h"
#include "queue.h"
#include "validNum.h"
#include "RPNevaluation.h"
#include "postfixtoinfix.h"
#include "resHistory.h"
#include "hashTableRPN.h"
#include "ui.h"

using namespace std;

const int BOX_WIDTH = 64;

// ============================================================
//  TIỆN ÍCH NHẬP LIỆU AN TOÀN
//  BUG ĐÃ SỬA: code cũ "cin >> choice" hay "cin >> result" không kiểm
//  tra lỗi định dạng. Nếu người dùng nhập chữ thay vì số, cin sẽ rơi
//  vào failbit và toàn bộ vòng lặp sau đó loạn nhịp (đọc lại giá trị cũ
//  vô hạn lần). Nay luôn kiểm tra fail() và xin nhập lại.
// ============================================================
int readInt(const string& prompt)
{
    int v;
    while (true)
    {
        cout << GREEN << prompt << RESET;
        if (cin >> v)
        {
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return v;
        }
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        cout << RED << "Vui long nhap mot so nguyen hop le!\n" << RESET;
    }
}

double readDouble(const string& prompt)
{
    double v;
    while (true)
    {
        cout << GREEN << prompt << RESET;
        if (cin >> v)
        {
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            return v;
        }
        cin.clear();
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        cout << RED << "Vui long nhap mot so thuc hop le!\n" << RESET;
    }
}

// ============================================================
//  MENU CHÍNH (UI nâng cấp: khung Unicode, căn chỉnh, màu sắc)
// ============================================================
void printMenu()
{
    ui::boxTop(BOX_WIDTH);
    ui::title("Reverse Polish Notation Calculator", BOX_WIDTH, GREEN);
    ui::boxMid(BOX_WIDTH);
    ui::row("1. Nhap va tinh bieu thuc RPN", BOX_WIDTH);
    ui::row("2. Xem lich su ket qua", BOX_WIDTH);
    ui::row("3. Tim kiem ket qua trong lich su", BOX_WIDTH);
    ui::row("4. Tim kiem bieu thuc theo ket qua", BOX_WIDTH);
    ui::row("5. Chuyen hau to -> trung to (theo ket qua da luu)", BOX_WIDTH);
    ui::row("6. Xem toan bo bang bieu thuc", BOX_WIDTH);
    ui::row("7. Xoa mot ket qua trong lich su", BOX_WIDTH);
    ui::row("8. Xoa toan bo lich su", BOX_WIDTH);
    ui::row("9. Tro giup (cac toan tu ho tro)", BOX_WIDTH);
    ui::row("0. Thoat", BOX_WIDTH);
    ui::boxBottom(BOX_WIDTH);
}

void printHelp()
{
    ui::boxTop(BOX_WIDTH);
    ui::title("Cac toan tu duoc ho tro", BOX_WIDTH, CYAN);
    ui::boxMid(BOX_WIDTH);
    ui::row("Hai ngoi : + - * / % ^", BOX_WIDTH);
    ui::row("Mot ngoi : ~ (doi dau)  ! (giai thua)  sqrt (can bac hai)", BOX_WIDTH);
    ui::row("Vi du    : 5 3 -        => 2", BOX_WIDTH);
    ui::row("Vi du    : 9 sqrt       => 3", BOX_WIDTH);
    ui::row("Vi du    : 5 !          => 120", BOX_WIDTH);
    ui::row("Vi du    : 7 ~          => -7", BOX_WIDTH);
    ui::row("Vi du    : 10 3 %       => 1", BOX_WIDTH);
    ui::row("Tu khoa  : 'ans' dung lai ket qua lan truoc", BOX_WIDTH);
    ui::boxBottom(BOX_WIDTH);
}

int main()
{
    Res_History history;        // lưu kết quả
    HashTableRPN hashTable;      // lưu biểu thức theo kết quả
    double lastResult = 0.0;
    bool hasAns = false;         // kiểm tra xem đã có kết quả trước chưa

    while (true)
    {
        cout << "\n";
        printMenu();
        int choice = readInt("Nhap lua chon: ");

        ui::progressBar(string(CYAN) + "Dang xu ly" + RESET, 350, 16);

        if (choice == 0)
        {
            cout << BLUE << "Tam biet!\n" << RESET;
            break;
        }

        else if (choice == 1)
        {
            cout << GREEN << "Nhap bieu thuc hau to (cac token cach nhau boi dau cach): " << RESET;
            string expr;
            getline(cin, expr);

            if (expr.empty())
            {
                cout << RED << "Bieu thuc rong, khong co gi de tinh!\n" << RESET;
                continue;
            }

            // Đưa các token vào hàng đợi
            Queue q;
            istringstream iss(expr);
            string token;
            bool ansError = false;
            while (iss >> token)
            {
                if (token == "ans")
                {
                    if (hasAns)
                    {
                        q.push(ui::fmt(lastResult, 15));
                    }
                    else
                    {
                        cerr << RED << "Loi: Chua co ket qua truoc do (ans khong hop le)!" << RESET << endl;
                        ansError = true;
                        break;
                    }
                }
                else
                {
                    q.push(token);
                }
            }
            if (ansError)
                continue;

            try
            {
                double result = evaluateRPN(q);
                cout << GREEN << "Ket qua = " << ui::fmt(result) << RESET << endl;

                // Cập nhật giá trị ans
                lastResult = result;
                hasAns = true;

                // Lưu vào lịch sử và bảng băm
                history.add(result);
                hashTable.add(result, expr);
            }
            catch (const exception& e)
            {
                cerr << RED << "Loi: " << e.what() << RESET << endl;
            }
        }

        else if (choice == 2)
        {
            if (history.size() == 0)
            {
                cout << RED << "Lich su trong." << RESET << endl;
            }
            else
            {
                cout << "\n--------" << GREEN << "LICH SU KET QUA" << RESET << "--------\n";
                history.print();
                cout << BLUE << "Ban co muon sap xep ket qua tang dan? (Y/N): " << RESET;
                char opt;
                cin >> opt;
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                if (opt == 'Y' || opt == 'y')
                {
                    history.sortHistory();
                    history.print();
                }
                else if (opt == 'N' || opt == 'n')
                {
                    continue;
                }
                else
                {
                    cout << RED << "Lua chon khong hop le, bo qua sap xep.\n" << RESET;
                }
            }
        }

        else if (choice == 3)
        {
            double key = readDouble("Nhap ket qua can tim trong lich su: ");

            if (history.searchHistory(key))
                cout << GREEN << "Ket qua " << ui::fmt(key) << " co ton tai trong lich su.\n" << RESET;
            else
                cout << RED << "Khong tim thay ket qua nay trong lich su.\n" << RESET;
        }

        else if (choice == 4)
        {
            double key = readDouble("Nhap ket qua muon tim: ");

            optional<vector<string>> exprListOpt = hashTable.getValues(key);
            if (exprListOpt.has_value())
            {
                cout << GREEN << "Cac bieu thuc co ket qua = " << ui::fmt(key) << ":\n" << RESET;
                for (const string& e : exprListOpt.value())
                    cout << "=> " << YELLOW << e << RESET << endl;
            }
            else
            {
                cout << RED << "Khong tim thay ket qua nay trong bang bieu thuc.\n" << RESET;
            }
        }

        else if (choice == 5)
        {
            double result = readDouble("Nhap ket qua cua bieu thuc muon chuyen: ");

            if (history.searchHistory(result))
            {
                optional<vector<string>> exprListOpt = hashTable.getValues(result);
                cout << "Cac bieu thuc da co ket qua = " << ui::fmt(result) << ":\n";
                if (exprListOpt.has_value())
                {
                    for (const string& e : exprListOpt.value())
                    {
                        try
                        {
                            cout << "=> " << GREEN << postfixToInfix(e) << RESET << endl;
                        }
                        catch (const exception& ex)
                        {
                            cout << "=> " << RED << "(khong the chuyen doi: " << ex.what() << ")" << RESET << endl;
                        }
                    }
                }
            }
            else
            {
                cout << RED << "Khong tim thay ket qua nay trong bang bieu thuc.\n" << RESET;
            }
        }

        else if (choice == 6)
        {
            hashTable.print();
        }

        else if (choice == 7)
        {
            double result = readDouble("Nhap ket qua muon xoa: ");
            if (history.removeAll(result))
            {
                hashTable.remove(result);
                cout << GREEN << "Da xoa " << ui::fmt(result) << " khoi lich su" << RESET << endl;
            }
            else
                cout << RED << ui::fmt(result) << " khong ton tai trong lich su!" << RESET << endl;
        }

        else if (choice == 8)
        {
            history.clearHistory();
            hashTable.clear();
        }

        else if (choice == 9)
        {
            printHelp();
        }

        else
        {
            cout << RED << "Lua chon khong hop le!\n" << RESET;
        }
    }

    return 0;
}
