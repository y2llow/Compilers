int global_value = 0;

void set_global(int value) {
    global_value = value;
    return;
}

int main() {
    set_global(9);
    return global_value;
}
