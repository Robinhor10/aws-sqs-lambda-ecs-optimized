package com.example.processor.repository;

import com.example.processor.model.MessageData;
import io.micrometer.core.instrument.Counter;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbTable;
import software.amazon.awssdk.enhanced.dynamodb.Key;

import java.time.Instant;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class MessageRepositoryTest {

    @Mock
    private DynamoDbEnhancedClient dynamoDbEnhancedClient;
    
    @Mock
    private DynamoDbTable<MessageData> table;
    
    @Mock
    private Counter dynamoDbInsertCounter;
    
    @Mock
    private Counter dynamoDbDeleteCounter;
    
    @Mock
    private Counter dynamoDbErrorCounter;
    
    private MessageRepository messageRepository;
    private MessageData messageData;
    private String customerId;
    private String recordId;

    @BeforeEach
    void setUp() {
        // Não mockamos o método table() diretamente para evitar problemas com tipos genéricos
        
        messageRepository = new MessageRepository(dynamoDbEnhancedClient);
        
        // Usar reflection para injetar os mocks
        ReflectionTestUtils.setField(messageRepository, "tableName", "messages-table");
        ReflectionTestUtils.setField(messageRepository, "table", table);
        ReflectionTestUtils.setField(messageRepository, "dynamoDbInsertCounter", dynamoDbInsertCounter);
        ReflectionTestUtils.setField(messageRepository, "dynamoDbDeleteCounter", dynamoDbDeleteCounter);
        ReflectionTestUtils.setField(messageRepository, "dynamoDbErrorCounter", dynamoDbErrorCounter);
        
        customerId = UUID.randomUUID().toString();
        recordId = Instant.now().toString();
        
        messageData = MessageData.builder()
                .customerId(customerId)
                .recordId(recordId)
                .name("Test User")
                .email("test@example.com")
                .operation("INSERT")
                .build();
    }

    @Test
    void testSaveIncrementsDynamoDbInsertCounter() {
        // Arrange - não precisamos mockar o comportamento do table.putItem
        // pois estamos apenas verificando as chamadas aos contadores
        
        // Act
        MessageData result = messageRepository.save(messageData);
        
        // Assert
        assertNotNull(result);
        verify(dynamoDbInsertCounter, times(1)).increment();
        verify(dynamoDbErrorCounter, never()).increment();
    }
    
    @Test
    void testSaveHandlesExceptionAndIncrementsErrorCounter() {
        // Arrange - simulamos uma exceção ao acessar a tabela
        doThrow(new RuntimeException("Test exception")).when(table).putItem(any(MessageData.class));
        
        // Act & Assert
        assertThrows(RuntimeException.class, () -> messageRepository.save(messageData));
        verify(dynamoDbErrorCounter, times(1)).increment();
    }
    
    @Test
    void testDeleteIncrementsDynamoDbDeleteCounter() {
        // Arrange
        // Não precisamos mockar o comportamento do método deleteItem
        // pois estamos apenas verificando as chamadas aos contadores
        
        // Act
        messageRepository.delete(customerId, recordId);
        
        // Assert
        verify(dynamoDbDeleteCounter, times(1)).increment();
        verify(dynamoDbErrorCounter, never()).increment();
    }
    
    @Test
    void testDeleteHandlesExceptionAndIncrementsErrorCounter() {
        // Arrange
        doThrow(new RuntimeException("Test exception")).when(table).deleteItem(any(Key.class));
        
        // Act & Assert
        assertThrows(RuntimeException.class, () -> messageRepository.delete(customerId, recordId));
        verify(dynamoDbErrorCounter, times(1)).increment();
    }
    
    @Test
    void testFindByIdReturnsMessageData() {
        // Arrange - configuramos o mock para retornar nosso objeto de teste
        doReturn(messageData).when(table).getItem(any(Key.class));
        
        // Act
        MessageData result = messageRepository.findById(customerId, recordId);
        
        // Assert
        assertNotNull(result);
        assertEquals(customerId, result.getCustomerId());
        assertEquals(recordId, result.getRecordId());
        verify(dynamoDbErrorCounter, never()).increment();
    }
    
    @Test
    void testFindByIdHandlesExceptionAndIncrementsErrorCounter() {
        // Arrange - simulamos uma exceção ao acessar a tabela
        doThrow(new RuntimeException("Test exception")).when(table).getItem(any(Key.class));
        
        // Act & Assert
        assertThrows(RuntimeException.class, () -> messageRepository.findById(customerId, recordId));
        verify(dynamoDbErrorCounter, times(1)).increment();
    }
}
