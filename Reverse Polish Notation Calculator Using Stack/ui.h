#pragma once
#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <sstream>
#include <iomanip>
using namespace std;

// ============================================================
//  MÀU SẮC (ANSI escape codes - hoạt động trên Windows 10+,
//  Linux, macOS terminal hiện đại)
// ============================================================
#define GREEN     "\x1b[32m"
#define RED       "\x1b[31m"
#define YELLOW    "\x1b[33m"
#define BLUE      "\x1b[34m"
#define CYAN      "\x1b[36m"
#define MAGENTA   "\x1b[35m"
#define GRAY      "\x1b[90m"
#define BOLD      "\x1b[1m"
#define RESET     "\x1b[0m"
#define UNDERLINE "\x1b[4m"

// ============================================================
//  BOX-DRAWING (Unicode) để vẽ khung đẹp cho menu / bảng
// ============================================================
namespace ui
{
    const string H = "\u2500"; // ─
    const string V = "\u2502"; // │
    const string TL = "\u250C"; // ┌
    const string TR = "\u2510"; // ┐
    const string BL = "\u2514"; // └
    const string BR = "\u2518"; // ┘
    const string ML = "\u251C"; // ├
    const string MR = "\u2524"; // ┤
    const string MT = "\u252C"; // ┬
    const string MB = "\u2534"; // ┴

    // Lặp một chuỗi UTF-8 n lần
    inline string repeat(const string& s, int n)
    {
        string out;
        out.reserve(s.size() * n);
        for (int i = 0; i < n; ++i) out += s;
        return out;
    }

    // Vẽ đường kẻ ngang đầy đủ độ rộng `width`, có nối ở 2 đầu
    inline string line(int width, const string& left, const string& right)
    {
        return left + repeat(H, width) + right;
    }

    // Vẽ tiêu đề căn giữa trong khung rộng `width`
    inline void title(const string& text, int width, const string& color = CYAN)
    {
        // Đếm theo ký tự hiển thị (xấp xỉ, đủ cho tiếng Việt không dấu)
        int textLen = (int)text.size();
        int pad = width - textLen;
        int left = pad / 2 > 0 ? pad / 2 : 0;
        int right = pad - left > 0 ? pad - left : 0;
        cout << V << string(left, ' ') << color << BOLD << text << RESET
             << string(right, ' ') << V << "\n";
    }

    // Vẽ một dòng nội dung căn trái, đệm đủ độ rộng
    inline void row(const string& text, int width, const string& color = "")
    {
        int textLen = (int)text.size();
        int pad = width - textLen;
        if (pad < 0) pad = 0;
        cout << V << " " << color << text << RESET << string(pad - 1 > 0 ? pad - 1 : 0, ' ') << V << "\n";
    }

    // Khung mở
    inline void boxTop(int width) { cout << YELLOW << line(width, TL, TR) << RESET << "\n"; }
    inline void boxMid(int width) { cout << YELLOW << line(width, ML, MR) << RESET << "\n"; }
    inline void boxBottom(int width) { cout << YELLOW << line(width, BL, BR) << RESET << "\n"; }

    // ============================================================
    //  Thanh tiến trình (progress bar) - không block lâu, mượt hơn Sleep cứng
    // ============================================================
    inline void progressBar(const string& label, int durationMs = 400, int steps = 20)
    {
        cout << CYAN;
        int stepDelay = durationMs / steps;
        for (int i = 1; i <= steps; ++i)
        {
            int percent = i * 100 / steps;
            int filled = i;
            cout << "\r" << label << " [" << string(filled, '#') << string(steps - filled, '-') << "] " << percent << "%" << flush;
            this_thread::sleep_for(chrono::milliseconds(stepDelay));
        }
        cout << "\r" << string(label.size() + steps + 10, ' ') << "\r" << flush << RESET;
    }

    // Định dạng double gọn gàng (bỏ số 0 thừa ở cuối)
    inline string fmt(double v, int precision = 6)
    {
        ostringstream oss;
        oss << fixed << setprecision(precision) << v;
        string s = oss.str();
        // bỏ số 0 dư ở cuối, giữ lại ít nhất 1 số sau dấu .
        size_t dot = s.find('.');
        if (dot != string::npos)
        {
            size_t lastNonZero = s.find_last_not_of('0');
            if (lastNonZero == dot) lastNonZero++; // giữ "x.0"
            s.erase(lastNonZero + 1);
        }
        return s;
    }
}
