void write_const(const int *p) {
    *p = 4;
    return;
}

int main() {
    int x = 0;
    write_const(&x);
    return x;
}
