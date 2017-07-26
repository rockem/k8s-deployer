package com.agt.greeter;

public class Greeting {

    private static final String template = "Hello, %s";
    private final String name;

    public Greeting(String name) {
        this.name = name == null ? "World" : name;
    }

    public String getContent() {
        return String.format(template, name);
    }
}