int global_counter = 3;

void add_to_pointer(int* target, int amount) {
    int local_amount = amount + global_counter;
    *target = *target + local_amount;
}

int compute_delta(int base) {
    int result = base;

    {
        int result = base + 2;

        if (result > 5) {
            int inner = result * 2;
            return inner - base;
        }
    }

    return result;
}

int main() {
    int value = 10;
    int delta = compute_delta(value);

    add_to_pointer(&value, delta);

    if (value > 30) {
        int bonus = 4;
        value = value + bonus;
    } else {
        int penalty = 2;
        value = value - penalty;
    }

    return value;
}