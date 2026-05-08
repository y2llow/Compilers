/*
 * Symbol table showcase
 * This file is made to generate a rich symbol table visualization.
 */

#define START_VALUE 10
#define TRUE 1
#define FALSE 0

typedef int MyInt;
typedef MyInt* MyIntPtr;

enum Status {
    STATUS_OK = 0,
    STATUS_FAIL = 1
};

struct Point {
    int x;
    int y;
};

struct Node {
    int value;
    struct Node* next;
};

/* Global variables */
int global_counter = START_VALUE;
const int global_limit = 100;
float global_ratio = 2.5;
char global_letter = 'A';

int global_values[3] = {1, 2, 3};
int* global_ptr;

/* Forward declarations */
int add(int a, int b);
int add(int a, int b, int c);
float add(float a, float b);

void update_counter(int amount);
int sum_array(int* arr, int size);
int use_point(struct Point* p);
int scoped_example(int value);

/* Overload by parameter count */
int add(int a, int b) {
    int result = a + b;
    return result;
}

int add(int a, int b, int c) {
    int result = a + b + c;
    return result;
}

/* Overload by parameter type */
float add(float a, float b) {
    float result = a + b;
    return result;
}

/* Void function with pointer/global usage */
void update_counter(int amount) {
    int local_copy = global_counter;
    local_copy = local_copy + amount;
    global_counter = local_copy;
}

/* Function with array passed as pointer */
int sum_array(int* arr, int size) {
    int i = 0;
    int total = 0;

    while (i < size) {
        int current = arr[i];
        total = total + current;
        i = i + 1;
    }

    return total;
}

/* Function with struct pointer and arrow access */
int use_point(struct Point* p) {
    int result = p->x + p->y;
    return result;
}

/* Function with nested scopes and shadowing */
int scoped_example(int value) {
    int result = value;

    if (value > 0) {
        int inner_value = value + 1;
        result = inner_value;

        {
            int deeply_nested = inner_value + result;
            int value = deeply_nested;
            result = value;
        }
    } else {
        int negative_value = 0 - value;
        result = negative_value;
    }

    return result;
}

int main() {
    MyInt a = 1;
    MyInt b = 2;
    MyIntPtr ptr = &a;

    struct Point p;
    struct Node node;

    int result1 = 0;
    int result2 = 0;
    float result3 = 0.0;
    int array_sum = 0;
    int point_sum = 0;
    int scoped = 0;
    int status = STATUS_OK;

    p.x = 4;
    p.y = 5;

    node.value = 42;
    node.next = 0;

    result1 = add(a, b);
    result2 = add(a, b, 3);
    result3 = add(1.5, 2.5);

    update_counter(result1);

    array_sum = sum_array(global_values, 3);
    point_sum = use_point(&p);
    scoped = scoped_example(result2);

    if (status == STATUS_OK) {
        int final_result = array_sum + point_sum + scoped;
        return final_result;
    } else {
        return STATUS_FAIL;
    }
}