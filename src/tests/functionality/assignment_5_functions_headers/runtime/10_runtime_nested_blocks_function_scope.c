int f(int x) {
    int y = x;
    {
        int y = 100;
        y = y + 1;
    }
    return y;
}
int main() { return f(7); }
