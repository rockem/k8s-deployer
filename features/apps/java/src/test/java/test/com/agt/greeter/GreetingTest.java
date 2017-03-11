package test.com.agt.greeter;

import com.agt.greeter.Greeting;
import org.junit.Test;

import static org.hamcrest.core.Is.is;
import static org.junit.Assert.*;

public class GreetingTest {


    @Test
    public void shouldGreetWorldByDefault() throws Exception {
        assertThat(new Greeting(null).getContent(), is("Hello, World"));
    }

    @Test
    public void shouldGreetSpecifiedName() throws Exception {
        assertThat(new Greeting("Kuku").getContent(), is("Hello, Kuku"));
    }
}