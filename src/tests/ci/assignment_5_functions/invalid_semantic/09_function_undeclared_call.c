int add(int a, int b);  // Forward declaration only

int main() {
    int x = add(5, 3);  // Function not defined anywhere
    return x;
}