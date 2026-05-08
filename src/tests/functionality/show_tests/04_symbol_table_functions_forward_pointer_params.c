int read_value(const int* ptr);
void write_value(int* ptr, int new_value);
int combine(int left, int right);

int global_seed = 5;

int read_value(const int* ptr) {
    int local_copy = *ptr;
    return local_copy + global_seed;
}

void write_value(int* ptr, int new_value) {
    int adjusted = new_value + global_seed;
    *ptr = adjusted;
}

int combine(int left, int right) {
    int result = left + right;

    {
        int left = result * 2;
        result = left - right;
    }

    return result;
}

int main() {
    int storage = 4;
    int before = read_value(&storage);

    write_value(&storage, before);

    int after = read_value(&storage);
    int result = combine(before, after);

    return result;
}