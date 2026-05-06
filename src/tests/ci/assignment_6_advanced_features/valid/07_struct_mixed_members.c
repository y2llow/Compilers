#include <stdio.h>

struct Person {
    char name[20];
    int age;
    float height;
};

int main() {
    struct Person p;
    p.age = 30;
    p.height = 1.75f;
    printf("%d\n", p.age);
    return 0;
}