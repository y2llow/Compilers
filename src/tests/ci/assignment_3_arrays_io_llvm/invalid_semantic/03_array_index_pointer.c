int main() {
    int values[3] = {1, 2, 3};
    int* p = &values[0];
    return values[p];
}
