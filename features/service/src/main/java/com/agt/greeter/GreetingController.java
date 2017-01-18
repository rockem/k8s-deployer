package com.agt.greeter;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Value;

@RestController
public class GreetingController {

    @Value("${internalGreeting}")
    private String internalGreeting;
    @Value("${globalName}")
    private String globalName;

    @RequestMapping("/greeting")
    public String greeting() {
        return internalGreeting + ' ' + globalName;
    }
}