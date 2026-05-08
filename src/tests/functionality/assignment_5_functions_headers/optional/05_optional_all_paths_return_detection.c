int maybe(int x) {
    if (x > 0) {
        return 1;
    } else {
        x = x + 1;
    }
}
int main() { return maybe(1); }
