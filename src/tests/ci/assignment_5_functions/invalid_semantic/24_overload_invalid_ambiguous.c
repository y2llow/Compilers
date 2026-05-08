// src/tests/ci/assignment_5_functions/invalid_semantic/24_overload_invalid_ambiguous.c

int foo(int x, float y) {
    return x;
}

float foo(float x, int y) {
    return y;
}

int main() {
    int result = foo(1, 2);
    return result;
}