int main() {
    int x = 1;
    int y = 2;
    const int* p = &x;
    p = &y;
    return y;
}
