package com.example.processor.controller;

import com.example.processor.model.ProcessRequest;
import com.example.processor.model.ProcessResponse;
import com.example.processor.service.MessageProcessorService;
import io.micrometer.core.annotation.Timed;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.concurrent.CompletableFuture;

@RestController
@RequestMapping("/process")
@Slf4j
public class ProcessorController {

    private final MessageProcessorService processorService;

    public ProcessorController(MessageProcessorService processorService) {
        this.processorService = processorService;
    }

    @PostMapping
    @Timed(value = "process.message", description = "Time taken to process a message")
    public ResponseEntity<ProcessResponse> processMessage(@RequestBody ProcessRequest request) {
        log.info("Received request to process message: {}", request.getId());
        ProcessResponse response = processorService.processMessage(request);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/async")
    public CompletableFuture<ResponseEntity<ProcessResponse>> processMessageAsync(@RequestBody ProcessRequest request) {
        log.info("Received async request to process message: {}", request.getId());
        return processorService.processMessageAsync(request)
                .thenApply(ResponseEntity::ok);
    }

    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("Service is healthy");
    }
}
