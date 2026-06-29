#pragma once
#include <stdexcept>
#include <string>
#include <cmath>
using namespace std;

// ============================================================
//  CÁC HÀM TOÁN HỌC TỰ XÂY DỰNG (không dùng pow/log/sqrt có sẵn của <cmath>
//  cho hàm chính, để giữ đúng tinh thần "tự cài thuật toán" của project gốc)
// ============================================================

// HÀM MŨ e^x  (khai triển Taylor)
double myExp(double x)
{
    double term = 1.0; // phần tử hiện tại trong chuỗi
    double sum = 1.0;  // tổng ban đầu = 1
    for (int n = 1; n < 100; ++n)
    { // tăng từ 50 -> 100 vòng để chính xác hơn với |x| lớn
        term *= x / n;
        sum += term;
        // Bug cũ: vòng lặp luôn chạy đúng 50 lần dù x lớn hay nhỏ.
        // Thêm điều kiện dừng sớm khi số hạng đã quá nhỏ, đỡ tính dư.
        if (term < 1e-18 && term > -1e-18 && n > 10)
            break;
    }
    return sum;
}

// HÀM LOGARIT ln(x)
double myLn(double x)
{
    if (x <= 0.0)
        throw runtime_error("logarit cua so khong duong!");
    if (!isfinite(x))
        throw runtime_error("logarit cua gia tri khong huu han!");

    // Đưa x về vùng gần 1 để chuỗi hội tụ tốt
    int k = 0;
    const double e = 2.718281828459045;
    const int MAX_SCALE_STEPS = 10000; // BUG CŨ: vòng while có thể chạy "vô hạn"
                                        // về lý thuyết nếu x là giá trị bất thường (inf, rất lớn).
                                        // Thêm giới hạn số vòng để đảm bảo luôn dừng.
    int steps = 0;
    while (x > 2.0)
    {
        x /= e;
        k++;
        if (++steps > MAX_SCALE_STEPS)
            throw runtime_error("gia tri qua lon, khong the tinh logarit!");
    }
    steps = 0;
    while (x < 0.5)
    {
        x *= e;
        k--;
        if (++steps > MAX_SCALE_STEPS)
            throw runtime_error("gia tri qua nho, khong the tinh logarit!");
    }

    // Sử dụng công thức: ln(x) = 2 * (y + y^3/3 + y^5/5 + ...)
    double y = (x - 1) / (x + 1);
    double y2 = y * y;
    double term = y;
    double sum = 0.0;

    for (int n = 1; n < 60; n += 2)
    {
        sum += term / n;
        term *= y2;
    }

    return 2 * sum + k;
}

// HÀM CĂN BẬC HAI (phương pháp Newton-Raphson)
double mySqrt(double x)
{
    if (x < 0.0)
        throw runtime_error("khong the tinh can bac hai cua so am!");
    if (x == 0.0)
        return 0.0;

    double guess = x;
    for (int i = 0; i < 100; ++i)
    {
        double next = 0.5 * (guess + x / guess);
        if (next == guess) break; // đã hội tụ, dừng sớm
        guess = next;
    }
    return guess;
}

// HÀM GIAI THỪA (chỉ áp dụng cho số nguyên không âm)
double myFactorial(double n)
{
    if (n < 0.0)
        throw runtime_error("giai thua cua so am khong hop le!");
    if (n != (long long)n)
        throw runtime_error("giai thua chi ap dung cho so nguyen!");
    if (n > 170) // > 170! vượt quá double, tránh inf âm thầm
        throw runtime_error("gia tri qua lon de tinh giai thua!");

    long long ni = (long long)n;
    double result = 1.0;
    for (long long i = 2; i <= ni; ++i)
        result *= (double)i;
    return result;
}

// HÀM MŨ a^b
double myPow(double base, double exp)
{
    // Trường hợp cơ bản
    if (base == 0.0)
    {
        if (exp <= 0.0)
            throw runtime_error("0 mu <= 0 khong hop le!");
        return 0.0;
    }

    // Nếu cơ số âm và mũ không nguyên → không xác định trong R
    if (base < 0.0 && exp != (long long)exp)
        throw runtime_error("co so am voi mu thuc khong hop le!");

    // Dùng công thức: a^b = e^(b * ln(|a|))
    double ln_base = myLn(base > 0 ? base : -base);
    double result = myExp(exp * ln_base);

    // Nếu cơ số âm và mũ là số nguyên lẻ → đổi dấu
    if (base < 0.0 && (((long long)exp) % 2 != 0))
        result = -result;

    return result;
}
