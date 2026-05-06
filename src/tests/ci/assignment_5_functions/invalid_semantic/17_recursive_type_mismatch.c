int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2.5); 
}

int main() {
    return fibonacci(10);
}