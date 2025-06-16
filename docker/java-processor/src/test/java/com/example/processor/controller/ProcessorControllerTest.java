package com.example.processor.controller;

import com.example.processor.model.ProcessRequest;
import com.example.processor.model.ProcessResponse;
import com.example.processor.service.MessageProcessorService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.time.Instant;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class ProcessorControllerTest {

    @Mock
    private MessageProcessorService messageProcessorService;

    @InjectMocks
    private ProcessorController processorController;

    private ProcessRequest request;
    private ProcessResponse successResponse;

    @BeforeEach
    void setUp() {
        // Preparar dados de teste
        String messageId = UUID.randomUUID().toString();
        String timestamp = Instant.now().toString();

        // Criar request
        request = new ProcessRequest();
        request.setId(messageId);
        request.setTimestamp(timestamp);
        request.setOperation("INSERT");
        request.setName("Test User");
        request.setEmail("test@example.com");

        // Criar resposta de sucesso
        successResponse = new ProcessResponse();
        successResponse.setStatus("SUCCESS");
        successResponse.setMessage("Message processed successfully");
        // Nota: ProcessResponse não tem método setTimestamp
    }

    @Test
    void processMessageSynchronously() {
        // Arrange
        when(messageProcessorService.processMessage(any(ProcessRequest.class))).thenReturn(successResponse);

        // Act
        ResponseEntity<ProcessResponse> response = processorController.processMessage(request);

        // Assert
        assertNotNull(response);
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(successResponse, response.getBody());
    }

    @Test
    void processMessageAsynchronously() {
        // Arrange
        when(messageProcessorService.processMessageAsync(any(ProcessRequest.class)))
                .thenReturn(CompletableFuture.completedFuture(successResponse));

        // Act
        CompletableFuture<ResponseEntity<ProcessResponse>> futureResponse = processorController.processMessageAsync(request);
        
        // Assert
        assertNotNull(futureResponse);
        ResponseEntity<ProcessResponse> response = futureResponse.join();
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(successResponse, response.getBody());
    }

    @Test
    void healthCheck() {
        // Act
        ResponseEntity<String> response = processorController.healthCheck();

        // Assert
        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("Service is healthy", response.getBody());
    }
}
