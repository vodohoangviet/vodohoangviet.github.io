#pragma once
#include <iostream>
#include <optional>
#include <string>
#include <sstream>
#include "stack.h"
#include "validNum.h"
using namespace std;

// ============================================================
//  CHUYỂN BIỂU THỨC HẬU TỐ (POSTFIX) SANG TRUNG TỐ (INFIX)
//
//  BUG ĐÃ SỬA: cùng lỗi đảo a/b như evaluateRPN. "5 3 -" trước đây
//  cho ra "(3 - 5)" (sai), nay cho ra đúng "(5 - 3)".
//
//  Dùng lại Stack<string> chung từ stack.h (trước đây có StackString
//  riêng với mảng tĩnh string[500] -> nay không còn giới hạn).
//
//  TÍNH NĂNG MỚI: hỗ trợ hiển thị toán tử một ngôi mới (~, !, sqrt)
//  và toán tử % (mod) dưới dạng trung tố.
// ============================================================

string postfixToInfix(const string& postfix)
{
    Stack<string> st;
    istringstream iss(postfix);
    string token;

    while (iss >> token)
    {
        if (isUnaryOperator(token))
        {
            if (st.getSize() < 1)
                throw runtime_error("Bieu thuc hau to khong hop le");

            string a = st.pop().value();
            string expr;
            if (token == "~")
                expr = "(-" + a + ")";
            else if (token == "!")
                expr = "(" + a + "!)";
            else if (token == "sqrt")
                expr = "sqrt(" + a + ")";

            st.push(expr);
        }
        else if (isBinaryOperator(token))
        {
            if (st.getSize() < 2)
                throw runtime_error("Bieu thuc hau to khong hop le");

            // Sửa thứ tự: pop ra TRƯỚC là toán hạng phải (b), pop SAU là trái (a)
            string b = st.pop().value();
            string a = st.pop().value();
            string expr = "(" + a + " " + token + " " + b + ")";
            st.push(expr);
        }
        else
        {
            st.push(token); // số hạng, đẩy vào stack
        }
    }

    if (st.getSize() != 1)
        throw runtime_error("Bieu thuc hau to khong hop le");

    return st.pop().value();
}
