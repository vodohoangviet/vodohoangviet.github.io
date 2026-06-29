#pragma once
#include <string>
#include <set>
using namespace std;

// ============================================================
//  KIỂM TRA TOKEN SỐ / TOÁN TỬ
// ============================================================

// kiểm tra ký tự có phải chữ số
inline bool my_isdigit(unsigned char c)
{
    return c >= '0' && c <= '9';
}

// Danh sách toán tử hai ngôi được hỗ trợ
inline bool isBinaryOperator(const string& tok)
{
    static const set<string> ops = { "+", "-", "*", "/", "^", "%" };
    return ops.count(tok) > 0;
}

// Danh sách toán tử một ngôi được hỗ trợ (đứng sau toán hạng trong RPN)
// "~" : đổi dấu (vd: 5 ~  => -5)
// "!" : giai thừa (vd: 5 !  => 120)
// "sqrt" : căn bậc hai (vd: 9 sqrt => 3)
inline bool isUnaryOperator(const string& tok)
{
    static const set<string> ops = { "~", "!", "sqrt" };
    return ops.count(tok) > 0;
}

// kiểm tra token có phải số hợp lệ (integer, float, hoặc dạng khoa học 1.5e-3)
bool isNumberToken(const string& tok)
{
    if (tok.empty())
        return false;

    bool seenDigit = false, seenDot = false, seenExp = false;
    size_t i = 0;

    // dấu ở đầu
    if (tok[i] == '+' || tok[i] == '-')
        i++;

    for (; i < tok.size(); ++i)
    {
        char c = tok[i];

        if (c == '.')
        {
            if (seenDot || seenExp)
                return false;
            seenDot = true;
        }
        else if (c == 'e' || c == 'E')
        {
            if (seenExp || !seenDigit)
                return false;
            seenExp = true;
            // cho phép dấu ngay sau e/E
            if (i + 1 < tok.size() && (tok[i + 1] == '+' || tok[i + 1] == '-'))
                i++;
        }
        else if (my_isdigit((unsigned char)c))
        {
            seenDigit = true;
        }
        else
        {
            return false;
        }
    }
    return seenDigit;
}
