#include "math.h"
#include "utils.h"
#include "20_nested_include.h"

int main() {
    int a = clamp(square(2), 0, 10);
    int b = multiply(add(1, 2), 3);
    return a + b;
}
