#define LIMIT 5

int square(int x) {
    return x * x;
}

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}

int mix(int a, int b) {
    int result = square(a);
    result = result + factorial(b);

    if (result > 100) {
        result = result - 10;
    } else {
        result = result + 10;
    }

    return result;
}

int main() {
    int values[5] = {1, 2, 3, 4, 5};
    int index = 0;
    int total = 0;

    while (index < LIMIT) {
        int current = values[index];
        int partial = mix(current, index);

        if (partial > 20) {
            total = total + partial;
        } else {
            total = total + square(partial);
        }

        index = index + 1;
    }

    return total;
}