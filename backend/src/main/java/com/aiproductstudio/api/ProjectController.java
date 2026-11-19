package com.aiproductstudio.api;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.aiproductstudio.dto.CreateProjectRequest;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/projects")
public class ProjectController {
    private static final UUID DEV_TENANT_ID = UUID.fromString("00000000-0000-0000-0000-000000000001");
    private static final UUID DEV_OWNER_ID = UUID.fromString("00000000-0000-0000-0000-000000000002");

    private final JdbcTemplate jdbc;
    private final RestClient agentClient;
    private final ObjectMapper mapper;

    public ProjectController(JdbcTemplate jdbc, RestClient agentRestClient, ObjectMapper mapper) {
        this.jdbc = jdbc;
        this.agentClient = agentRestClient;
        this.mapper = mapper;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Map<String, Object> create(@Valid @RequestBody CreateProjectRequest request) {
        UUID projectId = UUID.randomUUID();
        String projectName = request.productNameHint() == null || request.productNameHint().isBlank()
                ? "New product idea" : request.productNameHint().trim();
        jdbc.update("""
                INSERT INTO projects (id, tenant_id, owner_user_id, name, idea, status)
                VALUES (?, ?, ?, ?, ?, 'DISCOVERY')
                """, projectId, DEV_TENANT_ID, DEV_OWNER_ID, projectName, request.idea().trim());

        UUID runId = UUID.randomUUID();
        jdbc.update("""
                INSERT INTO agent_runs (id, project_id, graph_name, status, current_node, input, started_at)
                VALUES (?, ?, 'product_manager_discovery', 'RUNNING', 'generate_product_brief', ?::jsonb, now())
                """, runId, projectId, toJson(Map.of("idea", request.idea(), "productNameHint", request.productNameHint() == null ? "" : request.productNameHint())));

        try {
            JsonNode agentResponse = agentClient.post()
                    .uri("/v1/discovery/run")
                    .body(Map.of("project_id", projectId.toString(), "idea", request.idea(), "product_name_hint", request.productNameHint() == null ? "" : request.productNameHint()))
                    .retrieve()
                    .body(JsonNode.class);
            if (agentResponse == null || !agentResponse.has("product_brief")) {
                throw new IllegalStateException("Agent service returned an empty product brief");
            }
            JsonNode brief = agentResponse.get("product_brief");
            String briefJson = brief.toString();
            jdbc.update("UPDATE projects SET name = ?, canonical_spec = ?::jsonb, status = 'PRD_READY', updated_at = now() WHERE id = ?",
                    brief.path("product_name").asText(projectName), briefJson, projectId);
            jdbc.update("""
                    UPDATE agent_runs SET status = 'COMPLETED', current_node = 'validate_product_brief',
                    output = ?::jsonb, completed_at = now() WHERE id = ?
                    """, agentResponse.toString(), runId);
            jdbc.update("""
                    INSERT INTO artifacts (project_id, run_id, artifact_type, title, content)
                    VALUES (?, ?, 'PRODUCT_BRIEF', ?, ?::jsonb)
                    """, projectId, runId, brief.path("product_name").asText("Product brief"), briefJson);
            return Map.of(
                    "id", projectId.toString(),
                    "name", brief.path("product_name").asText(projectName),
                    "status", "PRD_READY",
                    "agentRunId", runId.toString(),
                    "discovery", agentResponse
            );
        } catch (Exception exception) {
            jdbc.update("UPDATE projects SET status = 'BLOCKED', updated_at = now() WHERE id = ?", projectId);
            jdbc.update("UPDATE agent_runs SET status = 'FAILED', error = ?::jsonb, completed_at = now() WHERE id = ?",
                    toJson(Map.of("message", safeMessage(exception))), runId);
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                    "Project was created but Product Manager discovery failed: " + safeMessage(exception), exception);
        }
    }

    @GetMapping
    public List<Map<String, Object>> list() {
        return jdbc.query("""
                SELECT id, name, idea, status, created_at, updated_at
                FROM projects WHERE tenant_id = ? ORDER BY created_at DESC LIMIT 50
                """, this::mapProject, DEV_TENANT_ID);
    }

    @GetMapping("/{id}")
    public Map<String, Object> get(@PathVariable UUID id) {
        List<Map<String, Object>> rows = jdbc.query("""
                SELECT id, name, idea, status, canonical_spec, created_at, updated_at
                FROM projects WHERE id = ? AND tenant_id = ?
                """, (rs, rowNum) -> {
            Map<String, Object> result = new java.util.LinkedHashMap<>();
            result.put("id", rs.getObject("id").toString());
            result.put("name", rs.getString("name"));
            result.put("idea", rs.getString("idea"));
            result.put("status", rs.getString("status"));
            String spec = rs.getString("canonical_spec");
            try {
                result.put("productBrief", spec == null ? null : mapper.readTree(spec));
            } catch (JsonProcessingException exception) {
                throw new SQLException("Stored product specification is not valid JSON", exception);
            }
            result.put("createdAt", rs.getObject("created_at", OffsetDateTime.class));
            result.put("updatedAt", rs.getObject("updated_at", OffsetDateTime.class));
            return result;
        }, id, DEV_TENANT_ID);
        if (rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Project not found");
        return rows.getFirst();
    }

    private Map<String, Object> mapProject(ResultSet rs, int rowNum) throws SQLException {
        return Map.of(
                "id", rs.getObject("id").toString(),
                "name", rs.getString("name"),
                "idea", rs.getString("idea"),
                "status", rs.getString("status"),
                "createdAt", rs.getObject("created_at", OffsetDateTime.class),
                "updatedAt", rs.getObject("updated_at", OffsetDateTime.class)
        );
    }

    private String toJson(Object value) {
        try { return mapper.writeValueAsString(value); }
        catch (JsonProcessingException exception) { throw new IllegalStateException("Could not serialize JSON", exception); }
    }

    private String safeMessage(Exception exception) {
        String message = exception.getMessage();
        return message == null ? exception.getClass().getSimpleName() : message.substring(0, Math.min(message.length(), 700));
    }
}
