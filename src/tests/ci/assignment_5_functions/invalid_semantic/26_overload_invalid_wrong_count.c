// src/tests/ci/assignment_5_functions/invalid_semantic/26_overload_invalid_wrong_count.c

int add(int x, int y) {
    return x + y;
}

int main() {
    return add(1, 2, 3);
}