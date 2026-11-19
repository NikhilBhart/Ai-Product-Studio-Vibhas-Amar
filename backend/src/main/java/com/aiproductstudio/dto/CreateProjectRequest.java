package com.aiproductstudio.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateProjectRequest(
        @NotBlank @Size(min = 5, max = 8000) String idea,
        @Size(max = 180) String productNameHint
) {}
