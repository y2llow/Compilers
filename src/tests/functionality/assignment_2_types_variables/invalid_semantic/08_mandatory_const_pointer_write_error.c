int main() {
    int x = 1;

    const int* p = &x;
    *p = 5;

    return x;
}
