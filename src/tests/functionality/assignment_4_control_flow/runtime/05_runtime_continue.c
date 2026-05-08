int main() {
    int x = 0;
    int sum = 0;

    while (x < 5) {
        x = x + 1;

        if (x == 3) {
            continue;
        }

        sum = sum + x;
    }

    return sum;
}
