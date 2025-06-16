package com.example.processor.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbBean;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbPartitionKey;
import software.amazon.awssdk.enhanced.dynamodb.mapper.annotations.DynamoDbSortKey;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@DynamoDbBean
public class MessageData {

    private String customerId;  // Renomeado de id para customerId
    private String recordId;    // Renomeado de timestamp para recordId
    private String operation;
    private String name;
    private String email;
    private String address;
    private String phone;
    private Long expiryTime;
    private Instant processedAt;

    @DynamoDbPartitionKey
    public String getCustomerId() {
        return customerId;
    }

    @DynamoDbSortKey
    public String getRecordId() {
        return recordId;
    }
}
