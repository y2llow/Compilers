void inc(int *p) {
    *p = *p + 1;
    return;
}

int main() {
    int x = 4;
    inc(&x);
    return x;
}
