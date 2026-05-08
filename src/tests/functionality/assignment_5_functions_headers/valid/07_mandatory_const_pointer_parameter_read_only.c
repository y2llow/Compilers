int read_const(const int *p) {
    return *p;
}

int main() {
    int x = 8;
    return read_const(&x);
}
