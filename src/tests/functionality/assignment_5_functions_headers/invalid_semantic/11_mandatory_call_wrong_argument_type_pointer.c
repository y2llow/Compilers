void set_value(int *p) {
    *p = 1;
    return;
}

int main() {
    int x = 0;
    set_value(x);
    return x;
}
