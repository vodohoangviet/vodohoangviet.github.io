#pragma once
#include <vector>
#include <optional>
using namespace std;

// ============================================================
//  STACK TỔNG QUÁT (TEMPLATE)
//  - Dùng vector động: không còn giới hạn cứng (cũ: double[500])
//  - RAII: tự giải phóng bộ nhớ, không cần delete thủ công
//  - Dùng chung được cho double (RPNevaluation) và string (postfixToInfix)
// ============================================================
template <typename T>
struct Stack
{
    vector<T> values;

    void push(const T& v)
    {
        values.push_back(v);
    }

    optional<T> pop()
    {
        if (values.empty())
            return {};
        T v = values.back();
        values.pop_back();
        return v;
    }

    // Xem phần tử trên cùng mà không xóa
    optional<T> peek() const
    {
        if (values.empty())
            return {};
        return values.back();
    }

    int getSize() const
    {
        return (int)values.size();
    }

    bool empty() const
    {
        return values.empty();
    }
};
