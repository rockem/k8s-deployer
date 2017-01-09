package com.agt.greeter;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Value;

@RestController
public class GreetingController {

    @Value("${greeting}")
    private String greeting;
    @Value("${greeting2}")
    private String greeting2;

    @RequestMapping("/greeting")
    public String greeting() {
        return greeting;
    }

    @RequestMapping("/greeting2")
    public String greeting2() {
        return greeting2;
    }

}