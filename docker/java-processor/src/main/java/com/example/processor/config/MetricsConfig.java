package com.example.processor.config;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.DescribeTableRequest;
import software.amazon.awssdk.services.dynamodb.model.DescribeTableResponse;

import java.util.concurrent.atomic.AtomicInteger;

@Configuration
public class MetricsConfig {

    private final AtomicInteger dynamoDbItemsCount = new AtomicInteger(0);
    
    @Value("${aws.dynamodb.table-name}")
    private String tableName;

    @Bean
    public Counter dynamoDbInsertCounter(MeterRegistry registry) {
        return Counter.builder("dynamodb_operation_total")
                .tag("operation", "INSERT")
                .description("Number of INSERT operations performed on DynamoDB")
                .register(registry);
    }

    @Bean
    public Counter dynamoDbDeleteCounter(MeterRegistry registry) {
        return Counter.builder("dynamodb_operation_total")
                .tag("operation", "DELETE")
                .description("Number of DELETE operations performed on DynamoDB")
                .register(registry);
    }

    @Bean
    public Counter dynamoDbErrorCounter(MeterRegistry registry) {
        return Counter.builder("dynamodb_operation_error_total")
                .description("Number of errors during DynamoDB operations")
                .register(registry);
    }

    @Bean
    public Counter sqsMessageReceivedCounter(MeterRegistry registry) {
        return Counter.builder("sqs_message_received_total")
                .description("Number of messages received from SQS")
                .register(registry);
    }

    @Bean
    public Counter sqsMessageErrorCounter(MeterRegistry registry) {
        return Counter.builder("sqs_message_error_total")
                .description("Number of errors processing SQS messages")
                .register(registry);
    }

    @Bean
    public Gauge dynamoDbItemsCountGauge(MeterRegistry registry, DynamoDbClient dynamoDbClient) {
        // Schedule a task to update the item count periodically
        updateDynamoDbItemCount(dynamoDbClient);
        
        return Gauge.builder("dynamodb_items_count", dynamoDbItemsCount::get)
                .description("Current number of items in the DynamoDB table")
                .register(registry);
    }
    
    private void updateDynamoDbItemCount(DynamoDbClient dynamoDbClient) {
        try {
            DescribeTableRequest request = DescribeTableRequest.builder()
                    .tableName(tableName)
                    .build();
            
            DescribeTableResponse response = dynamoDbClient.describeTable(request);
            if (response.table().itemCount() != null) {
                dynamoDbItemsCount.set(response.table().itemCount().intValue());
            }
        } catch (Exception e) {
            // Log error but don't fail
            System.err.println("Failed to update DynamoDB item count: " + e.getMessage());
        }
        
        // Schedule next update in 30 seconds
        new Thread(() -> {
            try {
                Thread.sleep(30000);
                updateDynamoDbItemCount(dynamoDbClient);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();
    }
}
