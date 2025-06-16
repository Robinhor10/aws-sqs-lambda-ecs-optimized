package com.example.processor.service;

import com.example.processor.model.MessageData;
import com.example.processor.model.ProcessRequest;
import com.example.processor.model.ProcessResponse;
import com.example.processor.repository.MessageRepository;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.concurrent.CompletableFuture;

@Service
@Slf4j
public class MessageProcessorService {

    private final MessageRepository messageRepository;
    private final Counter sqsMessageReceivedCounter;
    private final Counter sqsMessageErrorCounter;
    private final Timer processMessageTimer;

    public MessageProcessorService(MessageRepository messageRepository, 
                                 Counter sqsMessageReceivedCounter,
                                 Counter sqsMessageErrorCounter,
                                 MeterRegistry meterRegistry) {
        this.messageRepository = messageRepository;
        this.sqsMessageReceivedCounter = sqsMessageReceivedCounter;
        this.sqsMessageErrorCounter = sqsMessageErrorCounter;
        this.processMessageTimer = Timer.builder("process_message_seconds")
                .description("Time taken to process a message")
                .register(meterRegistry);
    }

    public ProcessResponse processMessage(ProcessRequest request) {
        log.info("Processing message with ID: {}, operation: {}", request.getId(), request.getOperation());
        
        // Incrementar contador de mensagens recebidas
        sqsMessageReceivedCounter.increment();
        
        return processMessageTimer.record(() -> {
            try {
                // Processar com base na operação
                ProcessResponse response;
                if ("INSERT".equalsIgnoreCase(request.getOperation())) {
                    response = handleInsert(request);
                } else if ("DELETE".equalsIgnoreCase(request.getOperation())) {
                    response = handleDelete(request);
                } else {
                    log.warn("Unknown operation: {}", request.getOperation());
                    sqsMessageErrorCounter.increment();
                    response = ProcessResponse.builder()
                            .id(request.getId())
                            .operation(request.getOperation())
                            .status("ERROR")
                            .processedAt(Instant.now())
                            .message("Unknown operation")
                            .build();
                }
                return response;
            } catch (Exception e) {
                log.error("Error processing message: {}", e.getMessage(), e);
                sqsMessageErrorCounter.increment();
                return ProcessResponse.builder()
                        .id(request.getId())
                        .operation(request.getOperation())
                        .status("ERROR")
                        .processedAt(Instant.now())
                        .message("Error: " + e.getMessage())
                        .build();
            }
        });
    }

    public CompletableFuture<ProcessResponse> processMessageAsync(ProcessRequest request) {
        return CompletableFuture.supplyAsync(() -> processMessage(request));
    }

    private ProcessResponse handleInsert(ProcessRequest request) {
        log.debug("Handling INSERT operation for ID: {}", request.getId());
        
        // Converter request para MessageData
        MessageData messageData = MessageData.builder()
                .customerId(request.getId())
                .recordId(request.getTimestamp())
                .operation(request.getOperation())
                .name(request.getName())
                .email(request.getEmail())
                .address(request.getAddress())
                .phone(request.getPhone())
                .processedAt(Instant.now())
                .build();
        
        try {
            // Salvar no DynamoDB
            MessageData savedData = messageRepository.save(messageData);
            
            log.info("Successfully inserted data with ID: {}", request.getId());
            
            return ProcessResponse.builder()
                    .id(savedData.getCustomerId())
                    .operation(savedData.getOperation())
                    .status("SUCCESS")
                    .processedAt(savedData.getProcessedAt())
                    .message("Data inserted successfully")
                    .build();
        } catch (Exception e) {
            sqsMessageErrorCounter.increment();
            throw e;
        }
    }

    private ProcessResponse handleDelete(ProcessRequest request) {
        log.debug("Handling DELETE operation for ID: {}", request.getId());
        
        try {
            // Verificar se o item existe
            MessageData existingData = messageRepository.findById(request.getId(), request.getTimestamp());
            
            if (existingData == null) {
                log.warn("Item not found for deletion. ID: {}, Timestamp: {}", request.getId(), request.getTimestamp());
                return ProcessResponse.builder()
                        .id(request.getId())
                        .operation(request.getOperation())
                        .status("WARNING")
                        .processedAt(Instant.now())
                        .message("Item not found for deletion")
                        .build();
            }
            
            // Excluir do DynamoDB
            messageRepository.delete(request.getId(), request.getTimestamp());
            
            log.info("Successfully deleted data with ID: {}", request.getId());
            
            return ProcessResponse.builder()
                    .id(request.getId())
                    .operation(request.getOperation())
                    .status("SUCCESS")
                    .processedAt(Instant.now())
                    .message("Data deleted successfully")
                    .build();
        } catch (Exception e) {
            log.error("Error deleting data: {}", e.getMessage(), e);
            sqsMessageErrorCounter.increment();
            return ProcessResponse.builder()
                    .id(request.getId())
                    .operation(request.getOperation())
                    .status("ERROR")
                    .processedAt(Instant.now())
                    .message("Error deleting data: " + e.getMessage())
                    .build();
        }
    }
}
