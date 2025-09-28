node Hello {
    has msg: str = "Hello, Jac!";
}

with entry {
    hello_node = Hello();
    print(hello_node.msg);
}


