#pragma once
#include <iostream>
#include <string>
#include <vector>
#include <optional>
#include <cmath>
#include "ui.h"

using namespace std;

// ============================================================
//  Mỗi Item trong bảng băm lưu kết quả và danh sách biểu thức
//  BUG ĐÃ SỬA: vector<string> thay cho linked-list thủ công (ExprNode*)
//  -> không còn rò rỉ bộ nhớ, không cần delete tay từng node.
// ============================================================
struct Item
{
    double result;             // key = kết quả
    vector<string> exprs;      // danh sách biểu thức cho ra kết quả này
    Item* next;                // chaining khi collision trong cùng bucket

    Item(double r, const string& expr)
        : result(r), exprs{ expr }, next(nullptr) {
    }
};

// ============================================================
//  BẢNG BĂM (Hash Table) tự cài, chaining theo bucket
//
//  BUG ĐÃ SỬA:
//   1) "int k = 7" nhưng "Item* table[10]" -> chỉ dùng 7/10 bucket,
//      3 bucket cuối luôn rỗng, lãng phí và dễ nhầm khi đổi kích thước.
//      Nay: kích thước bảng và số bucket dùng MỘT hằng số duy nhất.
//   2) Hash ép kiểu (long long)(key * 1e6) có thể overflow với số rất
//      lớn. Nay dùng fmod để giới hạn trước khi ép kiểu.
//   3) So sánh double bằng "==" tại nhiều nơi (Has, getValues, remove)
//      khiến 2 kết quả "gần như giống nhau" về hiển thị nhưng lệch ở
//      bit thấp sẽ không khớp. Nay so sánh bằng epsilon dùng chung.
// ============================================================
struct HashTableRPN
{
    static const int BUCKETS = 17; // số nguyên tố giúp phân bố đều hơn
    Item* table[BUCKETS] = { nullptr };

    static constexpr double EPS = 1e-9;

    static bool nearlyEqual(double a, double b)
    {
        return fabs(a - b) < EPS;
    }

    // Hàm băm cho kết quả (double) - an toàn hơn với số lớn/âm
    int hash(double key) const
    {
        double scaled = fmod(key * 1000000.0, (double)BUCKETS);
        long long h = (long long)scaled;
        if (h < 0) h += BUCKETS;
        return (int)(h % BUCKETS);
    }

    // Thêm biểu thức mới
    void add(double result, const string& expr)
    {
        int h = hash(result);
        Item* cur = table[h];
        while (cur)
        {
            if (nearlyEqual(cur->result, result))
            {
                cur->exprs.insert(cur->exprs.begin(), expr); // thêm vào đầu danh sách
                return;
            }
            cur = cur->next;
        }
        // Nếu chưa tồn tại, tạo Item mới và thêm vào đầu bucket
        Item* newItem = new Item(result, expr);
        newItem->next = table[h];
        table[h] = newItem;
    }

    // Kiểm tra kết quả đã tồn tại chưa
    bool Has(double result) const
    {
        int h = hash(result);
        Item* cur = table[h];
        while (cur)
        {
            if (nearlyEqual(cur->result, result))
                return true;
            cur = cur->next;
        }
        return false;
    }

    // Lấy tất cả biểu thức theo kết quả
    optional<vector<string>> getValues(double result) const
    {
        int h = hash(result);
        Item* cur = table[h];
        while (cur)
        {
            if (nearlyEqual(cur->result, result))
                return cur->exprs;
            cur = cur->next;
        }
        return {};
    }

    // Xóa toàn bộ biểu thức theo kết quả
    void remove(double result)
    {
        int h = hash(result);
        Item* cur = table[h];
        Item* prev = nullptr;

        while (cur)
        {
            if (nearlyEqual(cur->result, result))
            {
                if (prev)
                    prev->next = cur->next;
                else
                    table[h] = cur->next;
                delete cur; // vector<string> tự giải phóng bên trong destructor
                return;
            }
            prev = cur;
            cur = cur->next;
        }
    }

    // In toàn bộ bảng băm
    void print() const
    {
        bool any = false;
        cout << "-------------" << GREEN << "RPN Expression History Table" << RESET << "----------------" << endl;
        for (int i = 0; i < BUCKETS; i++)
        {
            Item* cur = table[i];
            while (cur)
            {
                any = true;
                cout << GREEN << "  Result = " << ui::fmt(cur->result) << RESET << "   "
                     << UNDERLINE << RED << "Exprs:" << RESET << " ";
                for (size_t j = 0; j < cur->exprs.size(); ++j)
                {
                    cout << GREEN << cur->exprs[j] << RESET;
                    if (j + 1 < cur->exprs.size()) cout << " | ";
                }
                cout << "\n";
                cur = cur->next;
            }
        }
        if (!any)
            cout << GRAY << "  (bang con trong)\n" << RESET;
        cout << "---------------------------------------------------------" << endl;
    }

    // Xóa toàn bộ bảng băm
    void clear()
    {
        for (int i = 0; i < BUCKETS; i++)
        {
            Item* cur = table[i];
            while (cur)
            {
                Item* tmp = cur;
                cur = cur->next;
                delete tmp;
            }
            table[i] = nullptr;
        }
    }

    ~HashTableRPN()
    {
        clear();
    }
};
