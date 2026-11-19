package com.aiproductstudio.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class HttpClientConfig {
    @Bean
    RestClient agentRestClient(RestClient.Builder builder,
                               @Value("${studio.agent-service-url:http://localhost:8001}") String baseUrl) {
        return builder.baseUrl(baseUrl).build();
    }
}
