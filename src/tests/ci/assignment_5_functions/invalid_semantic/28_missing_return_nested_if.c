int f(int x, int y) {
    if (x > 0) {
        if (y > 0) {
            return 1;
        }
    } else {
        return 2;
    }
}

int main() {
    return f(1, 0);
}