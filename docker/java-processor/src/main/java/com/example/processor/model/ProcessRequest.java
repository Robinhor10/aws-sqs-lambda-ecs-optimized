package com.example.processor.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProcessRequest {
    private String id;
    private String timestamp;
    private String operation;
    private String name;
    private String email;
    private String address;
    private String phone;
}
