#pragma once
#include "stack.h"
#include "queue.h"
#include "validNum.h"
#include "myPow.h"
#include <optional>
#include <stdexcept>
#include <cmath>
using namespace std;

// ============================================================
//  ĐÁNH GIÁ BIỂU THỨC RPN (Reverse Polish Notation)
//
//  BUG ĐÃ SỬA: code cũ pop b trước rồi gán "aOpt = pop()" sau, nhưng lại
//  gọi biến là `a` cho giá trị pop ĐẦU và `b` cho giá trị pop SAU — tức
//  là bị NGƯỢC. Với "5 3 -", thứ tự đúng phải là a=5 (pop sau, nằm dưới),
//  b=3 (pop trước, nằm trên) => a - b = 2. Code cũ tính ra -2 (sai).
//  Bản này sửa lại đúng thứ tự stack-based evaluation chuẩn.
//
//  TÍNH NĂNG MỚI:
//   - % : phép chia lấy phần dư (mod)
//   - ~ : đổi dấu (toán tử 1 ngôi, áp dụng cho số trên cùng của stack)
//   - ! : giai thừa (toán tử 1 ngôi)
//   - sqrt : căn bậc hai (toán tử 1 ngôi)
// ============================================================
double evaluateRPN(Queue q)
{
    Stack<double> st;

    while (q.getSize() > 0)
    {
        optional<string> tokOpt = q.pop();
        if (!tokOpt.has_value())
            break;
        string tok = tokOpt.value();

        if (isNumberToken(tok))
        {
            try
            {
                double v = stod(tok);
                st.push(v);
            }
            catch (...)
            {
                throw runtime_error("Token khong phai la mot so hop le: " + tok);
            }
        }
        else if (isUnaryOperator(tok))
        {
            optional<double> aOpt = st.pop();
            if (!aOpt.has_value())
                throw runtime_error("Thieu toan hang cho toan tu mot ngoi: " + tok);
            double a = aOpt.value();
            double res = 0.0;

            if (tok == "~")
                res = -a;
            else if (tok == "!")
                res = myFactorial(a);
            else if (tok == "sqrt")
                res = mySqrt(a);

            st.push(res);
        }
        else if (isBinaryOperator(tok))
        {
            // Quy ước stack chuẩn: phần tử pop ra TRƯỚC là toán hạng bên PHẢI (b),
            // phần tử pop ra SAU là toán hạng bên TRÁI (a).
            optional<double> bOpt = st.pop();
            optional<double> aOpt = st.pop();
            if (!aOpt.has_value() || !bOpt.has_value())
                throw runtime_error("Thieu toan hang cho toan tu: " + tok);

            double a = aOpt.value();
            double b = bOpt.value();
            double res = 0.0;

            if (tok == "+")
                res = a + b;
            else if (tok == "-")
                res = a - b;
            else if (tok == "*")
                res = a * b;
            else if (tok == "/")
            {
                if (b == 0)
                    throw runtime_error("khong the chia cho 0");
                res = a / b;
            }
            else if (tok == "%")
            {
                if (b == 0)
                    throw runtime_error("khong the chia lay du cho 0");
                res = fmod(a, b);
            }
            else if (tok == "^")
            {
                res = myPow(a, b);
            }

            st.push(res);
        }
        else
        {
            throw runtime_error("Toan tu khong hop le: " + tok);
        }
    }

    // Lấy kết quả cuối cùng
    if (st.getSize() != 1)
        throw runtime_error("Bieu thuc khong hop le!");

    optional<double> resOpt = st.pop();
    return resOpt.value();
}
