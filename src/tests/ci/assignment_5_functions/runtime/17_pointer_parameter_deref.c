int get(int* p) {
    return *p;
}

int main() {
    int x = 42;
    return get(&x);
}