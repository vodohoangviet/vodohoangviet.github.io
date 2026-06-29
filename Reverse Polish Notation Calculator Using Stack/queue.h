#pragma once
#include <deque>
#include <optional>
#include <string>
using namespace std;

// ============================================================
//  QUEUE (HÀNG ĐỢI) - dùng std::deque
//  - Trước: mảng tĩnh string[1000] -> tràn nếu biểu thức quá dài
//  - Nay: không giới hạn kích thước, pop ở đầu O(1)
// ============================================================
struct Queue
{
    deque<string> values;

    void push(const string& v)
    {
        values.push_back(v);
    }

    optional<string> pop()
    {
        if (values.empty())
            return {};
        string v = values.front();
        values.pop_front();
        return v;
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
