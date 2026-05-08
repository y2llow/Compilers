int f(int x) {
    int result = x;
    if (x > 0) {
        int result = x + 10;
        result = result + 1;
    }
    return result;
}

int main() {
    return f(3);
}
