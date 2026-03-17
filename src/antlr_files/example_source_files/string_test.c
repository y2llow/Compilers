int main() {
    // Test 1: Simple string assignment to char*
    char* msg = "Hello";

    // Test 2: String with escape sequences
    char* newline_msg = "Hello\nWorld";
    char* tab_msg = "Column1\tColumn2";
    char* quote_msg = "He said \"Hi\"";
    char* backslash_msg = "Path: C:\\Users\\test";

    // Test 3: Empty string
    char* empty = "";

    // Test 4: String assigned to char array
    char buf[50] = "test";
    char name[100] = "John Doe";
    char path[200] = "C:\\Program Files\\App";

    // Test 5: Multiple string variables
    char* greeting1 = "Good morning";
    char* greeting2 = "Good afternoon";
    char* greeting3 = "Good evening";

    // Test 6: Strings with various escape sequences
    char* newlines = "Line 1\nLine 2\nLine 3";
    char* mixed = "Name:\tJohn\nAge:\t30";

    // Test 7: Array of different sizes with strings
    char small[10] = "hi";
    char medium[50] = "medium sized text";
    char large[200] = "this is a much longer string that fits in a large buffer";

    // Test 8: String in expressions (later for printf)
    char* format_str = "Number: %d";

    return 0;
}