int foo() {
    int x = 5;
    return &x;
}

int main() {
    return foo();
}