package com.example.processor.config;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.DescribeTableRequest;
import software.amazon.awssdk.services.dynamodb.model.DescribeTableResponse;
import software.amazon.awssdk.services.dynamodb.model.TableDescription;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class MetricsConfigTest {

    private MetricsConfig metricsConfig;
    private MeterRegistry meterRegistry;

    @Mock
    private DynamoDbClient dynamoDbClient;

    @BeforeEach
    void setUp() {
        meterRegistry = new SimpleMeterRegistry();
        metricsConfig = new MetricsConfig();
    }

    @Test
    void testDynamoDbInsertCounter() {
        // Act
        Counter counter = metricsConfig.dynamoDbInsertCounter(meterRegistry);
        
        // Assert
        assertNotNull(counter);
        assertEquals("dynamodb_operation_total", counter.getId().getName());
        assertEquals("Number of INSERT operations performed on DynamoDB", counter.getId().getDescription());
    }

    @Test
    void testDynamoDbDeleteCounter() {
        // Act
        Counter counter = metricsConfig.dynamoDbDeleteCounter(meterRegistry);
        
        // Assert
        assertNotNull(counter);
        assertEquals("dynamodb_operation_total", counter.getId().getName());
        assertEquals("Number of DELETE operations performed on DynamoDB", counter.getId().getDescription());
    }

    @Test
    void testDynamoDbErrorCounter() {
        // Act
        Counter counter = metricsConfig.dynamoDbErrorCounter(meterRegistry);
        
        // Assert
        assertNotNull(counter);
        assertEquals("dynamodb_operation_error_total", counter.getId().getName());
        assertEquals("Number of errors during DynamoDB operations", counter.getId().getDescription());
    }

    @Test
    void testSqsMessageReceivedCounter() {
        // Act
        Counter counter = metricsConfig.sqsMessageReceivedCounter(meterRegistry);
        
        // Assert
        assertNotNull(counter);
        assertEquals("sqs_message_received_total", counter.getId().getName());
        assertEquals("Number of messages received from SQS", counter.getId().getDescription());
    }

    @Test
    void testSqsMessageErrorCounter() {
        // Act
        Counter counter = metricsConfig.sqsMessageErrorCounter(meterRegistry);
        
        // Assert
        assertNotNull(counter);
        assertEquals("sqs_message_error_total", counter.getId().getName());
        assertEquals("Number of errors processing SQS messages", counter.getId().getDescription());
    }

    @Test
    void testDynamoDbItemsCountGauge() {
        // Arrange
        TableDescription tableDescription = TableDescription.builder()
                .itemCount(100L)
                .build();
        
        DescribeTableResponse response = DescribeTableResponse.builder()
                .table(tableDescription)
                .build();
        
        when(dynamoDbClient.describeTable(any(DescribeTableRequest.class))).thenReturn(response);
        
        // Act
        Gauge gauge = metricsConfig.dynamoDbItemsCountGauge(meterRegistry, dynamoDbClient);
        
        // Assert
        assertNotNull(gauge);
        assertEquals("dynamodb_items_count", gauge.getId().getName());
        assertEquals("Current number of items in the DynamoDB table", gauge.getId().getDescription());
    }
}
