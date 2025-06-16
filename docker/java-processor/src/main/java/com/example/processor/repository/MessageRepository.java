package com.example.processor.repository;

import com.example.processor.model.MessageData;
import io.micrometer.core.instrument.Counter;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Repository;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Key;
import software.amazon.awssdk.enhanced.dynamodb.TableSchema;

import javax.annotation.PostConstruct;
import java.time.Instant;
import java.time.temporal.ChronoUnit;

@Repository
public class MessageRepository {

    private final DynamoDbEnhancedClient dynamoDbEnhancedClient;
    private DynamoDbTable<MessageData> table;

    @Value("${aws.dynamodb.table-name}")
    private String tableName;
    
    @Autowired
    private Counter dynamoDbInsertCounter;
    
    @Autowired
    private Counter dynamoDbDeleteCounter;
    
    @Autowired
    private Counter dynamoDbErrorCounter;

    public MessageRepository(DynamoDbEnhancedClient dynamoDbEnhancedClient) {
        this.dynamoDbEnhancedClient = dynamoDbEnhancedClient;
    }

    @PostConstruct
    public void init() {
        this.table = dynamoDbEnhancedClient.table(tableName, TableSchema.fromBean(MessageData.class));
    }

    public MessageData save(MessageData messageData) {
        // Definir o tempo de expiração (TTL) para 7 dias a partir de agora
        if (messageData.getExpiryTime() == null) {
            messageData.setExpiryTime(Instant.now().plus(7, ChronoUnit.DAYS).getEpochSecond());
        }
        
        // Registrar o momento do processamento
        messageData.setProcessedAt(Instant.now());
        
        try {
            // Salvar no DynamoDB
            table.putItem(messageData);
            // Incrementar contador de inserções
            dynamoDbInsertCounter.increment();
            return messageData;
        } catch (Exception e) {
            // Incrementar contador de erros
            dynamoDbErrorCounter.increment();
            throw e;
        }
    }

    public void delete(String customerId, String recordId) {
        Key key = Key.builder()
                .partitionValue(customerId)
                .sortValue(recordId)
                .build();
        
        try {        
            table.deleteItem(key);
            // Incrementar contador de deleções
            dynamoDbDeleteCounter.increment();
        } catch (Exception e) {
            // Incrementar contador de erros
            dynamoDbErrorCounter.increment();
            throw e;
        }
    }

    public MessageData findById(String customerId, String recordId) {
        Key key = Key.builder()
                .partitionValue(customerId)
                .sortValue(recordId)
                .build();
        
        try {
            return table.getItem(key);
        } catch (Exception e) {
            // Incrementar contador de erros
            dynamoDbErrorCounter.increment();
            throw e;
        }
    }
}
