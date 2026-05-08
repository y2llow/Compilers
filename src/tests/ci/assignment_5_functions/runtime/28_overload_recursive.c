// src/tests/ci/assignment_5_functions/runtime/28_overload_recursive.c

int sum(int n) {
    if (n <= 0) {
        return 0;
    }
    return n + sum(n - 1);
}

float sum(float n) {
    if (n <= 0.0) {
        return 0.0;
    }
    return n + sum(n - 1.0);
}

int main() {
    int   r1 = sum(5);
    float r2 = sum(3.0);
    return r1;
}