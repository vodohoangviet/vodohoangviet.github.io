#pragma once
#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include "hashTableRPN.h"
#include "ui.h"
using namespace std;

// ============================================================
//  LỊCH SỬ KẾT QUẢ
//
//  BUG ĐÃ SỬA:
//   1) Mảng động cấp phát tay (new[]/delete[]) -> rò rỉ bộ nhớ nếu có
//      exception giữa đường, không tuân RAII. Nay dùng vector<double>,
//      tự quản lý bộ nhớ hoàn toàn.
//   2) So sánh double bằng "==" trong removeAll/searchHistory: hai giá
//      trị "trông giống nhau" trên màn hình có thể lệch ở bit thấp do
//      sai số dấu phẩy động (vd kết quả của các phép chia/mũ) và sẽ
//      không khớp dù về logic phải khớp. Nay so sánh bằng epsilon.
//
//  TÍNH NĂNG MỚI:
//   - sortHistory dùng std::sort (introsort, O(n log n)) thay cho
//     bubble sort O(n^2) cũ, vẫn đúng kết quả nhưng nhanh hơn rất nhiều
//     khi lịch sử lớn.
//   - in bảng có số thứ tự, căn chỉnh đẹp hơn.
// ============================================================
struct Res_History
{
    vector<double> values;

    static constexpr double EPS = 1e-9;
    static bool nearlyEqual(double a, double b)
    {
        return fabs(a - b) < EPS;
    }

    void add(double v)
    {
        values.push_back(v);
    }

    int size() const { return (int)values.size(); }

    // Xóa TẤT CẢ phần tử có giá trị ~ result. Trả về true nếu có xóa.
    bool removeAll(double result)
    {
        size_t before = values.size();
        values.erase(
            remove_if(values.begin(), values.end(),
                [result](double v) { return nearlyEqual(v, result); }),
            values.end());
        return values.size() < before;
    }

    void print() const
    {
        if (values.empty())
        {
            cout << RED << "Lich su trong.\n" << RESET;
            return;
        }
        cout << GREEN << "Lich su ket qua (" << values.size() << " gia tri):\n" << RESET;
        for (size_t i = 0; i < values.size(); i++)
        {
            cout << GRAY << "  [" << i + 1 << "] " << RESET << CYAN << ui::fmt(values[i]) << RESET;
            if (i + 1 < values.size()) cout << "\n";
        }
        cout << endl;
    }

    // Sắp xếp tăng dần - dùng std::sort (nhanh hơn bubble sort O(n^2) cũ)
    void sortHistory()
    {
        sort(values.begin(), values.end());
    }

    // Tìm kiếm tuyến tính, trả về true nếu tìm thấy (so sánh epsilon)
    bool searchHistory(double target) const
    {
        for (double v : values)
            if (nearlyEqual(v, target))
                return true;
        return false;
    }

    // xóa toàn bộ lịch sử kết quả
    void clearHistory()
    {
        values.clear();
        cout << BLUE << "Da xoa lich su ket qua.\n" << RESET;
    }
};
