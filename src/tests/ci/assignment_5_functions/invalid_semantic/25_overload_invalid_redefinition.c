// src/tests/ci/assignment_5_functions/invalid_semantic/25_overload_invalid_redefinition.c

int add(int x, int y) {
    return x + y;
}

int add(int x, int y) {
    return x + y + 1;
}

int main() {
    return add(1, 2);
}