int compute(int x) {
    if (x > 0) {
        return x * 2;
    }
    // missing else branch or explicit return
}

int main() {
    return compute(5);
}