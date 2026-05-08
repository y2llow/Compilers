int main() {
    int x = 1;
    int y = 2;

    const int* p = &x;
    p = &y;       // dit moet toegestaan zijn

    return *p;    // 2
}